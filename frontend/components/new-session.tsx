"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { createSession, type SimilarProblem } from "@/lib/api";
import { AlertCircle, Zap, ArrowRight } from "lucide-react";

const methodologies = [
  {
    id: "5why",
    label: "5 Neden",
    labelEn: "Five Whys",
    description: "Kök nedene adım adım inin",
    color: "#df8050",
    bg: "rgba(223,128,80,0.08)",
    border: "rgba(223,128,80,0.3)",
  },
  {
    id: "ishikawa",
    label: "Ishikawa",
    labelEn: "Fishbone",
    description: "Balık kılçığı ile kategori analizi",
    color: "#45aac8",
    bg: "rgba(69,170,200,0.08)",
    border: "rgba(69,170,200,0.3)",
  },
  {
    id: "8d",
    label: "8D",
    labelEn: "Eight Disciplines",
    description: "8 disiplinli problem çözümü",
    color: "#4ec98a",
    bg: "rgba(78,201,138,0.08)",
    border: "rgba(78,201,138,0.3)",
  },
  {
    id: "pdca",
    label: "PDCA",
    labelEn: "Plan-Do-Check-Act",
    description: "Döngüsel sürekli iyileştirme",
    color: "#e8c240",
    bg: "rgba(232,194,64,0.08)",
    border: "rgba(232,194,64,0.3)",
  },
];

interface NewSessionProps {
  onSessionCreated: (
    sessionId: string,
    similarProblems: SimilarProblem[],
    firstPrompt: string,
    initialProblem: string
  ) => void;
}

