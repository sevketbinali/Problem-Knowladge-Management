"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { listRecords, deleteRecord, type ProblemRecord } from "@/lib/api";
import { RefreshCw, AlertCircle, ChevronDown, ChevronUp, Trash2 } from "lucide-react";

export default function RecordsView() {
  const { token } = useAuth();
  const [records, setRecords] = useState<ProblemRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  async function fetchRecords() {
    if (!token) return;
    setLoading(true);
    setError(null);
    const res = await listRecords(token);
    if (res.status === "success" && res.data) {
      setRecords(res.data);
    } else {
      setError(res.error || "Kayıtlar yüklenemedi.");
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchRecords();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function handleDelete(id: string) {
    if (!token || !confirm("Bu kaydı silmek istediğinize emin misiniz?")) return;
    const res = await deleteRecord(token, id);
    if (res.status === "success") {
      setRecords((prev) => prev.filter((r) => r.id !== id));
    }
  }

  const statusStyle = (status: string) => {
    switch (status) {
      case "resolved":
        return {
          color: "var(--color-success)",
          background: "var(--color-success-bg)",
          border: "1px solid rgba(78,201,138,0.2)",
        };
      case "pending":
        return {
          color: "var(--color-warning)",
          background: "var(--color-warning-bg)",
          border: "1px solid rgba(232,194,64,0.2)",
        };
      default:
        return {
          color: "var(--color-text-muted)",
          background: "var(--color-surface-hover)",
          border: "1px solid var(--color-border)",
        };
    }
  };

  return (
    <div
      className="animate-slide-up"
      style={{ maxWidth: 760, margin: "0 auto", padding: "40px 32px" }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 28,
        }}
      >
        <div>
          <h2
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 26,
              fontWeight: 500,
              color: "var(--color-text-primary)",
              marginBottom: 6,
              fontStyle: "italic",
            }}
          >
            Problem Kayıtları
          </h2>
          <p style={{ fontSize: 14, color: "var(--color-text-secondary)" }}>
            Çözülmüş tüm problemler ve alınan dersler
          </p>
        </div>
        <button
          onClick={fetchRecords}
          disabled={loading}
          style={{
            padding: 8,
            border: "1px solid var(--color-border)",
            borderRadius: 8,
            background: "var(--color-surface-hover)",
            color: "var(--color-text-secondary)",
            cursor: "pointer",
            opacity: loading ? 0.5 : 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <RefreshCw
            size={14}
            style={{ animation: loading ? "spin 0.8s linear infinite" : undefined }}
          />
        </button>
      </div>

      {/* Error */}
      {error && (
        <div
          className="animate-fade-in"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            background: "var(--color-danger-bg)",
            border: "1px solid rgba(224,80,80,0.2)",
            borderRadius: 10,
            marginBottom: 20,
          }}
        >
          <AlertCircle size={14} style={{ color: "var(--color-danger)", flexShrink: 0 }} />
          <span style={{ fontSize: 13, color: "var(--color-danger)" }}>{error}</span>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && records.length === 0 && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "80px 24px",
          }}
        >
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              border: "2px solid var(--color-border-hover)",
              borderTopColor: "var(--color-accent)",
              animation: "spin 0.7s linear infinite",
              marginBottom: 14,
            }}
          />
          <p style={{ fontSize: 13, color: "var(--color-text-muted)" }}>Kayıtlar yükleniyor…</p>
        </div>
      )}

      {/* Empty */}
      {!loading && records.length === 0 && !error && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "80px 24px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 12,
              background: "var(--color-surface-hover)",
              border: "1px solid var(--color-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 14,
            }}
          >
            <span
              style={{
                fontFamily: "var(--font-display)",
                fontSize: 22,
                color: "var(--color-text-muted)",
                fontStyle: "italic",
              }}
            >
              0
            </span>
          </div>
          <p style={{ fontSize: 14, color: "var(--color-text-muted)" }}>
            Henüz kayıt bulunmuyor.
          </p>
        </div>
      )}

      {/* Records */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {records.map((record, idx) => {
          const expanded = expandedId === record.id;
          return (
            <div
              key={record.id}
              className="animate-fade-in"
              style={{
                border: "1px solid var(--color-border)",
                borderRadius: 12,
                overflow: "hidden",
                background: "var(--color-surface)",
                transition: "border-color 0.15s",
                animationDelay: `${idx * 0.04}s`,
              }}
              onMouseEnter={(e) => {
                if (!expanded)
                  (e.currentTarget as HTMLElement).style.borderColor = "var(--color-border-hover)";
              }}
              onMouseLeave={(e) => {
                if (!expanded)
                  (e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)";
              }}
            >
              {/* Row header */}
              <button
                onClick={() => setExpandedId(expanded ? null : record.id)}
                style={{
                  width: "100%",
                  padding: "14px 18px",
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                {/* Methodology tag */}
                <span
                  style={{
                    fontSize: 10,
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    color: "var(--color-accent)",
                    background: "var(--color-accent-subtle)",
                    padding: "3px 8px",
                    borderRadius: 5,
                    textTransform: "uppercase",
                    flexShrink: 0,
                    letterSpacing: "0.06em",
                  }}
                >
                  {record.methodology || "—"}
                </span>

                {/* Department badge */}
                {record.department && (
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 700,
                      color: "var(--color-accent)",
                      background: "rgba(223,128,80,0.08)",
                      padding: "4px 10px",
                      borderRadius: 99,
                      border: "1px solid rgba(223,128,80,0.15)",
                      flexShrink: 0,
                    }}
                  >
                    {record.department}
                  </span>
                )}

                <div style={{ flex: 1, minWidth: 0 }}>
                  <p
                    style={{
                      fontSize: 14,
                      fontWeight: 500,
                      color: "var(--color-text-primary)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {record.title || "Başlıksız Problem"}
                  </p>
                  <p
                    style={{
                      fontSize: 11,
                      color: "var(--color-text-muted)",
                      fontFamily: "var(--font-mono)",
                      marginTop: 3,
                    }}
                  >
                    {record.created_at
                      ? new Date(record.created_at).toLocaleDateString("tr-TR", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                        })
                      : "—"}
                  </p>
                  {/* Tags Row */}
                  {record.tags && record.tags.length > 0 && (
                    <div style={{ display: "flex", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
                      {record.tags.map((tag) => (
                        <span
                          key={tag}
                          style={{
                            fontSize: 10,
                            fontWeight: 500,
                            color: "var(--color-text-secondary)",
                            background: "var(--color-surface-hover)",
                            padding: "2px 8px",
                            borderRadius: 6,
                            border: "1px solid var(--color-border)",
                          }}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "4px 10px",
                    borderRadius: 6,
                    flexShrink: 0,
                    ...statusStyle(record.resolution_status),
                  }}
                >
                  {record.resolution_status || "bilinmiyor"}
                </span>

                {expanded ? (
                  <ChevronUp size={14} style={{ color: "var(--color-text-muted)", flexShrink: 0 }} />
                ) : (
                  <ChevronDown size={14} style={{ color: "var(--color-text-muted)", flexShrink: 0 }} />
                )}
              </button>

              {/* Expanded content */}
              {expanded && (
                <div
                  className="animate-fade-in"
                  style={{
                    borderTop: "1px solid var(--color-border)",
                    padding: "18px 18px 16px",
                    display: "flex",
                    flexDirection: "column",
                    gap: 14,
                  }}
                >
                  {record.problem_description && (
                    <DetailField label="Problem Açıklaması" value={record.problem_description} />
                  )}
                  {record.root_cause && (
                    <DetailField label="Kök Neden" value={record.root_cause} />
                  )}
                  {record.lessons_learned && (
                    <div>
                      <DetailLabel label="Alınan Dersler" />
                      <div
                        style={{
                          marginTop: 8,
                          padding: "12px 14px",
                          background: "var(--color-info-bg)",
                          border: "1px solid rgba(69,170,200,0.15)",
                          borderRadius: 9,
                        }}
                      >
                        <p
                          style={{
                            fontSize: 13,
                            color: "var(--color-text-primary)",
                            lineHeight: 1.7,
                            whiteSpace: "pre-wrap",
                          }}
                        >
                          {record.lessons_learned}
                        </p>
                      </div>
                    </div>
                  )}

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      paddingTop: 6,
                    }}
                  >
                    <span
                      style={{
                        fontSize: 10,
                        fontFamily: "var(--font-mono)",
                        color: "var(--color-text-muted)",
                      }}
                    >
                      ID: {record.id}
                    </span>
                    <button
                      onClick={() => handleDelete(record.id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        padding: "5px 10px",
                        border: "none",
                        background: "none",
                        borderRadius: 7,
                        fontSize: 12,
                        color: "var(--color-text-muted)",
                        cursor: "pointer",
                        transition: "all 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "var(--color-danger)";
                        (e.currentTarget as HTMLElement).style.background = "var(--color-danger-bg)";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "var(--color-text-muted)";
                        (e.currentTarget as HTMLElement).style.background = "none";
                      }}
                    >
                      <Trash2 size={12} />
                      Sil
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function DetailLabel({ label }: { label: string }) {
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

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <DetailLabel label={label} />
      <p
        style={{
          marginTop: 6,
          fontSize: 13,
          color: "var(--color-text-secondary)",
          lineHeight: 1.6,
        }}
      >
        {value}
      </p>
    </div>
  );
}
