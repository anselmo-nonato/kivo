"use client";

import React from "react";
import { CreditCard, Calendar } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface CardsExecutiveSummaryProps {
  cardsSummary: any;
  creditCardsCount: number;
}

export function CardsExecutiveSummary({
  cardsSummary,
  creditCardsCount,
}: CardsExecutiveSummaryProps) {
  const usagePercentage = cardsSummary?.usage_percentage || 0;

  return (
    <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl border border-slate-800 space-y-6 relative overflow-hidden">
      {/* Efeito decorativo de fundo */}
      <div className="absolute -right-16 -bottom-16 w-64 h-64 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />
      <div className="absolute -left-16 -top-16 w-64 h-64 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-500 text-white flex items-center justify-center shadow-lg shadow-purple-500/30">
            <CreditCard className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-black text-white tracking-tight">Consolidado de Cartões & Limites</h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {creditCardsCount} {creditCardsCount === 1 ? "Cartão Ativo" : "Cartões Ativos"}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Visão macro de limites totais, saldo disponível consolidado e previsibilidade das próximas faturas
            </p>
          </div>
        </div>
      </div>

      {/* 4 Cards de Métricas Consolidadas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Limite Total */}
        <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Limite Total de Crédito
          </span>
          <div className="text-2xl font-black text-white tracking-tight">
            {formatCurrency(cardsSummary?.total_credit_limit)}
          </div>
          <span className="text-[11px] text-slate-400">Soma de todos os cartões</span>
        </div>

        {/* 2. Limite Disponível */}
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 space-y-1">
          <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block">
            Limite Disponível Livre
          </span>
          <div className="text-2xl font-black text-emerald-400 tracking-tight">
            {formatCurrency(cardsSummary?.total_available_limit)}
          </div>
          <span className="text-[11px] text-emerald-500/80">Liberado para novas compras</span>
        </div>

        {/* 3. Limite Utilizado / Fatura Atual */}
        <div className="p-4 rounded-2xl bg-purple-950/40 border border-purple-500/30 space-y-1">
          <span className="text-[11px] font-bold text-purple-300 uppercase tracking-wider block">
            Faturas / Limite Usado
          </span>
          <div className="text-2xl font-black text-purple-300 tracking-tight">
            {formatCurrency(cardsSummary?.total_used_limit)}
          </div>
          <span className="text-[11px] text-purple-400/80">Comprometido atualmente</span>
        </div>

        {/* 4. Taxa de Comprometimento */}
        <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Comprometimento</span>
            <span className="text-sm font-black text-white">{usagePercentage}%</span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                usagePercentage > 75
                  ? "bg-red-500"
                  : usagePercentage > 40
                  ? "bg-amber-500"
                  : "bg-emerald-500"
              }`}
              style={{ width: `${Math.min(100, usagePercentage)}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-400 block">
            {usagePercentage <= 30
              ? "✨ Nível de endividamento saudável"
              : usagePercentage <= 70
              ? "⚠️ Uso moderado de limite"
              : "🚨 Atenção: Limite alto comprometido"}
          </span>
        </div>
      </div>

      {/* PREVISIBILIDADE TOTAL DAS FATURAS (PRÓXIMOS 6 MESES) */}
      {cardsSummary?.monthly_forecast && cardsSummary.monthly_forecast.length > 0 && (
        <div className="pt-2 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-black uppercase tracking-wider text-slate-200">
                Previsibilidade de Faturas Futuras (Próximos Meses)
              </h3>
            </div>
            <span className="text-[11px] text-slate-400">Compras à vista e parcelamentos programados</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
            {cardsSummary.monthly_forecast.map((fc: any, idx: number) => {
              const isCurrent = idx === 0;
              const amt = parseFloat(fc.total_amount || 0);

              return (
                <div
                  key={fc.month}
                  className={`p-3.5 rounded-2xl border transition-all ${
                    isCurrent
                      ? "bg-purple-900/40 border-purple-500/50 shadow-inner"
                      : "bg-slate-800/40 border-slate-700/50 hover:border-slate-600"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-xs font-bold ${isCurrent ? "text-purple-300" : "text-slate-400"}`}>
                      {fc.month_name}
                    </span>
                    {isCurrent && (
                      <span className="text-[9px] font-black uppercase tracking-wider px-1.5 py-0.2 rounded bg-purple-500 text-white">
                        Atual
                      </span>
                    )}
                  </div>

                  <div className={`text-base font-black tracking-tight ${amt > 0 ? "text-white" : "text-slate-500"}`}>
                    {formatCurrency(amt)}
                  </div>

                  <div className="text-[10px] text-slate-400 mt-1">
                    {fc.transaction_count} {fc.transaction_count === 1 ? "lançamento" : "lançamentos"}
                  </div>

                  {/* Mini detalhe por cartão */}
                  {fc.by_card?.length > 0 && (
                    <div className="mt-2 pt-1.5 border-t border-slate-700/60 space-y-0.5">
                      {fc.by_card.map((bc: any) => (
                        <div key={bc.card_id} className="flex justify-between text-[9px] text-slate-300 truncate">
                          <span className="truncate max-w-[70px]">{bc.card_name}</span>
                          <span className="font-semibold text-purple-200">
                            R$ {parseFloat(bc.amount).toFixed(0)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
