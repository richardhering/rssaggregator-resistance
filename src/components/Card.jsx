export function Card({ article }) {
    return (
      <div className="card">
        <a href={article.link} target="_blank" rel="noopener noreferrer" className="card-link">
          {article.thumbnail && (
            <img
              src={article.thumbnail}
              alt="Article Thumbnail"
              className="thumbnail"
            />
          )}
          <h3>{article.title}</h3>
        </a>
        <p>{new Date(article.published).toLocaleString()}</p>
      </div>
    );
  }
  