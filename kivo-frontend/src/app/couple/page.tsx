"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  Users,
  ArrowRightLeft,
  CheckCircle2,
  Heart,
  Scale,
  Sparkles,
  TrendingUp,
  AlertCircle
} from "lucide-react";

export default function CouplePage() {
  const { activeWorkspace } = useAuth();
  const [equalization, setEqualization] = useState<any>(null);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [loading, setLoading] = useState(true);
  const [settled, setSettled] = useState(false);

  const loadEqualization = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const res = await api.get(`/workspaces/${activeWorkspace.id}/equalization?month=${month}`);
      setEqualization(res.data);
    } catch (err) {
      console.error("Erro ao carregar equalização:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEqualization();
  }, [activeWorkspace, month]);

  const isFamily = activeWorkspace?.type === "family";

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold text-slate-900">Equalização do Casal & Rateio Justo</h1>
              <Heart className="w-5 h-5 text-rose-500 fill-rose-500" />
            </div>
            <p className="text-xs text-slate-500">
              Divisão proporcional de despesas compartilhadas da casa baseada na renda de cada um
            </p>
          </div>

          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="px-4 py-2 rounded-xl border border-slate-300 bg-white text-sm font-bold text-slate-700 shadow-xs"
          />
        </div>

        {!isFamily ? (
          <div className="p-8 rounded-3xl bg-white border border-slate-200 text-center max-w-xl mx-auto space-y-4 shadow-xs">
            <div className="w-14 h-14 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center mx-auto">
              <Users className="w-7 h-7" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">Você está no Modo Solo</h2>
            <p className="text-sm text-slate-500">
              O módulo de equalização calcula automaticamente a divisão proporcional das despesas da casa para casais. Selecione um espaço familiar no topo ou crie um novo espaço familiar para convidar seu cônjuge.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Card Principal de Liquidação / Acerto */}
            <div className="p-6 md:p-8 rounded-3xl bg-linear-to-br from-slate-900 to-slate-800 text-white shadow-xl space-y-4 relative overflow-hidden">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                <Scale className="w-4 h-4" />
                <span>Acerto de Contas do Mês</span>
              </div>

              <div className="text-2xl md:text-3xl font-extrabold text-white">
                {equalization?.settlement_suggestion || "Calculando rateio..."}
              </div>

              {equalization?.amount_to_transfer > 0 && (
                <div className="pt-2 flex flex-wrap items-center gap-4">
                  <div className="text-xl font-extrabold font-mono text-emerald-400">
                    Valor: R$ {parseFloat(equalization.amount_to_transfer).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </div>

                  <button
                    onClick={() => setSettled(true)}
                    className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-extrabold text-sm flex items-center gap-2 shadow-lg shadow-emerald-500/30 transition-colors cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{settled ? "Acerto Realizado!" : "Marcar como Transferido / Quitado"}</span>
                  </button>
                </div>
              )}
            </div>

            {/* Comparativo dos Membros */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {equalization?.members?.map((m: any) => (
                <div key={m.member_id} className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900 text-lg">{m.display_name}</h3>
                      <span className="text-xs text-slate-400">
                        Proporção de Renda: <strong className="text-emerald-600">{m.income_percentage}%</strong>
                      </span>
                    </div>
                    <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-700 font-extrabold flex items-center justify-center text-sm">
                      {m.income_percentage}%
                    </div>
                  </div>

                  <div className="space-y-2 pt-2 text-xs text-slate-600 border-t border-slate-100">
                    <div className="flex justify-between">
                      <span>Renda Declarada:</span>
                      <span className="font-bold text-slate-800">
                        R$ {parseFloat(m.declared_income).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Cota Justa das Despesas ({m.income_percentage}%):</span>
                      <span className="font-bold text-slate-800">
                        R$ {parseFloat(m.fair_share_amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Efetivamente Pago no Mês:</span>
                      <span className="font-bold text-slate-800">
                        R$ {parseFloat(m.total_shared_paid).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>

                  <div
                    className={`p-3.5 rounded-2xl text-xs font-bold flex items-center justify-between ${
                      m.balance >= 0
                        ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                        : "bg-rose-50 text-rose-800 border border-rose-200"
                    }`}
                  >
                    <span>{m.balance >= 0 ? "Tem a Receber:" : "Tem a Pagar:"}</span>
                    <span className="text-sm font-mono font-extrabold">
                      R$ {Math.abs(parseFloat(m.balance)).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
