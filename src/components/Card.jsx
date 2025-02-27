export function Card({ article, loading }) {
  return (
    <div className="card">
      {loading || !article.link ? (
        <div className="card-placeholder">
          <div className="placeholder-thumbnail"></div>
          <div className="placeholder-title"></div>
        </div>
      ) : (
        <a href={article.link} target="_blank" rel="noopener noreferrer" className="card-link">
          {article.thumbnail && <img src={article.thumbnail} alt="Article Thumbnail" className="thumbnail" />}
          <h3>{article.title}</h3>
        </a>
      )}
      {!loading && article.published && <p>{new Date(article.published).toLocaleString()}</p>}
    </div>
  );
}
