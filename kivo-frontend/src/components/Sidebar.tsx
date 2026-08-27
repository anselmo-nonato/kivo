"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import {
  LayoutDashboard,
  CreditCard,
  ReceiptText,
  Tags,
  Users,
  TrendingDown,
  ShieldCheck,
  UploadCloud,
  ChevronRight
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { APP_VERSION, BUILD_ID, COMMIT_HASH } from "@/lib/version";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { activeWorkspace } = useAuth();

  const isFamily = activeWorkspace?.type === "family";

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Contas & Cartões", href: "/accounts", icon: CreditCard },
    { name: "Extrato & Lançamentos", href: "/transactions", icon: ReceiptText },
    { name: "Casal & Família", href: "/couple", icon: Users, badge: isFamily ? "Rateio" : "Solo" },
    { name: "Dívidas & Simulador", href: "/debts", icon: TrendingDown },
    { name: "Reserva & Ralos", href: "/reserve", icon: ShieldCheck },
    { name: "Importar OFX/CSV", href: "/import", icon: UploadCloud },
  ];

  return (
    <aside className="w-64 bg-[#051329] text-slate-300 flex flex-col justify-between shrink-0 h-screen sticky top-0 border-r border-slate-800">
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <Image
            src="/assets/kivo_logo.png"
            alt="KIVO Logo"
            width={130}
            height={40}
            className="h-8 w-auto object-contain brightness-0 invert"
          />
        </div>

        {/* Workspace Tag */}
        <div className="px-4 py-3">
          <div className="px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
            <span className="text-slate-500 font-medium block">Espaço Atual</span>
            <span className="text-emerald-400 font-bold truncate block">
              {activeWorkspace?.name || "Carregando..."}
            </span>
          </div>
        </div>

        {/* Links */}
        <nav className="px-3 space-y-1 mt-2">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className={`w-5 h-5 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
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
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Status & Build */}
      <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-500 space-y-1">
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
    </aside>
  );
};
