import { Card } from "./Card";
export function Search({articles}){
    return(
      <div className="search-output">
        {articles.map((article, index) => (
          <div key={index}>
            <Card article={article}/>
            
          </div>
        ))}
      </div>);
}