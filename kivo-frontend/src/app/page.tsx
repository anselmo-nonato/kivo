import Image from "next/image";
import { ArrowUpRight, ShieldCheck, PieChart, Users, KeyRound, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col justify-between p-6 md:p-12 max-w-6xl mx-auto">
      {/* Header */}
      <header className="flex justify-between items-center py-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <Image
            src="/assets/kivo_logo.png"
            alt="KIVO Logo"
            width={160}
            height={50}
            className="h-10 w-auto object-contain"
            priority
          />
        </div>
        <div className="flex items-center gap-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-emerald-800 bg-emerald-100 rounded-full">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Ambiente Local (Dev)
          </span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12 md:py-20 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Setup Inicial da Plataforma KIVO v0.1</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 tracking-tight">
          A chave da sua <span className="text-emerald-600">virada financeira</span>.
        </h1>

        <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto">
          Do diagnóstico e saída do vermelho à reserva de emergência e prosperidade financeira. Modo Solo e Modo Família 100% integrados.
        </p>

        {/* Status dos Serviços */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 max-w-4xl mx-auto text-left">
          <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
              <KeyRound className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">Backend REST API</h3>
            <p className="text-sm text-slate-500 mt-1">Python FastAPI com PostgreSQL e Redis.</p>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-medium text-emerald-600">
              <span>Porta 8000</span>
              <a href="http://localhost:8000/docs" target="_blank" className="hover:underline flex items-center gap-1">
                Swagger Docs <ArrowUpRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center mb-4">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">Segurança 2FA</h3>
            <p className="text-sm text-slate-500 mt-1">Argon2id, JWT e Google Authenticator (TOTP).</p>
            <div className="mt-4 pt-4 border-t border-slate-100 text-xs font-medium text-blue-600">
              RFC 6238 Nativo
            </div>
          </div>

          <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center mb-4">
              <Users className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">Multi-Tenancy</h3>
            <p className="text-sm text-slate-500 mt-1">Modo Solo e Família com Rateio Justo.</p>
            <div className="mt-4 pt-4 border-t border-slate-100 text-xs font-medium text-purple-600">
              Taxonomia 4D + Tags
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-xs text-slate-400 py-6 border-t border-slate-200">
        KIVO Finanças © 2026 — Todos os direitos reservados.
      </footer>
    </main>
  );
}
