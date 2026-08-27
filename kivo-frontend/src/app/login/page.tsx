"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ShieldCheck, KeyRound, ArrowRight, AlertCircle, Sparkles } from "lucide-react";

export default function LoginPage() {
  const { loginWithTokens } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Etapa 1: Login com Senha
  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/login", {
        email: email.trim(),
        password: password,
      });

      // Se exigir 2FA
      if (res.data.mfa_required) {
        setMfaToken(res.data.mfa_token);
      } else {
        // Login direto
        loginWithTokens(res.data.access_token, res.data.refresh_token, res.data.user);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "E-mail ou senha incorretos.");
    } finally {
      setLoading(false);
    }
  };

  // Etapa 2: Verificação do 2FA / Backup Code
  const handleVerifyMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/2fa/verify", {
        mfa_token: mfaToken,
        code: mfaCode.trim(),
      });

      loginWithTokens(res.data.access_token, res.data.refresh_token, res.data.user);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Código de autenticação ou de recuperação inválido.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl space-y-6">
        {/* Header com Logo */}
        <div className="text-center space-y-2">
          <Image
            src="/assets/kivo_logo.png"
            alt="KIVO"
            width={160}
            height={50}
            className="h-10 w-auto mx-auto object-contain"
            priority
          />
          <h1 className="text-2xl font-extrabold text-slate-900">
            {mfaToken ? "Verificação em 2 Etapas" : "Acesse sua conta"}
          </h1>
          <p className="text-xs text-slate-500">
            {mfaToken
              ? "Digite o código do Google Authenticator ou código de backup"
              : "Entre para gerenciar suas finanças solo e em família"}
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Formulário 1: E-mail e Senha */}
        {!mfaToken ? (
          <form onSubmit={handlePasswordLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">E-mail</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu.email@exemplo.com"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-hidden focus:ring-2 focus:ring-emerald-500 font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Senha</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-hidden focus:ring-2 focus:ring-emerald-500 font-medium"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              {loading ? "Entrando..." : "Entrar no KIVO"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          /* Formulário 2: 2FA TOTP */
          <form onSubmit={handleVerifyMfa} className="space-y-4">
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
              <ShieldCheck className="w-6 h-6 text-emerald-600 shrink-0" />
              <span>Sua conta está protegida por 2FA. Forneça o código para continuar.</span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Código de 6 Dígitos ou Código de Backup:
              </label>
              <input
                type="text"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                placeholder="000000 ou XXXXX-XXXXX"
                required
                autoFocus
                className="w-full text-center text-xl font-mono py-3 rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500 font-bold"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !mfaCode}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              {loading ? "Validando..." : "Validar e Acessar"}
              <ShieldCheck className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => setMfaToken(null)}
              className="w-full text-center text-xs text-slate-500 hover:underline pt-2"
            >
              Voltar ao login com senha
            </button>
          </form>
        )}

        <div className="text-center pt-2 border-t border-slate-100 text-xs text-slate-500">
          Ainda não tem conta?{" "}
          <Link href="/register" className="text-emerald-600 font-bold hover:underline">
            Criar conta gratuitamente
          </Link>
        </div>
      </div>
    </div>
  );
}
