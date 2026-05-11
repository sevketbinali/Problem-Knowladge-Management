"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { Eye, EyeOff, ArrowRight, AlertTriangle } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@pkm.local");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const err = await login(email, password);
    if (err) setError(err);
    setLoading(false);
  }

  const methods = ["5 Neden", "Ishikawa", "8D", "PDCA"];

  return (
    <div className="min-h-screen flex dot-grid relative overflow-hidden">
      {/* Ambient glow */}
      <div
        className="absolute pointer-events-none"
        style={{
          top: "30%",
          left: "35%",
          width: 480,
          height: 480,
          background: "radial-gradient(circle, rgba(223,128,80,0.06) 0%, transparent 70%)",
          transform: "translate(-50%, -50%)",
        }}
      />

      {/* Left decorative panel */}
      <div
        className="hidden lg:flex flex-col justify-between p-12 relative"
        style={{ width: 420, background: "var(--color-surface)", borderRight: "1px solid var(--color-border)" }}
      >
        {/* Top brand mark */}
        <div>
          <div
            className="inline-flex items-center gap-3 mb-12"
            style={{ borderBottom: "1px solid var(--color-border)", paddingBottom: 20 }}
          >
            <span
              style={{
                fontFamily: "var(--font-display)",
                fontSize: 28,
                fontWeight: 600,
                color: "var(--color-accent)",
                fontStyle: "italic",
                lineHeight: 1,
              }}
            >
              PKM
            </span>
            <span
              style={{
                width: 1,
                height: 24,
                background: "var(--color-border)",
                display: "inline-block",
              }}
            />
            <span
              style={{
                fontSize: 11,
                color: "var(--color-text-muted)",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                lineHeight: 1.4,
                display: "inline-block",
              }}
            >
              Problem<br />Bilgi Yönetimi
            </span>
          </div>

          {/* Headline */}
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 38,
              fontWeight: 500,
              lineHeight: 1.25,
              color: "var(--color-text-primary)",
              marginBottom: 20,
            }}
          >
            Problemleri çöz,<br />
            <span style={{ color: "var(--color-accent)", fontStyle: "italic" }}>bilgiyi koru.</span>
          </h1>
          <p
            style={{
              fontSize: 14,
              color: "var(--color-text-secondary)",
              lineHeight: 1.7,
              maxWidth: 300,
            }}
          >
            AI destekli kök neden analizi ile problemleri sistematik olarak çözün
            ve kurumsal hafızanızı güçlendirin.
          </p>
        </div>

        {/* Methodology badges */}
        <div>
          <p
            style={{
              fontSize: 10,
              color: "var(--color-text-muted)",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              marginBottom: 12,
            }}
          >
            Desteklenen metodolojiler
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {methods.map((m) => (
              <span
                key={m}
                style={{
                  padding: "5px 12px",
                  border: "1px solid var(--color-border-hover)",
                  borderRadius: 6,
                  fontSize: 12,
                  color: "var(--color-text-secondary)",
                  fontFamily: "var(--font-mono)",
                  background: "var(--color-surface-hover)",
                }}
              >
                {m}
              </span>
            ))}
          </div>
          <p
            style={{
              fontSize: 11,
              color: "var(--color-text-muted)",
              marginTop: 32,
            }}
          >
            v0.1.0 — AI destekli analiz
          </p>
        </div>

        {/* Decorative grid lines */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ opacity: 0.025 }}
          aria-hidden="true"
        >
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                top: 0,
                bottom: 0,
                left: `${(i + 1) * 12.5}%`,
                width: 1,
                background: "var(--color-text-primary)",
              }}
            />
          ))}
        </div>
      </div>

      {/* Right: Login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm animate-slide-up">
          {/* Mobile brand */}
          <div className="lg:hidden text-center mb-8">
            <span
              style={{
                fontFamily: "var(--font-display)",
                fontSize: 32,
                fontWeight: 600,
                color: "var(--color-accent)",
                fontStyle: "italic",
              }}
            >
              PKM
            </span>
            <p
              style={{
                fontSize: 13,
                color: "var(--color-text-muted)",
                marginTop: 4,
              }}
            >
              Problem Bilgi Yönetim Sistemi
            </p>
          </div>

          {/* Card */}
          <div
            className="card-amber"
            style={{ borderRadius: "0 0 16px 16px", padding: "32px 28px" }}
          >
            {/* Card header */}
            <div style={{ marginBottom: 28 }}>
              <h2
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: 22,
                  fontWeight: 500,
                  color: "var(--color-text-primary)",
                  marginBottom: 6,
                }}
              >
                Hesabınıza girin
              </h2>
              <p style={{ fontSize: 13, color: "var(--color-text-secondary)" }}>
                Devam etmek için kimlik bilgilerinizi girin
              </p>
            </div>

            <form onSubmit={handleSubmit}>
              {/* Email */}
              <div style={{ marginBottom: 16 }}>
                <label
                  htmlFor="email"
                  style={{
                    display: "block",
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--color-text-secondary)",
                    letterSpacing: "0.04em",
                    textTransform: "uppercase",
                    marginBottom: 8,
                  }}
                >
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-base"
                  placeholder="ornek@pkm.local"
                  required
                  style={{ paddingLeft: "1rem" }}
                />
              </div>

              {/* Password */}
              <div style={{ marginBottom: 24 }}>
                <label
                  htmlFor="password"
                  style={{
                    display: "block",
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--color-text-secondary)",
                    letterSpacing: "0.04em",
                    textTransform: "uppercase",
                    marginBottom: 8,
                  }}
                >
                  Şifre
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-base"
                    placeholder="••••••••"
                    required
                    style={{ paddingRight: "2.75rem" }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: "absolute",
                      right: 12,
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "var(--color-text-muted)",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
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
                    borderRadius: 8,
                    marginBottom: 16,
                  }}
                >
                  <AlertTriangle size={14} style={{ color: "var(--color-danger)", flexShrink: 0 }} />
                  <span style={{ fontSize: 13, color: "var(--color-danger)" }}>{error}</span>
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
                style={{ width: "100%" }}
              >
                {loading ? (
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
                ) : (
                  <>
                    Giriş Yap
                    <ArrowRight size={15} />
                  </>
                )}
              </button>
            </form>
          </div>

          <p
            style={{
              textAlign: "center",
              fontSize: 11,
              color: "var(--color-text-muted)",
              marginTop: 20,
            }}
          >
            AI destekli problem çözüm ve bilgi yönetim platformu
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
