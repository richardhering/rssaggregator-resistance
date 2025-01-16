from flask import Flask, request, jsonify
from collections import defaultdict
from datetime import datetime
import feedparser
import aiohttp
import asyncio
from xml.etree.ElementTree import Element, SubElement, tostring
from flask_cors import CORS
import re
import hashlib
from cachetools import TTLCache
import requests  # Missing import

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

feed_urls = list(set([
    "https://archive.org/services/collection-rss.php?collection=resistancearchive",
    "https://archive.org/services/collection-rss.php?collection=ingabystramstrikingart",
    "https://archive.org/services/collection-rss.php?query=subject:Chiara_Contrino",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX3iLGuSVVeri7ZEfud_j-su",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX0PzadF1L72XBw8mLpejzrY",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX21XJ7pjAWCaJKThHXOWPjb",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX375LTWGoOIHgDty4Cs6agg",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX3Bi3orWOkZRiPa7m7wKbRL",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX3lpMK8PoZTke2DsYbqCJMZ",
    "https://www.youtube.com/feeds/videos.xml?playlist_id=PLmEoLllcfuX0yx5BL-sFjGu3bZIEKmnNq",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157623673144706&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157692538977302&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157600354803923&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157600356404760&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157600357938530&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157604489309701&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157604586597656&lang=en-us&format=atom",
    "https://www.flickr.com/services/feeds/photoset.gne?nsid=8933893@N08&set=72157604184970480&lang=en-us&format=atom"
]))

FLICKR_API_KEY = "715d330285540544f7323bc79dd188c2"
cache = TTLCache(maxsize=100, ttl=3600)  # Cache with 1-hour TTL

# Async functions
async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return url, await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None

async def fetch_feeds_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return {url: feedparser.parse(content) for url, content in responses if content}

@app.route("/count_tags", methods=["GET"])
def process_and_count_tags():
    """Process feed data and return a dictionary of tag counts."""
    # Fetch feed data asynchronously
    feed_data = asyncio.run(fetch_feeds_async(feed_urls)); # Replace with your actual feed URLs
    
    tag_count = defaultdict(int)
    
    # Process feed data
    for url, feed in feed_data.items():
        for entry in feed.get("entries", []):
            tags = [tag["term"] for tag in entry.get("tags", [])]
            for tag in tags:
                if not (tag.startswith("texts/") or tag.startswith("image/")):
                                tag_count[tag] += 1
    # Return the tag counts as a JSON response
    return jsonify(tag_count)
def process_entries(feed_data):
    entries = []
    for url, feed in feed_data.items():
        for entry in feed.entries:
            processed_entry = {
                "title": entry.title,
                "link": entry.link,
                "published": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
                "tags": [tag.term for tag in getattr(entry, "tags", [])],
                "thumbnail": None,
            }
            entries.append(processed_entry)
    return sorted(entries, key=lambda x: x["published"], reverse=True)

def deduplicate(entries):
    seen_links = set()
    unique_entries = []
    for entry in entries:
        if entry["link"] not in seen_links:
            seen_links.add(entry["link"])
            unique_entries.append(entry)
    return unique_entries

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    feed_data = asyncio.run(fetch_feeds_async(feed_urls))
    entries = process_entries(feed_data)
    unique_entries = deduplicate(entries)
    results = boolean_search(unique_entries, query)  
    return jsonify(results)

def extract_photo_id(flickr_url):
    """Extract photo ID from a Flickr URL."""
    match = re.search(r'flickr\.com/photos/[^/]+/(\d+)', flickr_url)
    return match.group(1) if match else None

def get_flickr_thumbnail(photo_id):
    """Fetch the thumbnail for a Flickr photo."""
    if not photo_id:  # Ensure valid photo ID
        return None

    try:
        api_url = f"https://www.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key={FLICKR_API_KEY}&photo_id={photo_id}&format=json&nojsoncallback=1"
        response = requests.get(api_url, timeout=5)  # Add timeout
        response.raise_for_status()  # Handle HTTP errors
        data = response.json()
        if data.get("stat") != "ok":
            return None
        
        # Look for the 'Small' size thumbnail
        sizes = data.get("sizes", {}).get("size", [])
        thumbnail = next((size for size in sizes if size["label"] == "Small"), None)
        return thumbnail["source"] if thumbnail else None
    except requests.RequestException as e:
        print("Error fetching Flickr thumbnail:", e)
        return None
