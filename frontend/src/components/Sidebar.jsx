import { useState } from "react";
import { ingestDocument } from "../api";

export default function Sidebar({ health, onIngested }) {
  const [docName, setDocName] = useState("");
  const [docText, setDocText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  const isOnline = health?.status === "ok";

  async function handleIngest(e) {
    e.preventDefault();
    if (!docName.trim() || !docText.trim()) return;
    setSubmitting(true);
    setMessage(null);
    try {
      const result = await ingestDocument(docName.trim(), docText.trim());
      setMessage(`indexed ${result.chunks_indexed} chunk(s)`);
      setDocName("");
      setDocText("");
      onIngested?.();
    } catch (err) {
      setMessage(`error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">&gt;_</span>
        <span className="brand-name">compass</span>
      </div>

      <div className="status-block">
        <div className="section-label">system</div>
        <div className="status-row">
          <span>
            <span className={`status-dot ${isOnline ? "online" : "offline"}`} />
            api
          </span>
          <span>{isOnline ? "online" : "unreachable"}</span>
        </div>
        <div className="status-row">
          <span>provider</span>
          <span>{health?.llm_provider ?? "—"}</span>
        </div>
        <div className="status-row">
          <span>documents</span>
          <span>{health?.documents_indexed ?? 0}</span>
        </div>
        <div className="status-row">
          <span>env</span>
          <span>{health?.environment ?? "—"}</span>
        </div>
      </div>

      <div>
        <div className="section-label">ingest a doc</div>
        <form className="ingest-form" onSubmit={handleIngest} style={{ marginTop: 10 }}>
          <input
            placeholder="document name, e.g. deploy-runbook.md"
            value={docName}
            onChange={(e) => setDocName(e.target.value)}
          />
          <textarea
            rows={6}
            placeholder="paste doc / runbook / API spec text..."
            value={docText}
            onChange={(e) => setDocText(e.target.value)}
          />
          <button type="submit" disabled={submitting}>
            {submitting ? "indexing..." : "index document"}
          </button>
        </form>
        {message && <div className="status-row" style={{ marginTop: 8 }}>{message}</div>}
      </div>
    </aside>
  );
}
