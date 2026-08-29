"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import {
  LayoutDashboard,
  CreditCard,
  ReceiptText,
  Users,
  TrendingDown,
  ShieldCheck,
  UploadCloud,
  CalendarClock,
  ChevronLeft,
  ChevronRight,
  X,
  PanelLeftClose,
  PanelLeftOpen
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { APP_VERSION, BUILD_ID, COMMIT_HASH } from "@/lib/version";

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed = false,
  onToggleCollapse,
  isMobileOpen = false,
  onCloseMobile,
}) => {
  const pathname = usePathname();
  const { activeWorkspace } = useAuth();

  const isFamily = activeWorkspace?.type === "family";

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Contas & Cartões", href: "/accounts", icon: CreditCard },
    { name: "Contas & Rendas Fixas", href: "/recurring", icon: CalendarClock },
    { name: "Extrato & Lançamentos", href: "/transactions", icon: ReceiptText },
    { name: "Casal & Família", href: "/couple", icon: Users, badge: isFamily ? "Rateio" : "Solo" },
    { name: "Dívidas & Simulador", href: "/debts", icon: TrendingDown },
    { name: "Reserva & Ralos", href: "/reserve", icon: ShieldCheck },
    { name: "Importar OFX/CSV", href: "/import", icon: UploadCloud },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 md:hidden animate-in fade-in transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:sticky top-0 z-50 md:z-30 h-screen bg-[#051329] text-slate-300 flex flex-col justify-between shrink-0 border-r border-slate-800 transition-all duration-300 ease-in-out ${
          isCollapsed ? "w-20" : "w-64"
        } ${
          isMobileOpen
            ? "translate-x-0 shadow-2xl"
            : "-translate-x-full md:translate-x-0"
        }`}
      >
        {/* Top Header & Brand */}
        <div>
          <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/80 gap-2">
            <Link
              href="/dashboard"
              onClick={onCloseMobile}
              className="flex items-center gap-3 overflow-hidden focus:outline-hidden"
            >
              {isCollapsed ? (
                <Image
                  src="/assets/kivo_icon.png"
                  alt="KIVO Icon"
                  width={36}
                  height={36}
                  className="h-8 w-8 object-contain mx-auto rounded-lg"
                />
              ) : (
                <Image
                  src="/assets/kivo_logo.png"
                  alt="KIVO Logo"
                  width={130}
                  height={40}
                  className="h-8 w-auto object-contain brightness-0 invert"
                  priority
                />
              )}
            </Link>

            {/* Desktop Collapse Toggle */}
            <button
              onClick={onToggleCollapse}
              className="hidden md:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors cursor-pointer"
              title={isCollapsed ? "Expandir menu lateral" : "Recolher menu lateral"}
            >
              {isCollapsed ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>

            {/* Mobile Close Button */}
            <button
              onClick={onCloseMobile}
              className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors cursor-pointer"
              title="Fechar menu"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Workspace Pill */}
          {!isCollapsed ? (
            <div className="px-4 py-3 animate-in fade-in duration-200">
              <div className="px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
                <span className="text-slate-500 font-medium block text-[11px]">Espaço Atual</span>
                <span className="text-emerald-400 font-bold truncate block">
                  {activeWorkspace?.name || "Carregando..."}
                </span>
              </div>
            </div>
          ) : (
            <div className="py-2 flex justify-center" title={`Espaço: ${activeWorkspace?.name}`}>
              <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-emerald-400 font-bold text-xs">
                {activeWorkspace?.name?.charAt(0) || "W"}
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="px-3 space-y-1 mt-2">
            {navigation.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onCloseMobile}
                  title={isCollapsed ? item.name : undefined}
                  className={`flex items-center ${
                    isCollapsed ? "justify-center px-2.5" : "justify-between px-3.5"
                  } py-2.5 rounded-xl text-sm font-medium transition-all group relative ${
                    isActive
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold"
                      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon
                      className={`w-5 h-5 shrink-0 ${
                        isActive ? "text-emerald-400" : "text-slate-400 group-hover:text-slate-200"
                      }`}
                    />
                    {!isCollapsed && <span className="truncate">{item.name}</span>}
                  </div>

                  {!isCollapsed && item.badge && (
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        isFamily
                          ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}

                  {/* Floating tooltip on collapsed mode */}
                  {isCollapsed && (
                    <div className="hidden md:group-hover:flex absolute left-full ml-2.5 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg shadow-xl border border-slate-700 whitespace-nowrap z-50 pointer-events-none animate-in fade-in slide-in-from-left-1 duration-150">
                      {item.name}
                      {item.badge && (
                        <span className="ml-1.5 text-[9px] uppercase px-1 rounded bg-slate-800 text-emerald-400 font-bold">
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer Status & Build */}
        <div className="p-3.5 border-t border-slate-800/80 text-[11px] text-slate-500 space-y-1">
          {!isCollapsed ? (
            <div className="animate-in fade-in duration-200 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-slate-300 font-semibold">KIVO v{APP_VERSION}</span>
                </div>
                <span className="text-emerald-400 font-bold text-[10px] uppercase">Online</span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-0.5">
                <span>Build: {BUILD_ID}</span>
                <span className="text-slate-400">#{COMMIT_HASH}</span>
              </div>
            </div>
          ) : (
            <div
              className="flex flex-col items-center justify-center py-1 gap-1"
              title={`KIVO v${APP_VERSION} • Build ${BUILD_ID} (#${COMMIT_HASH})`}
            >
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[9px] font-mono text-slate-500 font-bold">v{APP_VERSION}</span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
