"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { TwoFactorModal } from "@/components/TwoFactorModal";
import { Loader2 } from "lucide-react";

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [is2FAModalOpen, setIs2FAModalOpen] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    // Carrega preferência do usuário do menu recolhido
    const saved = localStorage.getItem("kivo_sidebar_collapsed");
    if (saved !== null) {
      setIsCollapsed(saved === "true");
    }
  }, []);

  const handleToggleCollapse = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("kivo_sidebar_collapsed", String(next));
      return next;
    });
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-sm font-semibold text-slate-300">Carregando plataforma KIVO...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-slate-50 overflow-x-hidden">
      {/* Sidebar Desktop e Gaveta Mobile */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onOpen2FAModal={() => setIs2FAModalOpen(true)}
          onToggleMobile={() => setIsMobileOpen(!isMobileOpen)}
          isCollapsed={isCollapsed}
          onToggleCollapse={handleToggleCollapse}
        />
        <main className="p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto flex-1 min-w-0">
          {children}
        </main>
      </div>

      <TwoFactorModal
        isOpen={is2FAModalOpen}
        onClose={() => setIs2FAModalOpen(false)}
      />
    </div>
  );
};
