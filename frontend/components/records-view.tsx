"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { listRecords, deleteRecord, type ProblemRecord } from "@/lib/api";
import { RefreshCw, AlertCircle, ChevronDown, ChevronUp, Trash2, X } from "lucide-react";
import UnifiedRecordDetail from "./unified-record-detail";
import StatusBadge from "./status-badge";

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
    try {
      const res = await listRecords(token);
      if (res.status === "success" && res.data) {
        setRecords(res.data);
      } else {
        setError(res.error || "Kayıtlar yüklenemedi.");
      }
    } catch (err) {
      setError("Bağlantı hatası oluştu.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchRecords();
  }, [token]);

  async function handleDelete(id: string) {
    if (!token || !confirm("Bu kaydı silmek istediğinize emin misiniz?")) return;
    const res = await deleteRecord(token, id);
    if (res.status === "success") {
      setRecords((prev) => prev.filter((r) => r.id !== id));
    }
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: 26, fontWeight: 500, color: "var(--color-text-primary)", marginBottom: 8, fontStyle: "italic" }}>
            Problem Kayıtları
          </h2>
          <p style={{ fontSize: 14, color: "var(--color-text-secondary)" }}>
            Çözülmüş tüm problemler ve alınan dersler
          </p>
        </div>
        <button
          onClick={fetchRecords}
          disabled={loading}
          style={{ padding: 8, border: "1px solid var(--color-border)", borderRadius: 8, background: "var(--color-surface-hover)", color: "var(--color-text-secondary)", cursor: "pointer", opacity: loading ? 0.5 : 1, display: "flex", alignItems: "center", justifyContent: "center" }}
        >
          <RefreshCw size={14} style={{ animation: loading ? "spin 0.8s linear infinite" : undefined }} />
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 14px", background: "var(--color-danger-bg)", border: "1px solid rgba(224,80,80,0.2)", borderRadius: 10, marginBottom: 20 }}>
          <AlertCircle size={14} style={{ color: "var(--color-danger)", flexShrink: 0 }} />
          <span style={{ fontSize: 13, color: "var(--color-danger)" }}>{error}</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && records.length === 0 && !error && (
        <div style={{ textAlign: "center", padding: "60px 24px", background: "var(--color-surface)", borderRadius: 16, border: "1px dashed var(--color-border)" }}>
          <p style={{ fontSize: 14, color: "var(--color-text-muted)" }}>Henüz kayıt bulunmuyor.</p>
        </div>
      )}

      {/* Records List */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {records.map((record, idx) => {
          const expanded = expandedId === record.id;
          return (
            <div
              key={record.id}
              className="animate-fade-in"
              style={{
                border: "1px solid var(--color-border)",
                borderRadius: 14,
                overflow: "hidden",
                background: "var(--color-surface)",
                transition: "all 0.2s",
                animationDelay: `${idx * 0.05}s`,
                boxShadow: expanded ? "0 10px 30px rgba(0,0,0,0.05)" : "none",
                borderColor: expanded ? "var(--color-accent)" : "var(--color-border)"
              }}
            >
              {/* Row Header */}
              <button
                onClick={() => setExpandedId(expanded ? null : record.id)}
                style={{ width: "100%", padding: "16px 20px", display: "flex", alignItems: "center", gap: 16, background: "none", border: "none", cursor: "pointer", textAlign: "left" }}
              >
                <span style={{ fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--color-accent)", background: "var(--color-accent-subtle)", padding: "3px 8px", borderRadius: 5, textTransform: "uppercase", letterSpacing: "0.06em", border: "1px solid rgba(223, 128, 80, 0.2)" }}>
                  {record.methodology || "—"}
                </span>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: 15, fontWeight: 600, color: "var(--color-text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {record.title || "Başlıksız Problem"}
                  </p>
                  <p style={{ fontSize: 11, color: "var(--color-text-muted)", marginTop: 4 }}>
                    {record.created_at ? new Date(record.created_at).toLocaleDateString("tr-TR", { day: 'numeric', month: 'short', year: 'numeric' }) : "—"}
                  </p>
                  
                  {!expanded && record.problem_description && (
                    <p style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 6, opacity: 0.7, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {record.problem_description}
                    </p>
                  )}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <StatusBadge status={record.resolution_status || (record as any).status} />
                  {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </button>

              {/* Detail Content */}
              {expanded && (
                <div 
                  className="animate-fade-in"
                  style={{ 
                    borderTop: "1px solid var(--color-border)", 
                    padding: "32px 40px", 
                    background: "var(--color-surface-hover)" 
                  }}
                >
                  <UnifiedRecordDetail record={record} />
                  
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 24, paddingTop: 20, borderTop: "1px dashed var(--color-border)" }}>
                    <span style={{ fontSize: 10, fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>ID: {record.id}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(record.id); }}
                      style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", background: "var(--color-danger-bg)", border: "1px solid rgba(224,80,80,0.2)", borderRadius: 8, fontSize: 12, fontWeight: 600, color: "var(--color-danger)", cursor: "pointer" }}
                    >
                      <Trash2 size={14} />
                      Kaydı Sil
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
