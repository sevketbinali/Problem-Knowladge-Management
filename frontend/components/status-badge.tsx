"use client";

interface StatusBadgeProps {
  status?: string;
  className?: string;
}

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  const s = (status || "").toLowerCase();
  
  // Translation and Logic Unified
  let label = status || "Durum Belirtilmedi";
  let colors = { color: "var(--color-info)", background: "var(--color-info-bg)", borderColor: "rgba(69, 170, 200, 0.2)" };

  if (s === "resolved" || s === "finalized" || s === "tamamlandı") {
    label = "Tamamlandı";
    colors = { color: "var(--color-success)", background: "var(--color-success-bg)", borderColor: "rgba(78, 201, 138, 0.2)" };
  } else if (s === "pending" || s === "beklemede") {
    label = "Beklemede";
    colors = { color: "var(--color-warning)", background: "var(--color-warning-bg)", borderColor: "rgba(232, 194, 64, 0.2)" };
  } else if (s === "in_progress" || s === "devam ediyor") {
    label = "Devam Ediyor";
    colors = { color: "var(--color-info)", background: "var(--color-info-bg)", borderColor: "rgba(69, 170, 200, 0.2)" };
  }

  return (
    <span 
      className={className}
      style={{ 
        fontSize: 10, 
        fontWeight: 800, 
        padding: "4px 12px", 
        borderRadius: 7, 
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        border: "1px solid transparent",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        ...colors
      }}
    >
      {label}
    </span>
  );
}
