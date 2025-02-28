export const SyntaxExplanation = () => {
    return(
        <div className="syntax-container">
        <h1>How to use:</h1>
        <p>Search supports the following operators:</p>
        <table style={{ border: '1px solid black', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid black', padding: '8px' }}>Operator</th>
              <th style={{ border: '1px solid black', padding: '8px' }}>Symbol</th>
              <th style={{ border: '1px solid black', padding: '8px' }}>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ border: '1px solid black', padding: '8px' }}>AND</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>,</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>Includes results containing both terms.</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black', padding: '8px' }}>OR</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>|</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>Includes results containing either term.</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black', padding: '8px' }}>NOT</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>-</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>Excludes results containing the term.</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black', padding: '8px' }}>Grouping</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>()</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>Groups terms for complex queries.</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black', padding: '8px' }}>Phrase</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>""</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>Matches an exact phrase.</td>
            </tr>
          </tbody>
        </table>
        <h2>Examples</h2>
        <h3>Basic Queries:</h3>
        <p>climate,change → Matches entries with both "climate" AND "change".</p>
        <p>protest | activism → Matches entries with either "protest" OR "activism".</p>
        <p>-violence → Excludes entries containing "violence".</p>
        <h3>Complex Queries:</h3>
        <p>(environment | sustainability),policy → Matches entries containing either "environment" OR "sustainability" AND "policy".</p>
        <p>"climate crisis" | (renewable,energy) → Matches entries with the exact phrase "climate crisis" OR both "renewable" AND "energy".</p>
        <p>-corporate,(greenwashing|deception) → Excludes entries with "corporate" while requiring "greenwashing" OR "deception".</p>
      </div>
    )
};