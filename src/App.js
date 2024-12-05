import React, { useState } from "react";
import { AppHeader } from "./components/AppHeader";
import "./App.css";
import { TextInput } from "./components/TextInput";
import { Search } from "./components/Search";


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
    <AppHeader/>
      <div className="search-bar">
        <TextInput 
          query = {query}
          setQuery = {setQuery}
        />
        <button className="search-button" onClick={searchFeeds}>Search</button>
      </div>
      

      <Search articles={articles}/>
      <div>
        <pre>{JSON.stringify(articles, null, 2)}</pre>
      </div>
    </div>
  );
}

export default App;
