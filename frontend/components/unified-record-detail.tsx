"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Target, Lightbulb, Tag, Calendar, Layers, Activity, User as UserIcon } from "lucide-react";
import { type ProblemRecord } from "@/lib/api";
import StatusBadge from "./status-badge";

interface UnifiedRecordDetailProps {
  record: ProblemRecord;
}

export default function UnifiedRecordDetail({ record }: UnifiedRecordDetailProps) {
  // Veri tutarlılığı için alan isimlerini normalize ediyoruz
  const description = record.problem_description || (record as any).description || (record as any).problem || "";
  const rootCause = record.root_cause || (record as any).payload?.root_cause || "";
  const lessonsLearned = record.lessons_learned || (record as any).payload?.lessons_learned || "";
  const status = record.resolution_status || (record as any).status || "";
  const createdBy = record.created_by || (record as any).payload?.created_by || "Bilinmiyor";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
      {/* Quick Info Bar - Theme Consistent */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, paddingBottom: 20, borderBottom: "1px solid var(--color-border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Layers size={14} style={{ color: "var(--color-text-muted)" }} />
          <span style={{ fontSize: 11, fontWeight: 700, color: "var(--color-accent)", background: "var(--color-accent-subtle)", padding: "4px 10px", borderRadius: 6, textTransform: "uppercase", letterSpacing: "0.02em" }}>
            {record.methodology || "—"}
          </span>
        </div>
        
        {record.department && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Activity size={14} style={{ color: "var(--color-text-muted)" }} />
            <span style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-primary)", background: "var(--color-surface-hover)", padding: "4px 10px", borderRadius: 6, border: "1px solid var(--color-border)" }}>
              {record.department}
            </span>
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <UserIcon size={14} style={{ color: "var(--color-text-muted)" }} />
          <span style={{ fontSize: 11, color: "var(--color-text-secondary)", fontWeight: 600 }}>
            {createdBy}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Calendar size={14} style={{ color: "var(--color-text-muted)" }} />
          <span style={{ fontSize: 11, color: "var(--color-text-secondary)", fontWeight: 500 }}>
            {record.created_at ? new Date(record.created_at).toLocaleDateString("tr-TR", { day: 'numeric', month: 'long', year: 'numeric' }) : "—"}
          </span>
        </div>

        {/* Unified Status Badge */}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center" }}>
          <StatusBadge status={status} />
        </div>
      </div>

      {/* Title Section */}
      <div style={{ marginBottom: 4 }}>
        <h3 style={{ 
          fontSize: 24, 
          fontWeight: 600, 
          color: "var(--color-text-primary)", 
          lineHeight: 1.3,
          fontFamily: "var(--font-display)"
        }}>
          {record.title}
        </h3>
      </div>

      {/* Problem Description Block */}
      {description && (
        <div style={{ 
          background: "var(--color-surface-hover)", 
          padding: "24px", 
          borderRadius: "16px", 
          border: "1px solid var(--color-border)",
          position: "relative",
          overflow: "hidden"
        }}>
          <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: "var(--color-accent)", opacity: 0.5 }} />
          
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <h4 style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-muted)", letterSpacing: "0.08em" }}>
              Problem Açıklaması
            </h4>
          </div>
          <p style={{ fontSize: 15, color: "var(--color-text-secondary)", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
            {description}
          </p>
        </div>
      )}

      {/* Content Grid */}
      <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
        {rootCause && (
          <div style={{ borderLeft: "2px solid var(--color-border)", paddingLeft: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
              <div style={{ padding: 6, background: "var(--color-surface-active)", borderRadius: 8 }}>
                <Target size={16} style={{ color: "var(--color-accent)" }} />
              </div>
              <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-primary)", letterSpacing: "0.05em" }}>
                Kök Neden
              </h4>
            </div>
            <div className="markdown-content" style={{ 
              fontSize: 15, color: "var(--color-text-secondary)", lineHeight: 1.7
            }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{rootCause}</ReactMarkdown>
            </div>
          </div>
        )}

        {lessonsLearned && (
          <div style={{ 
            padding: "28px",
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: "16px",
            boxShadow: "inset 0 0 20px rgba(0,0,0,0.2)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <div style={{ padding: 6, background: "var(--color-warning-bg)", borderRadius: 8 }}>
                <Lightbulb size={18} style={{ color: "var(--color-warning)" }} />
              </div>
              <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--color-text-primary)", letterSpacing: "0.05em" }}>
                Alınan Dersler
              </h4>
            </div>
            <div className="markdown-content" style={{
              fontSize: 15,
              color: "var(--color-text-primary)",
              lineHeight: 1.8
            }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{lessonsLearned}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      {/* Tags Section */}
      {record.tags && record.tags.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", paddingTop: 12, borderTop: "1px solid var(--color-border)" }}>
          <Tag size={14} style={{ color: "var(--color-text-muted)" }} />
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {record.tags.map(tag => (
              <span key={tag} style={{ 
                fontSize: 11, 
                fontWeight: 600, 
                color: "var(--color-text-secondary)", 
                background: "var(--color-surface-hover)", 
                padding: "4px 12px", 
                borderRadius: 20, 
                border: "1px solid var(--color-border)"
              }}>
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}

      <style jsx global>{`
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
          margin-top: 24px;
          margin-bottom: 12px;
          font-weight: 600;
          color: var(--color-text-primary);
          font-family: var(--font-display);
        }
        .markdown-content p { margin-bottom: 16px; }
        .markdown-content ul, .markdown-content ol {
          margin-bottom: 18px;
          padding-left: 24px;
          color: var(--color-text-secondary);
        }
        .markdown-content li { margin-bottom: 8px; }
        .markdown-content strong { font-weight: 700; color: var(--color-text-primary); }
      `}</style>
    </div>
  );
}
