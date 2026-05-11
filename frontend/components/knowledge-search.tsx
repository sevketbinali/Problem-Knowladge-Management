"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { searchKnowledge, type SimilarProblem } from "@/lib/api";
import { Search, AlertCircle } from "lucide-react";

export default function KnowledgeSearch() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SimilarProblem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || !token) return;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    const res = await searchKnowledge(token, query.trim());
    if (res.status === "success" && res.data) {
      setResults(res.data);
    } else {
      setError(res.error || "Arama yapılamadı.");
    }
    setLoading(false);
  }

  return (
    <div
      className="animate-slide-up"
      style={{ maxWidth: 680, margin: "0 auto", padding: "40px 32px" }}
    >
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
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
          Bilgi Bankası
        </h2>
        <p style={{ fontSize: 14, color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          Geçmiş problem kayıtlarını anlamsal olarak arayın — vektör veritabanı üzerinden eşleştirme.
        </p>
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} style={{ marginBottom: 32 }}>
        <div style={{ position: "relative" }}>
          <Search
            size={16}
            style={{
              position: "absolute",
              left: 16,
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--color-text-muted)",
              pointerEvents: "none",
            }}
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Problemi doğal dilde arayın… (ör: sensör ısınması, motor arızası)"
            style={{
              width: "100%",
              padding: "14px 110px 14px 44px",
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              borderRadius: 12,
              fontSize: 14,
              color: "var(--color-text-primary)",
              fontFamily: "var(--font-sans)",
              outline: "none",
              transition: "border-color 0.15s, box-shadow 0.15s",
              boxSizing: "border-box",
            }}
            onFocus={(e) => {
              (e.target as HTMLInputElement).style.borderColor = "var(--color-accent)";
              (e.target as HTMLInputElement).style.boxShadow = "0 0 0 3px var(--color-accent-glow)";
            }}
            onBlur={(e) => {
              (e.target as HTMLInputElement).style.borderColor = "var(--color-border)";
              (e.target as HTMLInputElement).style.boxShadow = "none";
            }}
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            style={{
              position: "absolute",
              right: 6,
              top: "50%",
              transform: "translateY(-50%)",
              padding: "8px 16px",
              background: query.trim() && !loading ? "var(--color-accent)" : "var(--color-surface-hover)",
              border: `1px solid ${query.trim() && !loading ? "var(--color-accent)" : "var(--color-border)"}`,
              borderRadius: 8,
              fontSize: 12,
              fontWeight: 600,
              color: query.trim() && !loading ? "#fff" : "var(--color-text-muted)",
              cursor: query.trim() && !loading ? "pointer" : "not-allowed",
              display: "flex",
              alignItems: "center",
              gap: 6,
              transition: "all 0.15s",
            }}
          >
            {loading ? (
              <span
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  border: "2px solid rgba(255,255,255,0.3)",
                  borderTopColor: "#fff",
                  display: "inline-block",
                  animation: "spin 0.6s linear infinite",
                }}
              />
            ) : (
              <Search size={13} />
            )}
            Ara
          </button>
        </div>
      </form>

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

      {/* Pre-search state */}
      {!hasSearched && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "60px 24px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              width: 60,
              height: 60,
              borderRadius: 14,
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 16,
            }}
          >
            <Search size={24} style={{ color: "var(--color-text-muted)", opacity: 0.5 }} />
          </div>
          <p
            style={{
              fontSize: 14,
              color: "var(--color-text-secondary)",
              lineHeight: 1.7,
              maxWidth: 340,
            }}
          >
            Geçmiş problem kayıtlarını doğal dil ile arayın.
            Vektör veritabanı üzerinden anlamsal eşleştirme yapılır.
          </p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "60px 24px",
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              border: "2px solid var(--color-border-hover)",
              borderTopColor: "var(--color-accent)",
              animation: "spin 0.7s linear infinite",
              marginBottom: 12,
            }}
          />
          <p style={{ fontSize: 13, color: "var(--color-text-muted)" }}>
            Anlamsal arama yapılıyor…
          </p>
        </div>
      )}

      {/* No results */}
      {hasSearched && !loading && results.length === 0 && !error && (
        <div style={{ textAlign: "center", padding: "40px 24px" }}>
          <p style={{ fontSize: 14, color: "var(--color-text-muted)" }}>
            Aramanızla eşleşen kayıt bulunamadı.
          </p>
        </div>
      )}

      {/* Results */}
      {!loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {results.map((result, i) => (
            <div
              key={i}
              className="animate-fade-in"
              style={{
                padding: "16px 18px",
                border: "1px solid var(--color-border)",
                borderRadius: 12,
                background: "var(--color-surface)",
                transition: "border-color 0.15s",
                animationDelay: `${i * 0.05}s`,
                cursor: "default",
              }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border-hover)")
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)")
              }
            >
              {/* Title + score */}
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  gap: 12,
                  marginBottom: 10,
                }}
              >
                <h3
                  style={{
                    fontSize: 14,
                    fontWeight: 500,
                    color: "var(--color-text-primary)",
                    lineHeight: 1.4,
                  }}
                >
                  {result.payload.title}
                </h3>
                <span
                  style={{
                    fontSize: 11,
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    color: "var(--color-accent)",
                    background: "var(--color-accent-subtle)",
                    padding: "3px 8px",
                    borderRadius: 6,
                    flexShrink: 0,
                    whiteSpace: "nowrap",
                  }}
                >
                  {result.score}%
                </span>
              </div>

              {/* Tags */}
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
                <span
                  style={{
                    fontSize: 10,
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    color: "var(--color-text-muted)",
                    background: "var(--color-surface-hover)",
                    padding: "3px 8px",
                    borderRadius: 5,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                  }}
                >
                  {result.payload.methodology}
                </span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "3px 8px",
                    borderRadius: 5,
                    ...(result.payload.resolution_status === "resolved"
                      ? {
                          color: "var(--color-success)",
                          background: "var(--color-success-bg)",
                        }
                      : {
                          color: "var(--color-warning)",
                          background: "var(--color-warning-bg)",
                        }),
                  }}
                >
                  {result.payload.resolution_status}
                </span>
              </div>

              {/* Root cause */}
              <p
                style={{
                  fontSize: 12,
                  color: "var(--color-text-secondary)",
                  lineHeight: 1.5,
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                <span style={{ color: "var(--color-text-muted)", fontWeight: 600 }}>
                  Kök Neden:{" "}
                </span>
                {result.payload.root_cause}
              </p>
            </div>
          ))}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