export default function NewSession({ onSessionCreated }: NewSessionProps) {
  const { token } = useAuth();
  const [problem, setProblem] = useState("");
  const [methodology, setMethodology] = useState("5why");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (problem.length < 20) {
      setError("Problem açıklaması en az 20 karakter olmalıdır.");
      return;
    }
    if (!token) return;
    setError(null);
    setLoading(true);
    const res = await createSession(token, problem, methodology);
    if (res.status === "success" && res.data) {
      onSessionCreated(
        res.data.session_id,
        res.data.similar_problems || [],
        res.data.next_prompt || "",
        problem
      );
    } else {
      setError(res.error || "Oturum başlatılamadı.");
    }
    setLoading(false);
  }

  const selected = methodologies.find((m) => m.id === methodology)!;
  const charOk = problem.length >= 20;

  return (
    <div
      className="animate-slide-up"
      style={{ maxWidth: 680, margin: "0 auto", padding: "40px 32px" }}
    >
      {/* Page header */}
      <div style={{ marginBottom: 32 }}>
        <h2
          style={{
            fontFamily: "var(--font-display)",
            fontSize: 26,
            fontWeight: 500,
            color: "var(--color-text-primary)",
            marginBottom: 8,
            fontStyle: "italic",
          }}
        >
          Yeni Problem Oturumu
        </h2>
        <p style={{ fontSize: 14, color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          Problemi tanımlayın ve bir metodoloji seçin. AI asistanınız sizi adım
          adım yönlendirecektir.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Methodology selection */}
        <div style={{ marginBottom: 28 }}>
          <p
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "var(--color-text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 12,
            }}
          >
            Metodoloji Seçin
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 10,
            }}
          >
            {methodologies.map((m) => {
              const active = methodology === m.id;
              return (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setMethodology(m.id)}
                  style={{
                    padding: "14px 16px",
                    borderRadius: 12,
                    border: active ? `1px solid ${m.border}` : "1px solid var(--color-border)",
                    background: active ? m.bg : "var(--color-surface)",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.15s",
                    position: "relative",
                    overflow: "hidden",
                  }}
                  onMouseEnter={(e) => {
                    if (!active)
                      (e.currentTarget as HTMLElement).style.borderColor =
                        "var(--color-border-hover)";
                  }}
                  onMouseLeave={(e) => {
                    if (!active)
                      (e.currentTarget as HTMLElement).style.borderColor =
                        "var(--color-border)";
                  }}
                >
                  {/* Active indicator bar */}
                  {active && (
                    <div
                      style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 2,
                        background: m.color,
                        borderRadius: "12px 12px 0 0",
                      }}
                    />
                  )}

                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <span
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: 11,
                        fontWeight: 600,
                        color: active ? m.color : "var(--color-text-muted)",
                        letterSpacing: "0.06em",
                        textTransform: "uppercase",
                        background: active ? `${m.color}18` : "var(--color-surface-hover)",
                        padding: "2px 8px",
                        borderRadius: 5,
                        transition: "all 0.15s",
                      }}
                    >
                      {m.label}
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: 11,
                      color: active ? "var(--color-text-secondary)" : "var(--color-text-muted)",
                      lineHeight: 1.4,
                    }}
                  >
                    {m.description}
                  </p>
                </button>
              );
            })}
          </div>

          {/* Selected methodology info */}
          <div
            style={{
              marginTop: 10,
              padding: "8px 14px",
              background: "var(--color-surface-hover)",
              borderRadius: 8,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: selected.color,
                flexShrink: 0,
              }}
            />
            <span style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>
              <strong style={{ color: selected.color }}>{selected.label}</strong>
              {" "}— {selected.labelEn}
            </span>
          </div>
        </div>

        {/* Problem description */}
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 10,
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
              Problem Açıklaması
            </p>
            <span
              style={{
                fontSize: 11,
                fontFamily: "var(--font-mono)",
                color: charOk ? "var(--color-success)" : "var(--color-text-muted)",
                transition: "color 0.2s",
              }}
            >
              {problem.length} / 20 min
            </span>
          </div>

          <textarea
            value={problem}
            onChange={(e) => setProblem(e.target.value)}
            rows={6}
            placeholder="Problemi mümkün olduğunca detaylı açıklayın. Örn: Üretim hattındaki 3 numaralı sensör son 2 haftadır aşırı ısınıyor ve otomatik kapanmaya geçiyor..."
            style={{
              width: "100%",
              padding: "14px 16px",
              background: "var(--color-surface-hover)",
              border: charOk
                ? "1px solid rgba(78,201,138,0.3)"
                : "1px solid var(--color-border)",
              borderRadius: 12,
              fontSize: 14,
              color: "var(--color-text-primary)",
              fontFamily: "var(--font-sans)",
              lineHeight: 1.65,
              resize: "none",
              outline: "none",
              transition: "border-color 0.2s, box-shadow 0.2s",
              boxSizing: "border-box",
            }}
            onFocus={(e) => {
              (e.target as HTMLTextAreaElement).style.boxShadow =
                charOk
                  ? "0 0 0 3px rgba(78,201,138,0.1)"
                  : "0 0 0 3px var(--color-accent-glow)";
              (e.target as HTMLTextAreaElement).style.borderColor = charOk
                ? "rgba(78,201,138,0.4)"
                : "var(--color-accent)";
            }}
            onBlur={(e) => {
              (e.target as HTMLTextAreaElement).style.boxShadow = "none";
              (e.target as HTMLTextAreaElement).style.borderColor = charOk
                ? "rgba(78,201,138,0.3)"
                : "var(--color-border)";
            }}
          />
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
              marginBottom: 16,
            }}
          >
            <AlertCircle size={14} style={{ color: "var(--color-danger)", flexShrink: 0 }} />
            <span style={{ fontSize: 13, color: "var(--color-danger)" }}>{error}</span>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !charOk}
          className="btn-primary"
          style={{ width: "100%", padding: "14px 24px", fontSize: 14 }}
        >
          {loading ? (
            <>
              <span
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: "50%",
                  border: "2px solid rgba(255,255,255,0.3)",
                  borderTopColor: "#fff",
                  display: "inline-block",
                  animation: "spin 0.6s linear infinite",
                }}
              />
              Bağlam analiz ediliyor...
            </>
          ) : (
            <>
              <Zap size={15} />
              Oturumu Başlat
              <ArrowRight size={15} />
            </>
          )}
        </button>
      </form>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