def parse_query(query):
    """Parse the query into terms, handling AND, OR, NOT, and parentheses."""
    # Remove extra spaces around parentheses for easier handling
    query = re.sub(r'\s*\(\s*', '(', query)
    query = re.sub(r'\s*\)\s*', ')', query)
    
    # Split the query into terms while preserving multi-word tags enclosed in quotes
    tokens = re.findall(r'\"[^\"]+\"|\S+|\(|\)', query)

    def parse_tokens(tokens):
        """Recursive function to handle bracketing and boolean logic."""
        stack = []
        temp = []
        
        while tokens:
            token = tokens.pop(0)
            
            if token == '(':
                # Recursively parse the content inside parentheses
                temp.append(parse_tokens(tokens))
            elif token == ')':
                # Return when encountering a closing parenthesis
                stack.append(temp)
                return stack
            else:
                # Process regular terms
                temp.append(token)
        
        stack.append(temp)
        return stack

    return parse_tokens(tokens)

def evaluate_query(entry, parsed_query):
    """Evaluate the parsed query against an entry."""
    tags = set(entry["tags"])
    result = True
    
    for condition in parsed_query:
        if isinstance(condition, list):
            # Recursively evaluate nested conditions
            result &= evaluate_query(entry, condition)
        else:
            # Process the AND, OR, NOT logic for each condition
            include_and = {term.strip('"') for term in condition if "|" not in term and not term.startswith("-")}
            include_or = {subterm for term in condition if "|" in term for subterm in term.split("|")}
            exclude = {term[1:] for term in condition if term.startswith("-")}

            # AND condition
            and_condition = include_and <= tags
            
            # OR condition
            or_condition = not include_or or any(tag in tags for tag in include_or)

            # NOT condition
            not_condition = exclude.isdisjoint(tags)

            result &= and_condition and or_condition and not_condition

    return result

def boolean_search(entries, query):
    """Perform boolean search with AND, OR, NOT functionality, including thumbnail generation."""
    parsed_query = parse_query(query)  # Parse the query with bracketing support

    results = []

    for entry in entries:
        # Evaluate the parsed query against the entry's tags
        if evaluate_query(entry, parsed_query):
            # Generate thumbnail for archive.org
            if "archive.org/details" in entry["link"]:
                item_id = entry["link"].split("/")[-1]
                thumbnail_url = f"https://archive.org/services/img/{item_id}"
                entry["thumbnail"] = thumbnail_url

            # Generate thumbnail for Flickr
            elif "flickr.com" in entry["link"]:
                photo_id = extract_photo_id(entry["link"])
                if photo_id:
                    thumbnail_url = get_flickr_thumbnail(photo_id)
                    if thumbnail_url:
                        entry["thumbnail"] = thumbnail_url

            results.append(entry)

    print("Search results:", results)
    return results


@app.route("/atom-feed", methods=["GET"])
def atom_feed():
    feed_data = asyncio.run(fetch_feeds_async(feed_urls))
    entries = process_entries(feed_data)
    feed = Element("feed", xmlns="http://www.w3.org/2005/Atom")
    SubElement(feed, "title").text = "Aggregated Feed"
    for entry in entries:
        entry_element = SubElement(feed, "entry")
        SubElement(entry_element, "title").text = entry["title"]
        SubElement(entry_element, "link", href=entry["link"])
        SubElement(entry_element, "published").text = entry["published"].isoformat() if entry["published"] else ""
    atom_xml = tostring(feed, encoding="utf-8").decode("utf-8")
    return atom_xml, 200, {"Content-Type": "application/atom+xml"}

if __name__ == "__main__":
    app.run(debug=True)
