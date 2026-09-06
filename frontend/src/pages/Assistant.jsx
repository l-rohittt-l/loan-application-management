// The assistant. One chat box for the whole product.
//
// This screen talks to POST /api/v1/chat and nothing else, and it will not need
// rewriting as the later phases land. Today that address answers policy
// questions from the user manual. In Phase 3 the same address gains the ability
// to read live application data, in Phase 4 its tools move behind MCP, and in
// Phase 5 it can run a full multi-agent review. The screen stays as it is; the
// brain behind the door gets smarter.
//
// Two deliberate choices worth explaining in a walkthrough:
//
//   * Every answer shows the manual extracts it came from. An assistant that
//     cites its source can be checked; one that does not has to be trusted.
//     For a bank that difference matters.
//
//   * The conversation lives in this component's memory only. It is never put
//     in localStorage, because customer questions are customer data and
//     Rule 13 keeps that off the browser's disk.

import { useEffect, useRef, useState } from "react";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import Button from "../components/ui/Button";
import Icon from "../components/ui/Icon";

// What each brain is called on screen, so the routing is visible rather than magic.
const MODES = {
  rag: { text: "Answered from the user manual", icon: "file" },
  agent: { text: "Read live application data", icon: "activity" },
  review: { text: "Multi-agent review", icon: "shield" },
  empty: { text: "", icon: "info" },
};

const SUGGESTIONS = [
  "What documents are required for a home loan?",
  "What is the minimum CIBIL score for a personal loan?",
  "How long does a personal loan take to approve?",
  "What happens if my application is rejected?",
];

function Sources({ sources }) {
  const [open, setOpen] = useState(false);
  if (!sources?.length) return null;

  return (
    <div className="sources">
      <button type="button" className="sources-toggle" onClick={() => setOpen((v) => !v)}>
        <Icon name={open ? "chevronDown" : "chevronLeft"} size={13} />
        {open ? "Hide" : "Show"} the {sources.length} manual extract
        {sources.length === 1 ? "" : "s"} this came from
      </button>
      {open && (
        <ol className="sources-list">
          {sources.map((s, i) => (
            <li key={s.chunk_id || i}>
              <span className="mono">{s.chunk_id}</span>
              <p>{s.excerpt}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default function Assistant() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  // Keep the newest message in view as the conversation grows.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  async function send(text) {
    const question = (text ?? draft).trim();
    if (!question || busy) return;

    setMessages((m) => [...m, { who: "you", text: question }]);
    setDraft("");
    setBusy(true);
    setError("");

    try {
      const res = await api.post("/chat", { message: question });
      setMessages((m) => [...m, {
        who: "assistant",
        text: res.data.answer,
        mode: res.data.mode,
        sources: res.data.sources,
        ms: res.data.duration_ms,
      }]);
    } catch (err) {
      setError(errorMessage(err));
      // Put the question back so nothing the person typed is lost.
      setDraft(question);
      setMessages((m) => m.slice(0, -1));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Assistant</h1>
          <p className="sub">
            Ask about loan policy, eligibility, documents or fees. Every answer
            comes from the bank's user manual, and shows you where it came from.
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" icon="close" onClick={() => setMessages([])}>
            Clear
          </Button>
        )}
      </div>

      <ErrorBanner message={error} onClose={() => setError("")} />

      <div className="chat">
        <div className="chat-log">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <div className="empty-icon"><Icon name="shield" size={24} /></div>
              <p className="empty-title">
                Hello{user?.name ? `, ${user.name.split(" ")[0]}` : ""}. What would you like to know?
              </p>
              <p className="empty-text">
                I answer only from the bank's user manual. If something is not in
                there, I will say so rather than guess.
              </p>
              <div className="chips" style={{ justifyContent: "center", marginTop: "1.1rem" }}>
                {SUGGESTIONS.map((s) => (
                  <button key={s} type="button" className="chip" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`bubble bubble-${m.who}`}>
              <div className="bubble-text">{m.text}</div>
              {m.who === "assistant" && (
                <>
                  <Sources sources={m.sources} />
                  <div className="bubble-meta">
                    <Icon name={MODES[m.mode]?.icon || "info"} size={12} />
                    <span>{MODES[m.mode]?.text || m.mode}</span>
                    {m.ms != null && <span>· {(m.ms / 1000).toFixed(1)}s</span>}
                  </div>
                </>
              )}
            </div>
          ))}

          {busy && (
            <div className="bubble bubble-assistant">
              <div className="typing" aria-label="Thinking">
                <span /><span /><span />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form
          className="chat-input"
          onSubmit={(e) => { e.preventDefault(); send(); }}
        >
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Ask about eligibility, documents, fees, timelines…"
            aria-label="Your question"
            disabled={busy}
          />
          <Button type="submit" variant="primary" loading={busy} disabled={!draft.trim()}>
            Send
          </Button>
        </form>
      </div>
    </>
  );
}
