import React, { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState(""); // Track the search input
  const [articles, setArticles] = useState([]); // Store articles

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
  

  return (
    <div id="rss-aggregator">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)} // Update query on input
        placeholder="Search tags (e.g., art,history -modern)"
      />
      <button onClick={searchFeeds}>Search</button>
      <div>
        {articles.map((article, index) => (
          <div key={index}>
            <a href={article.link} target="_blank" rel="noopener noreferrer">
              {article.title}
            </a>
            <p>{new Date(article.published).toLocaleString()}</p>
          </div>
        ))}
      </div>
      <div>
        <pre>{JSON.stringify(articles, null, 2)}</pre>
      </div>
    </div>
  );
}

export default App;
