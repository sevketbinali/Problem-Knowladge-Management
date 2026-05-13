"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import {
  MessageSquarePlus,
  Database,
  Search,
  Activity,
  LogOut,
  CheckCircle,
  X,
} from "lucide-react";
import NewSession from "@/components/new-session";
import ChatSession from "@/components/chat-session";
import RecordsView from "@/components/records-view";
import KnowledgeSearch from "@/components/knowledge-search";
import type { SimilarProblem } from "@/lib/api";

type View = "new" | "chat" | "records" | "search" | "report";

interface FinalizedReport {
  title?: string;
  record_id?: string;
  status?: string;
  lessons_learned?: string;
}

interface ActiveSession {
  id: string;
  firstPrompt: string;
  initialProblem: string;
  similarProblems: SimilarProblem[];
  methodologyLabel?: string; // To show in the sidebar
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState<View>("new");
  const [sessions, setSessions] = useState<ActiveSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [finalizedReport, setFinalizedReport] = useState<FinalizedReport | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: "info" | "warning" } | null>(null);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  function handleSessionCreated(id: string, problems: SimilarProblem[], prompt: string, problemText: string) {
    if (sessions.length >= 5) {
      setNotification({ message: "Maksimum 5 oturum sınırına ulaştınız. Lütfen bir oturumu bitirin.", type: "warning" });
      return;
    }

    const newSession: ActiveSession = {
      id,
      similarProblems: problems,
      firstPrompt: prompt,
      initialProblem: problemText,
    };

    const newSessions = [...sessions, newSession];
    setSessions(newSessions);
    setActiveSessionId(id);
    setCurrentView("chat");

    if (newSessions.length === 4) {
      setNotification({ message: "En fazla 5 oturum açılabilmektedir, 1 oturum daha açabilirsiniz.", type: "info" });
    }
  }

  function handleFinalized(report: FinalizedReport) {
    setFinalizedReport(report);
    // Remove the finalized session from active sessions
    setSessions(prev => prev.filter(s => s.id !== activeSessionId));
    setActiveSessionId(null);
    setCurrentView("report");
  }

  function handleNewSession() {
    if (sessions.length >= 5) {
      setNotification({ message: "Maksimum 5 oturum sınırına ulaştınız. Yeni bir oturum açmak için mevcut birini tamamlamanız gerekir.", type: "warning" });
      return;
    }
    setActiveSessionId(null);
    setFinalizedReport(null);
    setCurrentView("new");
  }

  const navItems = [
    { id: "new" as View, icon: MessageSquarePlus, label: "Yeni Oturum", badge: null },
    { id: "records" as View, icon: Database, label: "Kayıtlar", badge: null },
    { id: "search" as View, icon: Search, label: "Bilgi Bankası", badge: null },
  ];

  const initials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : "UK";

  return (
    <div className="min-h-screen flex">
      {/* ── Sidebar ─────────────────────────────────── */}
      <aside
        style={{
          width: 240,
          background: "var(--color-surface)",
          borderRight: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          position: "fixed",
          height: "100vh",
        }}
      >
        {/* Brand */}
        <div
          style={{
            padding: "20px 20px 16px",
            borderBottom: "1px solid var(--color-border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 8,
                background: "var(--color-accent-subtle)",
                border: "1px solid rgba(223,128,80,0.25)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 600,
                  fontSize: 15,
                  color: "var(--color-accent)",
                  fontStyle: "italic",
                }}
              >
                P
              </span>
            </div>
            <div>
              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: 15,
                  fontWeight: 600,
                  color: "var(--color-text-primary)",
                  fontStyle: "italic",
                }}
              >
                PKM Sistemi
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: "var(--color-text-muted)",
                  letterSpacing: "0.06em",
                  fontFamily: "var(--font-mono)",
                }}
              >
                v0.1.0
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "12px 10px", display: "flex", flexDirection: "column", gap: 2 }}>
          <p
            style={{
              fontSize: 9,
              color: "var(--color-text-muted)",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              padding: "4px 10px 8px",
              fontWeight: 600,
            }}
          >
            Navigasyon
          </p>

          {navItems.map((item) => {
            const active = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "9px 10px",
                  borderRadius: active ? "0 8px 8px 0" : 8,
                  marginLeft: active ? -10 : 0,
                  paddingLeft: active ? 20 : 10,
                  fontSize: 13,
                  fontWeight: active ? 600 : 400,
                  color: active ? "var(--color-accent)" : "var(--color-text-secondary)",
                  background: active ? "var(--color-accent-subtle)" : "transparent",
                  border: "none",
                  borderLeft: active ? "2px solid var(--color-accent)" : "2px solid transparent",
                  cursor: "pointer",
                  transition: "all 0.15s",
                  width: active ? "calc(100% + 10px)" : "100%",
                  textAlign: "left",
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.background = "var(--color-surface-hover)";
                    (e.currentTarget as HTMLElement).style.color = "var(--color-text-primary)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                    (e.currentTarget as HTMLElement).style.color = "var(--color-text-secondary)";
                  }
                }}
              >
                <item.icon size={15} style={{ flexShrink: 0 }} />
                {item.label}
              </button>
            );
          })}

          {/* Active sessions list */}
          {sessions.length > 0 && (
            <>
              <div
                style={{
                  height: 1,
                  background: "var(--color-border)",
                  margin: "8px 0",
                }}
              />
              <p
                style={{
                  fontSize: 9,
                  color: "var(--color-text-muted)",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  padding: "4px 10px 8px",
                  fontWeight: 600,
                }}
              >
                Aktif Oturumlar ({sessions.length}/5)
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {sessions.map((s) => {
                  const isActive = activeSessionId === s.id && currentView === "chat";
                  return (
                    <button
                      key={s.id}
                      onClick={() => {
                        setActiveSessionId(s.id);
                        setCurrentView("chat");
                      }}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "9px 10px",
                        borderRadius: isActive ? "0 8px 8px 0" : 8,
                        marginLeft: isActive ? -10 : 0,
                        paddingLeft: isActive ? 20 : 10,
                        fontSize: 12,
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? "var(--color-success)" : "var(--color-text-secondary)",
                        background: isActive ? "var(--color-success-bg)" : "transparent",
                        border: "none",
                        borderLeft: isActive ? "2px solid var(--color-success)" : "2px solid transparent",
                        cursor: "pointer",
                        transition: "all 0.15s",
                        width: isActive ? "calc(100% + 10px)" : "100%",
                        textAlign: "left",
                      }}
                    >
                      <span
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: "50%",
                          background: isActive ? "var(--color-success)" : "var(--color-text-muted)",
                          boxShadow: isActive ? "0 0 6px var(--color-success)" : "none",
                          flexShrink: 0,
                          animation: isActive ? "pulse-dot 2s ease-in-out infinite" : "none",
                        }}
                      />
                      <span style={{ 
                        overflow: "hidden", 
                        textOverflow: "ellipsis", 
                        whiteSpace: "nowrap" 
                      }}>
                        {s.initialProblem.slice(0, 20)}...
                      </span>
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </nav>

        {/* User footer */}
        <div
          style={{
            padding: "12px 10px",
            borderTop: "1px solid var(--color-border)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "8px 10px",
              borderRadius: 8,
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: "linear-gradient(135deg, var(--color-accent), var(--color-accent-hover))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.04em",
                flexShrink: 0,
              }}
            >
              {initials}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p
                style={{
                  fontSize: 12,
                  fontWeight: 500,
                  color: "var(--color-text-primary)",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {user?.email}
              </p>
              <p
                style={{
                  fontSize: 10,
                  color: "var(--color-text-muted)",
                  textTransform: "capitalize",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {user?.role || "user"}
              </p>
            </div>
            <button
              onClick={logout}
              title="Çıkış Yap"
              style={{
                padding: 6,
                border: "none",
                background: "none",
                cursor: "pointer",
                color: "var(--color-text-muted)",
                borderRadius: 6,
                display: "flex",
                transition: "color 0.15s",
              }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLElement).style.color = "var(--color-danger)")
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLElement).style.color = "var(--color-text-muted)")
              }
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────── */}
      <main style={{ flex: 1, marginLeft: 240, minHeight: "100vh" }}>
        <div style={{ height: "100vh", overflowY: "auto" }}>
          {currentView === "new" && (
            <NewSession onSessionCreated={handleSessionCreated} />
          )}
          {/* Render all active sessions but only show the current one */}
          {sessions.map(s => (
            <div 
              key={s.id} 
              style={{ display: (currentView === "chat" && activeSessionId === s.id) ? "block" : "none", height: "100%" }}
            >
              <ChatSession
                sessionId={s.id}
                similarProblems={s.similarProblems}
                firstPrompt={s.firstPrompt}
                initialProblem={s.initialProblem}
                onFinalized={handleFinalized}
              />
            </div>
          ))}

          {currentView === "records" && <RecordsView />}
          {currentView === "search" && <KnowledgeSearch />}
          {currentView === "report" && finalizedReport && (
            <ReportView report={finalizedReport} onNewSession={handleNewSession} />
          )}
        </div>

        {/* Global Notifications */}
        {notification && (
          <div
            style={{
              position: "fixed",
              bottom: 24,
              right: 24,
              padding: "12px 20px",
              background: notification.type === "warning" ? "var(--color-danger-bg)" : "var(--color-info-bg)",
              border: `1px solid ${notification.type === "warning" ? "var(--color-danger)" : "var(--color-accent)"}`,
              borderRadius: 12,
              color: notification.type === "warning" ? "var(--color-danger)" : "var(--color-text-primary)",
              boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
              display: "flex",
              alignItems: "center",
              gap: 12,
              zIndex: 10000,
              animation: "slide-in-right 0.3s ease-out",
            }}
          >
            <Activity size={18} />
            <span style={{ fontSize: 13, fontWeight: 500 }}>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              style={{
                background: "none",
                border: "none",
                color: "inherit",
                cursor: "pointer",
                padding: 4,
                opacity: 0.6,
              }}
            >
              <X size={14} />
            </button>
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        @keyframes slide-in-right {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

/* ── Report View ──────────────────────────────────────── */
function ReportView({
  report,
  onNewSession,
}: {
  report: FinalizedReport;
  onNewSession: () => void;
}) {
  return (
    <div
      className="animate-slide-up"
      style={{ maxWidth: 680, margin: "0 auto", padding: 40 }}
    >
      <div className="card-amber" style={{ borderRadius: "0 0 18px 18px", padding: 36 }}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 28 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 10,
              background: "var(--color-success-bg)",
              border: "1px solid rgba(78,201,138,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <CheckCircle size={22} style={{ color: "var(--color-success)" }} />
          </div>
          <div>
            <h2
              style={{
                fontFamily: "var(--font-display)",
                fontSize: 22,
                fontWeight: 500,
                color: "var(--color-text-primary)",
              }}
            >
              Çözüm Raporu
            </h2>
            <p style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>
              Lessons Learned — Bilgi bankasına eklendi
            </p>
          </div>
        </div>

        {/* Success banner */}
        <div
          style={{
            padding: "12px 16px",
            background: "var(--color-success-bg)",
            border: "1px solid rgba(78,201,138,0.15)",
            borderRadius: 10,
            marginBottom: 24,
            fontSize: 13,
            color: "var(--color-success)",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <CheckCircle size={15} />
          Bu problem bilgi bankasına başarıyla eklendi!
        </div>

        {/* Details */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20, marginBottom: 28 }}>
          {report.title && (
            <Field label="Başlık" value={report.title} />
          )}
          {report.record_id && (
            <Field label="Kayıt ID" value={report.record_id} mono />
          )}
          {report.status && (
            <Field label="Durum" value={report.status} />
          )}
          {report.lessons_learned && (
            <div>
              <FieldLabel label="Alınan Dersler" />
              <div
                style={{
                  marginTop: 8,
                  padding: "14px 16px",
                  background: "var(--color-info-bg)",
                  border: "1px solid rgba(69,170,200,0.15)",
                  borderRadius: 10,
                }}
              >
                <p
                  style={{
                    fontSize: 14,
                    color: "var(--color-text-primary)",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {report.lessons_learned}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Action */}
        <button onClick={onNewSession} className="btn-primary" style={{ width: "100%" }}>
          <MessageSquarePlus size={15} />
          Yeni Oturum Başlat
        </button>
      </div>
    </div>
  );
}

function FieldLabel({ label }: { label: string }) {
  return (
    <p
      style={{
        fontSize: 10,
        fontWeight: 700,
        color: "var(--color-text-muted)",
        textTransform: "uppercase",
        letterSpacing: "0.1em",
      }}
    >
      {label}
    </p>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <FieldLabel label={label} />
      <p
        style={{
          marginTop: 6,
          fontSize: mono ? 12 : 14,
          color: "var(--color-text-secondary)",
          fontFamily: mono ? "var(--font-mono)" : undefined,
          background: mono ? "var(--color-surface-hover)" : undefined,
          padding: mono ? "8px 12px" : undefined,
          borderRadius: mono ? 8 : undefined,
        }}
      >
        {value}
      </p>
    </div>
  );
}
