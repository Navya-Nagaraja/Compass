export default function SourcePanel({ sources }) {
  return (
    <aside className="source-panel">
      <div className="section-label">retrieved context</div>
      {(!sources || sources.length === 0) && (
        <div className="empty-state" style={{ margin: "12px 0 0" }}>
          sources for your last question will show up here
        </div>
      )}
      {sources?.map((source, i) => (
        <div className="source-card" key={`${source.document}-${source.chunk_index}-${i}`}>
          <div className="source-doc">
            <span>{source.document}</span>
            <span>#{source.chunk_index}</span>
          </div>
          <div className="score-bar-track">
            <div className="score-bar-fill" style={{ width: `${Math.max(0, Math.min(1, source.score)) * 100}%` }} />
          </div>
          <div className="source-text">{source.text}</div>
        </div>
      ))}
    </aside>
  );
}
