"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import {
  ChevronDown,
  LogOut,
  Shield,
  ShieldCheck,
  User as UserIcon,
  Plus,
  Building2,
  Users,
  Menu,
  PanelLeftClose,
  PanelLeftOpen
} from "lucide-react";
import Link from "next/link";

interface HeaderProps {
  onOpen2FAModal?: () => void;
  onToggleMobile?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpen2FAModal,
  onToggleMobile,
  isCollapsed,
  onToggleCollapse,
}) => {
  const { user, activeWorkspace, setActiveWorkspaceId, logout } = useAuth();
  const [isWsMenuOpen, setIsWsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Left Area: Mobile Hamburger + Desktop Collapse + Workspace Selector */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Mobile Hamburger Button */}
        <button
          onClick={onToggleMobile}
          className="md:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
          title="Abrir menu lateral"
          aria-label="Abrir menu lateral"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Desktop Collapse Toggle in Header */}
        <button
          onClick={onToggleCollapse}
          className="hidden md:flex p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
          title={isCollapsed ? "Expandir menu lateral" : "Recolher menu lateral"}
        >
          {isCollapsed ? (
            <PanelLeftOpen className="w-4 h-4" />
          ) : (
            <PanelLeftClose className="w-4 h-4" />
          )}
        </button>

        {/* Seletor de Workspace */}
        <div className="relative">
          <button
            onClick={() => setIsWsMenuOpen(!isWsMenuOpen)}
            className="flex items-center gap-1.5 sm:gap-2.5 px-2.5 sm:px-3.5 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800 text-xs sm:text-sm font-semibold transition-colors max-w-[150px] sm:max-w-[240px]"
          >
            {activeWorkspace?.type === "family" ? (
              <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-600 shrink-0" />
            ) : (
              <Building2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-600 shrink-0" />
            )}
            <span className="truncate">{activeWorkspace?.name || "Espaço"}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          </button>

          {isWsMenuOpen && (
            <div className="absolute top-full left-0 mt-1.5 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl py-2 z-50 animate-in fade-in zoom-in-95">
              <div className="px-3 py-1.5 text-xs font-bold text-slate-400 uppercase tracking-wider">
                Seus Espaços
              </div>
              {user?.workspaces.map((ws) => (
                <button
                  key={ws.id}
                  onClick={() => {
                    setActiveWorkspaceId(ws.id);
                    setIsWsMenuOpen(false);
                  }}
                  className={`w-full text-left px-3.5 py-2 text-sm flex items-center justify-between hover:bg-slate-50 transition-colors ${
                    ws.id === activeWorkspace?.id ? "bg-emerald-50 text-emerald-800 font-bold" : "text-slate-700"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    {ws.type === "family" ? (
                      <Users className="w-4 h-4 text-purple-500" />
                    ) : (
                      <Building2 className="w-4 h-4 text-emerald-500" />
                    )}
                    <span className="truncate">{ws.name}</span>
                  </div>
                  <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-semibold">
                    {ws.type}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Area: Perfil & 2FA */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Status 2FA */}
        <button
          onClick={onOpen2FAModal}
          className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
            user?.mfa_enabled
              ? "bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100"
              : "bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100"
          }`}
          title="Clique para configurar autenticação em 2 etapas"
        >
          {user?.mfa_enabled ? (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span className="hidden sm:inline">2FA Ativo</span>
              <span className="sm:hidden">2FA</span>
            </>
          ) : (
            <>
              <Shield className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span className="hidden sm:inline">Ativar 2FA</span>
              <span className="sm:hidden">2FA</span>
            </>
          )}
        </button>

        {/* Menu do Usuário */}
        <div className="relative">
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="flex items-center gap-1.5 sm:gap-2.5 p-1 sm:pl-2 sm:pr-3 rounded-full hover:bg-slate-100 text-slate-700 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <span className="text-sm font-semibold hidden md:inline truncate max-w-[120px]">
              {user?.full_name}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
          </button>

          {isUserMenuOpen && (
            <div className="absolute top-full right-0 mt-1.5 w-52 bg-white border border-slate-200 rounded-2xl shadow-xl py-2 z-50 animate-in fade-in zoom-in-95">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-xs text-slate-400">Conectado como</p>
                <p className="text-sm font-bold text-slate-800 truncate">{user?.email}</p>
              </div>

              <button
                onClick={() => {
                  setIsUserMenuOpen(false);
                  if (onOpen2FAModal) onOpen2FAModal();
                }}
                className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
              >
                <ShieldCheck className="w-4 h-4 text-slate-400" />
                <span>Segurança 2FA</span>
              </button>

              <button
                onClick={logout}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 font-semibold"
              >
                <LogOut className="w-4 h-4 text-red-500" />
                <span>Sair da Conta</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
