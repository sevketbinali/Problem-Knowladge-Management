"use client";

import { AuthProvider, useAuth } from "@/lib/auth-context";
import LoginPage from "@/components/login-page";
import Dashboard from "@/components/dashboard";

function AppContent() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-3 border-[var(--color-accent)] border-t-transparent rounded-full animate-spin" />
          <p className="text-[var(--color-text-secondary)] text-sm">
            Yükleniyor...
          </p>
        </div>
      </div>
    );
  }

  if (!token) return <LoginPage />;
  return <Dashboard />;
}

export default function Home() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
