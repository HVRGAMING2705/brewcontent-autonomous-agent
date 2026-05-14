"use client";

import "./globals.css";
import { useState, useRef, useEffect, useCallback } from "react";

const API = "http://127.0.0.1:8000";

// ── Types ──────────────────────────────────────────────────────────────────────

interface Source {
  title: string;
  url: string;
  score: number;
}

interface Message {
  id: string;
  role: "user" | "assistant" | "error";
  text: string;
  sources?: Source[];
  activity?: string[];
  loading?: boolean;
}

interface KBStatus {
  status: string;
  chunks_found: number;
  message: string;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function uid() {
  return Math.random().toString(36).slice(2);
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function ActivityLog({ items }: { items: string[] }) {
  const [open, setOpen] = useState(false);
  if (!items || items.length === 0) return null;
  return (
    <div style={{ marginTop: 10 }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          background: "none",
          border: "1px solid var(--border)",
          color: "var(--text-muted)",
          borderRadius: "var(--radius-sm)",
          padding: "3px 10px",
          fontSize: 12,
          display: "flex",
          alignItems: "center",
          gap: 5,
        }}
      >
        <span>{open ? "▾" : "▸"}</span>
        {open ? "Hide" : "Show"} agent activity ({items.length} steps)
      </button>
      {open && (
        <div
          style={{
            marginTop: 8,
            padding: "10px 14px",
            background: "var(--surface-2)",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border)",
            fontSize: 12.5,
            color: "var(--text-muted)",
            lineHeight: 1.8,
          }}
        >
          {items.map((item, i) => (
            <div key={i} style={{ padding: "1px 0" }}>
              {item}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SourceList({ sources }: { sources: Source[] }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ marginTop: 12 }}>
      <div
        style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}
      >
        Sources
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {sources.map((s, i) => (
          <a
            key={i}
            href={s.url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-block",
              padding: "3px 10px",
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              borderRadius: 99,
              fontSize: 12,
              color: "var(--accent-light)",
              textDecoration: "none",
              maxWidth: 280,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={`${s.title} — score ${s.score}`}
          >
            ↗ {s.title || s.url}
          </a>
        ))}
      </div>
    </div>
  );
}

function ChatBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  const isError = msg.role === "error";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        padding: "6px 0",
      }}
    >
      {!isUser && (
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "var(--accent)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
            flexShrink: 0,
            marginRight: 10,
            marginTop: 2,
          }}
        >
          🤖
        </div>
      )}
      <div style={{ maxWidth: "78%", minWidth: 60 }}>
        <div
          style={{
            background: isUser
              ? "var(--user-bubble)"
              : isError
              ? "#2d1515"
              : "var(--ai-bubble)",
            border: `1px solid ${
              isError ? "var(--error)" : "var(--border)"
            }`,
            borderRadius: isUser
              ? "var(--radius) var(--radius) 4px var(--radius)"
              : "var(--radius) var(--radius) var(--radius) 4px",
            padding: "12px 16px",
            color: isError ? "#fca5a5" : "var(--text)",
            fontSize: 14.5,
            lineHeight: 1.7,
            whiteSpace: "pre-wrap",
          }}
        >
          {msg.loading ? (
            <span style={{ color: "var(--text-muted)" }}>
              <LoadingDots />
            </span>
          ) : (
            msg.text
          )}
        </div>
        {!msg.loading && msg.activity && (
          <ActivityLog items={msg.activity} />
        )}
        {!msg.loading && msg.sources && (
          <SourceList sources={msg.sources} />
        )}
      </div>
      {isUser && (
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "#1e1b4b",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
            flexShrink: 0,
            marginLeft: 10,
            marginTop: 2,
          }}
        >
          👤
        </div>
      )}
    </div>
  );
}

