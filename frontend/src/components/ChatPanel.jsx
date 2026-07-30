import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api";

export default function ChatPanel({ onNewSources }) {
  const [entries, setEntries] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [entries]);

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || asking) return;

    setAsking(true);
    setQuestion("");
    const pendingId = crypto.randomUUID();
    setEntries((prev) => [...prev, { id: pendingId, question: trimmed, answer: null, latency: null }]);

    try {
      const result = await askQuestion(trimmed);
      setEntries((prev) =>
        prev.map((entry) =>
          entry.id === pendingId ? { ...entry, answer: result.answer, latency: result.latency_ms } : entry
        )
      );
      onNewSources?.(result.sources ?? []);
    } catch (err) {
      setEntries((prev) =>
        prev.map((entry) => (entry.id === pendingId ? { ...entry, answer: `error: ${err.message}`, latency: 0 } : entry))
      );
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="chat-panel">
      <div className="chat-log" ref={logRef}>
        {entries.length === 0 && (
          <div className="empty-state">
            index a doc in the sidebar, then ask a question below.
            <br />
            compass answers only from what you've indexed — nothing invented.
          </div>
        )}
        {entries.map((entry) => (
          <div className="log-entry" key={entry.id}>
            <div className="log-prompt">
              <span className="glyph">&gt;</span>
              <span>{entry.question}</span>
            </div>
            <div className="log-answer">{entry.answer ?? "thinking..."}</div>
            {entry.latency !== null && <div className="log-meta">{entry.latency.toFixed(0)}ms</div>}
          </div>
        ))}
      </div>

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <span className="glyph">&gt;</span>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="ask about an indexed doc or runbook..."
          disabled={asking}
        />
        <button type="submit" disabled={asking || !question.trim()}>
          {asking ? "asking..." : "ask"}
        </button>
      </form>
    </main>
  );
}
