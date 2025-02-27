import { Card } from "./Card";

export function Search({ articles, loading }) {
  return (
    <div className="search-output">
      {articles.map((article, index) => (
        <Card key={index} article={article} loading={loading} />
      ))}
    </div>
  );
}
