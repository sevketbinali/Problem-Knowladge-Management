"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { searchKnowledge, getRecord, type SimilarProblem, type ProblemRecord } from "@/lib/api";
import { Search, AlertCircle, ChevronDown, ChevronUp, Layers, Activity, Calendar, Loader2 } from "lucide-react";
import UnifiedRecordDetail from "./unified-record-detail";
import StatusBadge from "./status-badge";

export default function KnowledgeSearch() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SimilarProblem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [fullRecordsCache, setFullRecordsCache] = useState<Record<string, ProblemRecord>>({});
  const [fetchingIds, setFetchingIds] = useState<Record<string, boolean>>({});

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !query.trim()) return;

    setLoading(true);
    setError(null);
    setExpandedId(null);
    try {
      const res = await searchKnowledge(token, query);
      if (res.status === "success") {
        setResults(res.data || []);
      } else {
        setError(res.error || "Arama başarısız oldu.");
      }
    } catch (err) {
      setError("Arama sırasında bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }

  async function toggleExpand(id: string) {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }

    setExpandedId(id);

    // Detay verisi zaten varsa tekrar çekme
    if (fullRecordsCache[id]) return;

    // Detay verisini çek
    setFetchingIds(prev => ({ ...prev, [id]: true }));
    try {
      const res = await getRecord(token!, id);
      if (res.status === "success" && res.data) {
        setFullRecordsCache(prev => ({ ...prev, [id]: res.data! }));
      }
    } catch (err) {
      console.error("Failed to fetch full record", err);
    } finally {
      setFetchingIds(prev => ({ ...prev, [id]: false }));
    }
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: 28, fontWeight: 500, color: "var(--color-text-primary)", fontStyle: "italic", marginBottom: 12 }}>
          Bilgi Bankası
        </h2>
        <p style={{ fontSize: 15, color: "var(--color-text-secondary)" }}>
          Geçmişteki tüm problem kayıtları arasında akıllı arama yapın
        </p>
      </div>

      <form onSubmit={handleSearch} style={{ position: "relative", marginBottom: 40 }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Problem veya hata kodunu buraya yazın..."
          style={{ width: "100%", padding: "18px 24px 18px 56px", background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 16, fontSize: 16, color: "var(--color-text-primary)", boxShadow: "0 4px 20px rgba(0,0,0,0.04)", transition: "all 0.2s" }}
        />
        <Search style={{ position: "absolute", left: 20, top: "50%", transform: "translateY(-50%)", color: "var(--color-text-muted)" }} size={22} />
        <button type="submit" disabled={loading} style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", padding: "10px 20px", background: "var(--color-accent)", color: "#fff", border: "none", borderRadius: 10, fontWeight: 600, fontSize: 14, cursor: "pointer", opacity: loading ? 0.6 : 1 }}>
          {loading ? "Aranıyor..." : "Ara"}
        </button>
      </form>

      {error && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "16px", background: "var(--color-danger-bg)", border: "1px solid rgba(224,80,80,0.2)", borderRadius: 12, marginBottom: 32 }}>
          <AlertCircle size={18} style={{ color: "var(--color-danger)" }} />
          <p style={{ color: "var(--color-danger)", fontSize: 14 }}>{error}</p>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {results.length > 0 ? (
          results.map((result, i) => {
            const expanded = expandedId === result.id;
            const isFetching = fetchingIds[result.id];
            const dbData = fullRecordsCache[result.id];
            const summaryData = dbData || (result.payload as any);

            return (
              <div key={result.id} className="animate-fade-in" style={{ border: "1px solid var(--color-border)", borderRadius: 14, overflow: "hidden", background: "var(--color-surface)", transition: "all 0.2s", animationDelay: `${i * 0.05}s`, borderColor: expanded ? "var(--color-accent)" : "var(--color-border)", boxShadow: expanded ? "0 8px 24px rgba(0,0,0,0.06)" : "none" }}>
                <button
                  onClick={() => toggleExpand(result.id)}
                  style={{ width: "100%", padding: "16px 20px", display: "flex", alignItems: "center", gap: 16, background: "none", border: "none", cursor: "pointer", textAlign: "left" }}
                >
                  <span style={{ fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--color-accent)", background: "var(--color-accent-subtle)", padding: "3px 8px", borderRadius: 5, textTransform: "uppercase" }}>
                    {summaryData.methodology || "—"}
                  </span>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <p style={{ fontSize: 15, fontWeight: 600, color: "var(--color-text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {summaryData.title || "Başlıksız Problem"}
                      </p>
                      <span style={{ fontSize: 9, color: "var(--color-text-muted)", background: "var(--color-surface-hover)", padding: "2px 6px", borderRadius: 4 }}>
                        Eşleşme: %{Math.round(result.score * 100)}
                      </span>
                    </div>
                    
                    {!expanded && (summaryData.problem_description || summaryData.description) && (
                      <p style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 6, opacity: 0.7, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {summaryData.problem_description || summaryData.description}
                      </p>
                    )}
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    {isFetching ? (
                      <Loader2 size={16} className="animate-spin" style={{ color: "var(--color-accent)" }} />
                    ) : (
                      <>
                        <StatusBadge status={summaryData.resolution_status || summaryData.status} />
                        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </>
                    )}
                  </div>
                </button>

                {expanded && dbData && (
                  <div className="animate-fade-in" style={{ borderTop: "1px solid var(--color-border)", padding: "32px 40px", background: "var(--color-surface-hover)" }}>
                    <UnifiedRecordDetail record={dbData} />
                    <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px dashed var(--color-border)", display: "flex", justifyContent: "space-between" }}>
                      <span style={{ fontSize: 10, color: "var(--color-text-muted)", fontFamily: "var(--font-mono)" }}>
                        Kayıt Doğrulandı: {result.id}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : !loading && query && (
          <div style={{ textAlign: "center", padding: "60px 24px", background: "var(--color-surface)", borderRadius: 16, border: "1px dashed var(--color-border)" }}>
            <p style={{ fontSize: 14, color: "var(--color-text-muted)", lineHeight: 1.5 }}>
              Arama kriterlerinize uygun benzer bir kayıt bulunamadı.<br/>
              Lütfen farklı anahtar kelimeler deneyin.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
