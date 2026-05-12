"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { 
  Send, 
  CheckCircle2, 
  ArrowLeft, 
  Flag, 
  Loader2, 
  Sparkles, 
  X, 
  Tag, 
  Info,
  ExternalLink
} from "lucide-react";
import { 
  submitStep,
  finalizeSession,
  stepBack,
  getSuggestions, 
  getRecord, 
  type ProblemRecord,
  type SimilarProblem 
} from "@/lib/api";

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
  const [localSimilarProblems, setLocalSimilarProblems] = useState<SimilarProblem[]>(similarProblems);
  
  // Update local state if props change (initial load)
  useEffect(() => {
    if (similarProblems && similarProblems.length > 0 && localSimilarProblems.length === 0) {
      setLocalSimilarProblems(similarProblems);
    }
  }, [similarProblems]);

  // Modal states for similar record details
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [detailRecord, setDetailRecord] = useState<ProblemRecord | null>(null);
  const [fetchingDetail, setFetchingDetail] = useState(false);

  // Modal states for finalization
  const [isFinalizeModalOpen, setIsFinalizeModalOpen] = useState(false);
  const [editedDepartment, setEditedDepartment] = useState("");
  const [editedSummary, setEditedSummary] = useState("");
  const [editedTags, setEditedTags] = useState("");
  const [isDeptAI, setIsDeptAI] = useState(true);
  const [isSummaryAI, setIsSummaryAI] = useState(true);
  const [isTagsAI, setIsTagsAI] = useState(true);

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

        // Dynamic Similarity Update: Search again with new context
        if (token) {
          searchKnowledge(token, userMsg).then(simRes => {
            if (simRes.status === "success" && simRes.data) {
              setLocalSimilarProblems(simRes.data);
            }
          });
        }
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
    const res = await getSuggestions(token, sessionId);
    if (res.status === "success" && res.data) {
      setEditedDepartment(res.data.department);
      setEditedSummary(res.data.summary);
      setEditedTags(res.data.tags.join(", "));
      setIsDeptAI(true);
      setIsSummaryAI(true);
      setIsTagsAI(true);
      setIsFinalizeModalOpen(true);
    } else {
      // Fallback if suggestions fail
      setEditedDepartment("Üretim");
      setEditedSummary(initialProblem.slice(0, 50));
      setEditedTags("");
      setIsFinalizeModalOpen(true);
    }
    setFinalizing(false);
  }

  async function handleConfirmFinalize() {
    if (!token) return;
    setFinalizing(true);
    const res = await finalizeSession(token, sessionId, {
      department: editedDepartment,
      summary: editedSummary,
      tags: editedTags,
    });
    if (res.status === "success" && res.data) {
      setIsFinalizeModalOpen(false);
      onFinalized(res.data as FinalizedReport);
    }
    setFinalizing(false);
  }

  async function openRecordDetail(recordId: string) {
    if (!token || !recordId) return;
    setFetchingDetail(true);
    try {
      const res = await getRecord(token, recordId);
      if (res.status === "success" && res.data) {
        setDetailRecord(res.data);
        setIsDetailModalOpen(true);
      } else {
        alert("Kayıt detayları getirilemedi: " + (res.error || "Bilinmeyen hata"));
      }
    } catch (err) {
      console.error("Failed to fetch record detail", err);
    } finally {
      setFetchingDetail(false);
    }
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
      {/* ── Similar Record Detail Modal ──────────────── */}
      {isDetailModalOpen && detailRecord && (
        <div 
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 9999, padding: 20
          }}
          onClick={() => setIsDetailModalOpen(false)}
        >
          <div 
            style={{
              width: "100%", maxWidth: 800, maxHeight: "90vh",
              background: "var(--color-surface)", borderRadius: 20,
              border: "1px solid var(--color-border)",
              boxShadow: "0 20px 50px rgba(0,0,0,0.2)",
              display: "flex", flexDirection: "column", overflow: "hidden"
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--color-border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--color-text-primary)" }}>Kayıt Detayı</h3>
                <p style={{ fontSize: 12, color: "var(--color-text-muted)" }}>ID: {detailRecord.id}</p>
              </div>
              <button onClick={() => setIsDetailModalOpen(false)} style={{ background: "none", border: "none", color: "var(--color-text-muted)", cursor: "pointer" }}>
                <X size={20} />
              </button>
            </div>
            
            <div style={{ flex: 1, overflowY: "auto", padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
              <div>
                <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", color: "var(--color-accent)", marginBottom: 8 }}>Başlık</h4>
                <p style={{ fontSize: 16, fontWeight: 600, color: "var(--color-text-primary)" }}>{detailRecord.title}</p>
              </div>

              <div style={{ display: "flex", gap: 30 }}>
                <div>
                  <h4 style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 4 }}>Metodoloji</h4>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-accent)", background: "var(--color-accent-subtle)", padding: "4px 10px", borderRadius: 6 }}>{detailRecord.methodology}</span>
                </div>
                <div>
                  <h4 style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 4 }}>Departman</h4>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-primary)", background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", padding: "4px 10px", borderRadius: 6 }}>{detailRecord.department || "Bilinmiyor"}</span>
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 8 }}>Problem Açıklaması</h4>
                <p style={{ fontSize: 14, color: "var(--color-text-secondary)", lineHeight: 1.6, background: "var(--color-surface-hover)", padding: 16, borderRadius: 12 }}>{detailRecord.problem_description}</p>
              </div>

              <div>
                <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 8 }}>Kök Neden</h4>
                <p style={{ fontSize: 14, color: "var(--color-text-primary)", lineHeight: 1.6, borderLeft: "3px solid var(--color-accent)", paddingLeft: 16 }}>{detailRecord.root_cause}</p>
              </div>

              <div>
                <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 8 }}>Alınan Dersler</h4>
                <div style={{ fontSize: 14, color: "var(--color-text-secondary)", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{detailRecord.lessons_learned}</div>
              </div>

              {detailRecord.tags && detailRecord.tags.length > 0 && (
                <div>
                  <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 8 }}>Etiketler</h4>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                    {detailRecord.tags.map(t => (
                      <span key={t} style={{ fontSize: 12, color: "var(--color-text-secondary)", background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", padding: "4px 12px", borderRadius: 999 }}>#{t}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
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
          {localSimilarProblems.length > 0 ? (
            localSimilarProblems.map((prob, i) => (
              <div
                key={i}
                onClick={() => {
                  openRecordDetail(prob.id);
                }}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "var(--color-surface-hover)",
                  border: "1px solid var(--color-border)",
                  transition: "all 0.15s",
                  cursor: "pointer",
                }}
                onMouseEnter={(e) => {
                  ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-accent)");
                  ((e.currentTarget as HTMLElement).style.transform = "translateY(-2px)");
                  ((e.currentTarget as HTMLElement).style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)");
                }}
                onMouseLeave={(e) => {
                  ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)");
                  ((e.currentTarget as HTMLElement).style.transform = "translateY(0)");
                  ((e.currentTarget as HTMLElement).style.boxShadow = "none");
                }}
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
                    {(prob.score * 100).toFixed(1)}%
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


      {/* ── Finalize Confirmation Modal ──────────────── */}
      {isFinalizeModalOpen && (
        <div 
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0,0,0,0.6)", backdropFilter: "blur(8px)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 1100, padding: 20
          }}
        >
          <div 
            style={{
              width: "100%", maxWidth: 500,
              background: "var(--color-surface)", borderRadius: 24,
              border: "1px solid var(--color-border)",
              boxShadow: "0 30px 60px rgba(0,0,0,0.3)",
              padding: 32, display: "flex", flexDirection: "column", gap: 24
            }}
          >
            <div style={{ textAlign: "center" }}>
              <div style={{ width: 64, height: 64, borderRadius: 20, background: "var(--color-success-bg)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
                <CheckCircle2 size={32} color="var(--color-success)" />
              </div>
              <h3 style={{ fontSize: 22, fontWeight: 800, color: "var(--color-text-primary)", marginBottom: 8 }}>Analizi Tamamla</h3>
              <p style={{ fontSize: 14, color: "var(--color-text-muted)" }}>Lütfen aşağıdaki bilgileri kontrol edin ve onaylayın.</p>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Summary */}
              <div style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                  <label style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)" }}>Problem Özeti</label>
                  {isSummaryAI && (
                    <div title="AI tarafından üretildi" style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--color-accent)", fontSize: 10, fontWeight: 700 }}>
                      <Sparkles size={10} /> AI ÜRETİMİ
                    </div>
                  )}
                </div>
                <textarea 
                  value={editedSummary}
                  onChange={e => { setEditedSummary(e.target.value); setIsSummaryAI(false); }}
                  rows={2}
                  style={{ width: "100%", padding: 12, borderRadius: 12, background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", fontSize: 14, resize: "none", outline: "none" }}
                />
              </div>

              {/* Department */}
              <div style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                  <label style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)" }}>Departman</label>
                  {isDeptAI && (
                    <div title="AI tarafından üretildi" style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--color-accent)", fontSize: 10, fontWeight: 700 }}>
                      <Sparkles size={10} /> AI ÜRETİMİ
                    </div>
                  )}
                </div>
                <select 
                  value={editedDepartment}
                  onChange={e => { setEditedDepartment(e.target.value); setIsDeptAI(false); }}
                  style={{ width: "100%", padding: "12px", borderRadius: 12, background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", fontSize: 14, outline: "none" }}
                >
                  <option value="Üretim">Üretim</option>
                  <option value="Lojistik">Lojistik</option>
                  <option value="Kalite">Kalite</option>
                  <option value="Bilgi İşlem">Bilgi İşlem</option>
                  <option value="Finans">Finans</option>
                </select>
              </div>

              {/* Tags */}
              <div style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                  <label style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)" }}>Etiketler (Virgülle ayırın)</label>
                  {isTagsAI && (
                    <div title="AI tarafından üretildi" style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--color-accent)", fontSize: 10, fontWeight: 700 }}>
                      <Sparkles size={10} /> AI ÜRETİMİ
                    </div>
                  )}
                </div>
                <div style={{ position: "relative" }}>
                  <Tag size={14} style={{ position: "absolute", left: 12, top: 15, color: "var(--color-text-muted)" }} />
                  <input 
                    value={editedTags}
                    onChange={e => { setEditedTags(e.target.value); setIsTagsAI(false); }}
                    placeholder="tag1, tag2, tag3"
                    style={{ width: "100%", padding: "12px 12px 12px 36px", borderRadius: 12, background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", fontSize: 14, outline: "none" }}
                  />
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <button 
                onClick={() => setIsFinalizeModalOpen(false)}
                style={{ flex: 1, padding: "14px", borderRadius: 14, background: "var(--color-surface-hover)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", fontSize: 14, fontWeight: 600, cursor: "pointer" }}
              >
                İptal
              </button>
              <button 
                onClick={handleConfirmFinalize}
                disabled={finalizing}
                style={{ 
                  flex: 2, padding: "14px", borderRadius: 14, 
                  background: "var(--color-accent)", color: "#fff", 
                  fontSize: 14, fontWeight: 700, border: "none", cursor: "pointer",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                  opacity: finalizing ? 0.7 : 1
                }}
              >
                {finalizing ? <Loader2 size={18} style={{ animation: "spin 0.6s linear infinite" }} /> : <Flag size={16} />}
                Kaydı Tamamla ve Yayınla
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes typing-dot {
          0%, 100% { transform: translateY(0); opacity: 0.4; }
          50% { transform: translateY(-4px); opacity: 1; }
        }
        .animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
        @keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
