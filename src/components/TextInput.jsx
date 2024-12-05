
export function TextInput({query, setQuery}){
    return(<div id="text-input">
        <input
            id="text-search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)} // Update query on input
            placeholder="Search tags (e.g., art,history -modern)"
          />
      </div>);}