function LoadingDots() {
  return (
    <span
      style={{
        display: "inline-flex",
        gap: 4,
        alignItems: "center",
        height: 20,
      }}
    >
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: "var(--accent)",
            display: "inline-block",
            animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
      <style>{`
        @keyframes pulse {
          0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </span>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uid(),
      role: "assistant",
      text:
        "Hi! I'm your BrewContent Knowledge Agent. Ask me anything about campaigns, scheduling, templates, audience, billing, or any other BrewContent feature. I'll search my knowledge base — or scrape BrewContent directly if I don't know the answer yet.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [kbStatus, setKbStatus] = useState<KBStatus | null>(null);
  const [kbLoading, setKbLoading] = useState(true);
  const [history, setHistory] = useState<{ id: string; text: string }[]>([]);

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Fetch KB status on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/kb/status`);
        const data = await res.json();
        setKbStatus(data);
      } catch {
        setKbStatus({ status: "error", chunks_found: 0, message: "Cannot reach backend." });
      } finally {
        setKbLoading(false);
      }
    })();
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsgId = uid();
    const asMsgId = uid();

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", text },
      { id: asMsgId, role: "assistant", text: "", loading: true },
    ]);
    setHistory((prev) => [...prev, { id: userMsgId, text: text.slice(0, 60) }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        let detail = `Server error ${res.status}`;
        try {
          const err = await res.json();
          detail = err.detail || detail;
        } catch {}
        throw new Error(detail);
      }

      const data = await res.json();

      setMessages((prev) =>
        prev.map((m) =>
          m.id === asMsgId
            ? {
                ...m,
                loading: false,
                text: data.answer,
                sources: data.sources,
                activity: data.activity,
              }
            : m
        )
      );
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "An unexpected error occurred.";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === asMsgId
            ? {
                ...m,
                loading: false,
                role: "error",
                text: `⚠️ ${msg}`,
              }
            : m
        )
      );
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, loading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize
    const ta = e.target;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        background: "var(--bg)",
        overflow: "hidden",
      }}
    >
      {/* ── Sidebar ── */}
      <aside
        style={{
          width: 260,
          flexShrink: 0,
          background: "var(--sidebar-bg)",
          borderRight: "1px solid var(--border)",
          display: "flex",
          flexDirection: "column",
          padding: "20px 16px",
          gap: 20,
          overflowY: "auto",
        }}
      >
        {/* Logo */}
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 4,
            }}
          >
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: "var(--radius-sm)",
                background: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 18,
              }}
            >
              🍺
            </div>
            <div>
              <div
                style={{ fontWeight: 700, fontSize: 15, color: "var(--text)" }}
              >
                BrewContent
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                Knowledge Agent
              </div>
            </div>
          </div>
        </div>

        {/* KB Status */}
        <div
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "12px 14px",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 8,
            }}
          >
            KB Status
          </div>
          {kbLoading ? (
            <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
              Checking…
            </div>
          ) : kbStatus ? (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginBottom: 4,
                }}
              >
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background:
                      kbStatus.status === "ok"
                        ? "var(--success)"
                        : "var(--error)",
                    display: "inline-block",
                  }}
                />
                <span style={{ fontSize: 13 }}>
                  {kbStatus.status === "ok" ? "Connected" : "Offline"}
                </span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                {kbStatus.chunks_found} chunks indexed
              </div>
            </>
          ) : null}
        </div>

        {/* Chat History */}
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 10,
            }}
          >
            Recent Questions
          </div>
          {history.length === 0 ? (
            <div style={{ fontSize: 12, color: "var(--text-muted)", padding: "4px 0" }}>
              No questions yet
            </div>
          ) : (
            <div
              style={{ display: "flex", flexDirection: "column", gap: 4 }}
            >
              {[...history].reverse().slice(0, 15).map((h) => (
                <div
                  key={h.id}
                  style={{
                    padding: "7px 10px",
                    borderRadius: "var(--radius-sm)",
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    fontSize: 12.5,
                    color: "var(--text-muted)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    cursor: "default",
                  }}
                  title={h.text}
                >
                  {h.text}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Hints */}
        <div
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "12px 14px",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 8,
            }}
          >
            Try asking…
          </div>
          {[
            "How do I create an Instagram campaign?",
            "How does scheduling work?",
            "What is the brand kit?",
            "How do I manage billing?",
          ].map((q, i) => (
            <button
              key={i}
              onClick={() => {
                setInput(q);
                textareaRef.current?.focus();
              }}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                background: "none",
                border: "none",
                color: "var(--accent-light)",
                fontSize: 12,
                padding: "3px 0",
                lineHeight: 1.5,
              }}
            >
              → {q}
            </button>
          ))}
        </div>
      </aside>

      {/* ── Main Chat ── */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <header
          style={{
            padding: "14px 24px",
            borderBottom: "1px solid var(--border)",
            background: "var(--sidebar-bg)",
            display: "flex",
            alignItems: "center",
            gap: 10,
            flexShrink: 0,
          }}
        >
          <span style={{ fontSize: 20 }}>🤖</span>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>
              BrewContent Knowledge Agent
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Powered by Ollama · Supabase pgvector · Notion · Playwright
            </div>
          </div>
        </header>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px max(24px, calc(50% - 380px))",
          }}
        >
          {messages.map((msg) => (
            <ChatBubble key={msg.id} msg={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div
          style={{
            padding: "16px 24px 20px",
            borderTop: "1px solid var(--border)",
            background: "var(--sidebar-bg)",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              gap: 10,
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              padding: "10px 12px 10px 16px",
              maxWidth: 800,
              margin: "0 auto",
            }}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about BrewContent…"
              rows={1}
              disabled={loading}
              style={{
                flex: 1,
                background: "none",
                border: "none",
                outline: "none",
                color: "var(--text)",
                resize: "none",
                lineHeight: 1.6,
                maxHeight: 180,
                overflowY: "auto",
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                width: 36,
                height: 36,
                borderRadius: "var(--radius-sm)",
                background:
                  loading || !input.trim() ? "var(--surface-2)" : "var(--accent)",
                border: "none",
                color:
                  loading || !input.trim() ? "var(--text-muted)" : "#fff",
                fontSize: 16,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                transition: "background 0.15s",
              }}
              title="Send (Enter)"
            >
              {loading ? "⟳" : "↑"}
            </button>
          </div>
          <div
            style={{
              textAlign: "center",
              fontSize: 11,
              color: "var(--text-muted)",
              marginTop: 8,
            }}
          >
            Press Enter to send · Shift+Enter for new line · Agent will scrape BrewContent if KB is incomplete
          </div>
        </div>
      </main>
    </div>
  );
}
