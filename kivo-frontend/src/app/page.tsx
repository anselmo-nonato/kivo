"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, ShieldCheck, PieChart, Users, Sparkles, Scale } from "lucide-react";

export default function LandingHomePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.push("/dashboard");
    }
  }, [user, isLoading, router]);

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 h-20 flex items-center justify-between border-b border-slate-900">
        <Image
          src="/assets/kivo_logo.png"
          alt="KIVO"
          width={140}
          height={45}
          className="h-9 w-auto brightness-0 invert object-contain"
          priority
        />

        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-bold text-slate-300 hover:text-white transition-colors"
          >
            Entrar
          </Link>
          <Link
            href="/register"
            className="px-5 py-2.5 rounded-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-sm font-extrabold shadow-lg shadow-emerald-500/20 transition-all"
          >
            Criar Conta Grátis
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto w-full px-6 py-20 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          <span>A Chave da sua Virada Financeira</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white max-w-4xl mx-auto leading-tight">
          O controle financeiro inteligente para você e sua família.
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-medium">
          Taxonomia 4D, rateio justo de casal baseado na renda, motor de quitação de dívidas (Avalanche) e conciliação bancária de todos os seus bancos.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-base shadow-xl shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all"
          >
            <span>Acessar o Painel KIVO</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 rounded-2xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-white font-bold text-base transition-colors"
          >
            Fazer Login
          </Link>
        </div>

        {/* 3 Pilares */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 text-left">
          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
              <Scale className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-lg">Equalização do Casal</h3>
            <p className="text-xs text-slate-400">
              Divisão proporcional justa das contas conjuntas de acordo com o salário de cada um, eliminando discussões financeiras.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <PieChart className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-lg">Regra 50-30-20 & Ralos</h3>
            <p className="text-xs text-slate-400">
              Classificação automática de gastos essenciais, estilo de vida e identificação de ralos de dinheiro com impacto anualizado.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-lg">Segurança Máxima (2FA)</h3>
            <p className="text-xs text-slate-400">
              Proteção de nível bancário com autenticação em duas etapas via Google Authenticator (RFC 6238 TOTP) e códigos de backup.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full px-6 py-8 border-t border-slate-900 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span>© 2026 KIVO — Todos os direitos reservados.</span>
        <div className="flex items-center gap-6">
          <Link href="/login" className="hover:text-white">Login</Link>
          <Link href="/register" className="hover:text-white">Cadastro</Link>
          <a href="http://localhost:8000/docs" target="_blank" className="hover:text-white">API Swagger</a>
        </div>
      </footer>
    </div>
  );
}
