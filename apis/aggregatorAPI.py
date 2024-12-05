from flask import Flask, request, jsonify
from datetime import datetime
import feedparser
import requests
from xml.etree.ElementTree import Element, SubElement, tostring
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

feed_urls = [
    "https://archive.org/services/collection-rss.php?collection=resistancearchive",
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
]

FLICKR_API_KEY = "715d330285540544f7323bc79dd188c2"


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


def fetch_feeds(urls):
    """Fetch and process entries from multiple feeds, avoiding redundant thumbnails."""
    all_entries = []
    for url in set(urls):  # Deduplicate feed URLs
        feed = feedparser.parse(url)
        for entry in feed.entries:
            print("Processing entry:", entry)
            
            # Initialize entry data
            processed_entry = {
                "title": entry.title,
                "link": entry.link,
                "published": datetime(*entry.published_parsed[:6]),
                "tags": [tag.term for tag in getattr(entry, "tags", [])],
                "thumbnail": None,
            }

            # Add thumbnail for archive.org
            if "archive.org/details" in entry["link"] and not processed_entry["thumbnail"]:
                item_id = entry["link"].split("/")[-1]
                processed_entry["thumbnail"] = f"https://archive.org/services/img/{item_id}"
            # Add thumbnail for Flickr
            elif "flickr.com" in entry["link"] and not processed_entry["thumbnail"]:
                photo_id = extract_photo_id(entry["link"])
                if photo_id:
                    processed_entry["thumbnail"] = get_flickr_thumbnail(photo_id)
            
            all_entries.append(processed_entry)
    
    return sorted(all_entries, key=lambda x: x["published"], reverse=True)



def deduplicate(entries):
    seen_links = set()
    unique_entries = []
    for entry in entries:
        if entry["link"] not in seen_links:
            seen_links.add(entry["link"])
            unique_entries.append(entry)
    return unique_entries

def boolean_search(entries, query):
    """Perform boolean search with query, including thumbnail generation."""
    print("Query received:", query)
    terms = query.split()
    include = {term for term in terms if not term.startswith("-")}
    exclude = {term[1:] for term in terms if term.startswith("-")}
    
    results = []
    for entry in entries:
        tags = set(entry["tags"])
        if include <= tags and exclude.isdisjoint(tags):
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

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    entries = fetch_feeds(feed_urls)
    unique_entries = deduplicate(entries)
    results = boolean_search(unique_entries, query)
    return jsonify(results)

@app.route("/atom-feed", methods=["GET"])
def atom_feed():
    entries = fetch_feeds(feed_urls)
    unique_entries = deduplicate(entries)
    feed = Element('feed', xmlns="http://www.w3.org/2005/Atom")
    SubElement(feed, 'title').text = "Aggregated Feed"
    for entry in unique_entries:
        entry_element = SubElement(feed, 'entry')
        SubElement(entry_element, 'title').text = entry["title"]
        SubElement(entry_element, 'link', href=entry["link"])
        SubElement(entry_element, 'published').text = entry["published"].isoformat()
    atom_xml = tostring(feed, encoding="utf-8").decode("utf-8")
    return atom_xml, 200, {"Content-Type": "application/atom+xml"}

if __name__ == "__main__":
    app.run(debug=True)
