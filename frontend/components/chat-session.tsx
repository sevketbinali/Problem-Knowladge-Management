"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import {
  submitStep,
  finalizeSession,
  stepBack,
  type SimilarProblem,
} from "@/lib/api";
import { Send, CheckCircle2, ArrowLeft, Flag, Loader2 } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface FinalizedReport {
  title?: string;
  record_id?: string;
  status?: string;
  lessons_learned?: string;
}

interface ChatSessionProps {
  sessionId: string;
  similarProblems: SimilarProblem[];
  firstPrompt: string;
  initialProblem: string;
  onFinalized: (report: FinalizedReport) => void;
}

export default function ChatSession({
  sessionId,
  similarProblems,
  firstPrompt,
  initialProblem,
  onFinalized,
}: ChatSessionProps) {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [initialPromptSet, setInitialPromptSet] = useState(false);

  useEffect(() => {
    if (!initialPromptSet && messages.length === 0) {
      const initialMessages: ChatMessage[] = [];
      if (initialProblem) {
        initialMessages.push({ role: "user", content: initialProblem });
      }
      if (firstPrompt) {
        initialMessages.push({ role: "assistant", content: firstPrompt });
      }
      if (initialMessages.length > 0) {
        setMessages(initialMessages);
      }
      setInitialPromptSet(true);
    }
  }, [initialPromptSet, messages.length, firstPrompt, initialProblem]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!loading) inputRef.current?.focus();
  }, [loading]);

  // Auto-resize textarea as content grows
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [input]);

  async function handleSend() {
    if (!input.trim() || !token || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    const res = await submitStep(token, sessionId, userMsg);
    if (res.status === "success" && res.data) {
      if (res.data.current_step !== undefined) {
        setCurrentStep(res.data.current_step);
      }
      if (res.data.status === "completed") {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: res.data!.message || "Analiz tamamlandı. Lütfen oturumu finalize edin.",
          },
        ]);
        setIsCompleted(true);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.data!.next_prompt || "" },
        ]);
      }
    } else {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ Hata: ${res.error || "Yanıt işlenemedi."}` },
      ]);
    }
    setLoading(false);
  }

  async function handleFinalize() {
    if (!token) return;
    setFinalizing(true);
    const res = await finalizeSession(token, sessionId);
    if (res.status === "success" && res.data) {
      onFinalized(res.data as FinalizedReport);
    }
    setFinalizing(false);
  }

  async function handleBack() {
    if (!token || loading) return;
    setLoading(true);
    const res = await stepBack(token, sessionId);
    if (res.status === "success" && res.data) {
      if (res.data.current_step !== undefined) {
        setCurrentStep(res.data.current_step);
      }
      // Revert the last 2 messages (user's answer + ai's current question)
      setMessages((prev) => prev.slice(0, -2));
      setIsCompleted(false);
    }
    setLoading(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* ── Chat area ──────────────────────────────── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {/* Header */}
        <div
          style={{
            padding: "14px 20px",
            borderBottom: "1px solid var(--color-border)",
            background: "var(--color-surface)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexShrink: 0,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "var(--color-accent-subtle)",
                border: "1px solid rgba(223,128,80,0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: 16,
                  color: "var(--color-accent)",
                  fontStyle: "italic",
                  fontWeight: 600,
                }}
              >
                AI
              </span>
            </div>
            <div>
              <p
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: "var(--color-text-primary)",
                }}
              >
                Problem Analizi
              </p>
              <p
                style={{
                  fontSize: 10,
                  color: "var(--color-text-muted)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {sessionId.slice(0, 8)}…
              </p>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {currentStep > 0 && !isCompleted && (
              <button
                onClick={handleBack}
                disabled={loading}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "6px 12px",
                  background: "var(--color-surface-hover)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "var(--color-text-secondary)",
                  cursor: "pointer",
                  transition: "all 0.15s",
                  opacity: loading ? 0.5 : 1,
                }}
              >
                <ArrowLeft size={12} />
                Geri Al
              </button>
            )}
            {isCompleted && (
              <button
                onClick={handleFinalize}
                disabled={finalizing}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "7px 14px",
                  background: "var(--color-success)",
                  border: "none",
                  borderRadius: 8,
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#fff",
                  cursor: "pointer",
                  opacity: finalizing ? 0.6 : 1,
                  transition: "opacity 0.15s",
                }}
              >
                {finalizing ? (
                  <Loader2 size={12} style={{ animation: "spin 0.6s linear infinite" }} />
                ) : (
                  <Flag size={12} />
                )}
                Finalize Et
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px 20px",
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {messages.length === 0 && (
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                padding: "60px 24px",
              }}
            >
              <div
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 14,
                  background: "var(--color-accent-subtle)",
                  border: "1px solid rgba(223,128,80,0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: 16,
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-display)",
                    fontSize: 24,
                    color: "var(--color-accent)",
                    fontStyle: "italic",
                    opacity: 0.6,
                  }}
                >
                  AI
                </span>
              </div>
              <p
                style={{
                  fontSize: 14,
                  color: "var(--color-text-secondary)",
                  lineHeight: 1.6,
                  maxWidth: 320,
                }}
              >
                Oturum başlatıldı. İlk yanıtınızı girin — AI asistanınız sizi analiz boyunca yönlendirecek.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className="animate-fade-in"
              style={{
                display: "flex",
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                gap: 10,
                animationDelay: `${i * 0.03}s`,
              }}
            >
              {msg.role === "assistant" && (
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 8,
                    background: "var(--color-accent-subtle)",
                    border: "1px solid rgba(223,128,80,0.2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    marginTop: 2,
                  }}
                >
                  <span
                    style={{
                      fontFamily: "var(--font-display)",
                      fontSize: 11,
                      color: "var(--color-accent)",
                      fontStyle: "italic",
                      fontWeight: 600,
                    }}
                  >
                    AI
                  </span>
                </div>
              )}

              <div
                style={{
                  maxWidth: "70%",
                  padding: "12px 16px",
                  borderRadius: msg.role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                  fontSize: 14,
                  lineHeight: 1.65,
                  ...(msg.role === "user"
                    ? {
                        background: "var(--color-accent)",
                        color: "#fff",
                      }
                    : {
                        background: "var(--color-surface)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }),
                }}
              >
                <p style={{ whiteSpace: "pre-wrap", margin: 0 }}>{msg.content}</p>
              </div>

              {msg.role === "user" && (
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 8,
                    background: "var(--color-surface-hover)",
                    border: "1px solid var(--color-border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    marginTop: 2,
                    fontSize: 12,
                    fontWeight: 700,
                    color: "var(--color-text-secondary)",
                  }}
                >
                  S
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="animate-fade-in" style={{ display: "flex", gap: 10 }}>
              <div
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: 8,
                  background: "var(--color-accent-subtle)",
                  border: "1px solid rgba(223,128,80,0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-display)",
                    fontSize: 11,
                    color: "var(--color-accent)",
                    fontStyle: "italic",
                    fontWeight: 600,
                  }}
                >
                  AI
                </span>
              </div>
              <div
                style={{
                  padding: "12px 16px",
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "14px 14px 14px 4px",
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                }}
              >
                {[0, 1, 2].map((j) => (
                  <span
                    key={j}
                    style={{
                      width: 7,
                      height: 7,
                      borderRadius: "50%",
                      background: "var(--color-text-muted)",
                      display: "inline-block",
                      animation: `typing-dot 1.4s infinite ${j * 0.2}s`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed badge */}
          {isCompleted && (
            <div
              className="animate-fade-in"
              style={{ display: "flex", justifyContent: "center" }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "8px 16px",
                  background: "var(--color-success-bg)",
                  border: "1px solid rgba(78,201,138,0.2)",
                  borderRadius: 999,
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--color-success)",
                }}
              >
                <CheckCircle2 size={14} />
                Analiz tamamlandı — Finalize edebilirsiniz
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input bar */}
        {!isCompleted && (
          <div
            style={{
              padding: "14px 16px",
              borderTop: "1px solid var(--color-border)",
              background: "var(--color-surface)",
              flexShrink: 0,
            }}
          >
            <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Yanıtınızı yazın… (Enter ile gönderin, Shift+Enter yeni satır)"
                disabled={loading}
                style={{
                  flex: 1,
                  padding: "11px 14px",
                  background: "var(--color-surface-hover)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 10,
                  fontSize: 14,
                  color: "var(--color-text-primary)",
                  fontFamily: "var(--font-sans)",
                  resize: "none",
                  outline: "none",
                  lineHeight: 1.5,
                  transition: "border-color 0.15s, box-shadow 0.15s",
                  opacity: loading ? 0.5 : 1,
                  overflow: "hidden",
                  minHeight: 44,
                  maxHeight: 200,
                  overflowY: "auto",
                }}
                onFocus={(e) => {
                  (e.target as HTMLTextAreaElement).style.borderColor = "var(--color-accent)";
                  (e.target as HTMLTextAreaElement).style.boxShadow = "0 0 0 3px var(--color-accent-glow)";
                }}
                onBlur={(e) => {
                  (e.target as HTMLTextAreaElement).style.borderColor = "var(--color-border)";
                  (e.target as HTMLTextAreaElement).style.boxShadow = "none";
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 10,
                  background: input.trim() && !loading ? "var(--color-accent)" : "var(--color-surface-hover)",
                  border: `1px solid ${input.trim() && !loading ? "var(--color-accent)" : "var(--color-border)"}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: input.trim() && !loading ? "pointer" : "not-allowed",
                  flexShrink: 0,
                  transition: "all 0.15s",
                  color: input.trim() && !loading ? "#fff" : "var(--color-text-muted)",
                }}
              >
                <Send size={15} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Similar problems sidebar ──────────────── */}
      <div
        style={{
          width: 260,
          borderLeft: "1px solid var(--color-border)",
          background: "var(--color-surface)",
          overflowY: "auto",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            padding: "14px 16px",
            borderBottom: "1px solid var(--color-border)",
          }}
        >
          <p
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "var(--color-text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
            }}
          >
            Benzer Problemler
          </p>
        </div>

        <div style={{ padding: "12px 12px", display: "flex", flexDirection: "column", gap: 8 }}>
          {similarProblems.length > 0 ? (
            similarProblems.map((prob, i) => (
              <div
                key={i}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "var(--color-surface-hover)",
                  border: "1px solid var(--color-border)",
                  transition: "border-color 0.15s",
                  cursor: "default",
                }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border-hover)")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)")
                }
              >
                <p
                  style={{
                    fontSize: 12,
                    fontWeight: 500,
                    color: "var(--color-text-primary)",
                    marginBottom: 6,
                    lineHeight: 1.4,
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {prob.payload.title}
                </p>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <span
                    style={{
                      fontSize: 10,
                      fontFamily: "var(--font-mono)",
                      fontWeight: 600,
                      color: "var(--color-accent)",
                      background: "var(--color-accent-subtle)",
                      padding: "2px 7px",
                      borderRadius: 4,
                      textTransform: "uppercase",
                    }}
                  >
                    {prob.payload.methodology}
                  </span>
                  <span
                    style={{
                      fontSize: 10,
                      fontFamily: "var(--font-mono)",
                      color: "var(--color-text-muted)",
                    }}
                  >
                    {prob.score}%
                  </span>
                </div>
                <p
                  style={{
                    fontSize: 11,
                    color: "var(--color-text-muted)",
                    lineHeight: 1.4,
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {prob.payload.root_cause}
                </p>
              </div>
            ))
          ) : (
            <div style={{ padding: "24px 8px", textAlign: "center" }}>
              <p style={{ fontSize: 12, color: "var(--color-text-muted)", lineHeight: 1.5 }}>
                Bu probleme benzer geçmiş kayıt bulunamadı.
              </p>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
