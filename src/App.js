import React, { useEffect, useState } from "react";
import { AppHeader } from "./components/AppHeader";
import "./App.css";
import { TextInput } from "./components/TextInput";
import { Search } from "./components/Search";
import { WordCloud } from "./components/WordCloud";


function App() {
  const [query, setQuery] = useState(""); // Track the search input
  const [articles, setArticles] = useState([]); // Store articles

  const [tags, setTags] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function getTags() {
      try {
        const response = await fetch("http://127.0.0.1:5000/count_tags");
        console.log("Response status:", response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error("API Error:", errorText);
          setError("Failed to fetch tags: " + errorText);
          return;
        }

        const data = await response.json();
        console.log(data);
        if (data && typeof data === 'object') {
          setTags(data); // Update state with the fetched tags
        }

      } catch (error) {
        console.error("Error collecting tags:", error);
        setError("Network error: " + error.message);
      }
    }

    getTags();
  }, []); // Dependenc

  async function searchFeeds() {
    try {
      const response = await fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`);
        // Debugging the response
      console.log("Response status:", response.status);

      if (!response.ok) {
        console.error("API Error:", await response.text());
        return;
      }

      const data = await response.json();
      console.log("Fetched data:", data); // Logs the data from the API
      setArticles(data); // Update state with articles
    } catch (error) {
      console.error("Error fetching feeds:", error);
    }
  }


  const [selectedTag, setSelectedTag] = useState(null);

  const handleTagClick = (tagText) => {
    console.log("Selected tag:", tagText);
    setQuery(tagText);
  };
  
  return (
    <div id="rss-aggregator">
      <AppHeader />
      <div className="word-cloud-container">
        <div className="word-cloud">
          {tags === undefined ? (
            <div>Loading Word Cloud...</div> // Show loading state when tags are not yet available
          ) : (
            <WordCloud tags={tags} onTagClick={handleTagClick} /> // Render WordCloud when tags are available
          )}
        </div>
      </div>
      <div className="search-bar">
        <TextInput query={query} setQuery={setQuery} />
          <button className="search-button" onClick={searchFeeds}>
            Search
          </button>
      </div>
      <Search articles={articles} />
      <div>
        <pre>{JSON.stringify(articles, null, 2)}</pre>
      </div>
    </div>
  );
}

export default App;
