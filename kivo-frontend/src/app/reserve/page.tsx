"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  ShieldCheck,
  AlertOctagon,
  TrendingUp,
  Plus,
  Sparkles,
  PiggyBank,
  CheckCircle2,
  X
} from "lucide-react";

export default function ReservePage() {
  const { activeWorkspace } = useAuth();
  const [fund, setFund] = useState<any>(null);
  const [waste, setWaste] = useState<any>(null);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [depositAmount, setDepositAmount] = useState("");
  const [isDepositModalOpen, setIsDepositModalOpen] = useState(false);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [fundRes, wasteRes, accRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/emergency-fund`),
        api.get(`/workspaces/${activeWorkspace.id}/waste?month=${month}`),
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
      ]);

      setFund(fundRes.data);
      setWaste(wasteRes.data);
      setAccounts(accRes.data);
      if (accRes.data.length > 0) setSelectedAccountId(accRes.data[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace, month]);

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/emergency-fund/deposit`, {
        amount: parseFloat(depositAmount),
        account_id: selectedAccountId,
      });

      setIsDepositModalOpen(false);
      setDepositAmount("");
      loadData();
    } catch (err) {
      console.error("Erro ao depositar:", err);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Reserva de Emergência & Ralos</h1>
          <p className="text-xs text-slate-500">
            Proteção patrimonial com meta dinâmica de custos essenciais e combate a desperdícios
          </p>
        </div>

        {/* 1. Cofre da Reserva de Emergência */}
        <div className="p-6 md:p-8 rounded-3xl bg-linear-to-br from-emerald-900 to-slate-900 text-white shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <ShieldCheck className="w-7 h-7" />
              </div>
              <div>
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">Cofre Blindado</span>
                <h2 className="text-xl font-bold text-white">Status da Reserva de Emergência</h2>
              </div>
            </div>

            <button
              onClick={() => setIsDepositModalOpen(true)}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-extrabold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Aporte na Reserva</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
              <span className="text-xs text-slate-400 block">Saldo Acumulado</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">
                R$ {parseFloat(fund?.current_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
              <span className="text-xs text-slate-400 block">Meta Dinâmica ({fund?.target_months} meses)</span>
              <span className="text-2xl font-extrabold text-white font-mono">
                R$ {parseFloat(fund?.calculated_target_amount || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
              <span className="text-xs text-slate-400 block">Cobertura Atual</span>
              <span className="text-2xl font-extrabold text-emerald-400">
                {fund?.months_covered || 0} meses
              </span>
              <span className="text-[10px] text-slate-400 block">Classificação: {fund?.status_classification}</span>
            </div>
          </div>

          {/* Barra de Progresso */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Progresso da Meta</span>
              <span className="font-bold text-emerald-400">{fund?.progress_percentage || 0}%</span>
            </div>
            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                style={{ width: `${Math.min(100, fund?.progress_percentage || 0)}%` }}
                className="h-full bg-emerald-500 rounded-full transition-all"
              />
            </div>
          </div>
        </div>

        {/* 2. Relatório de Desperdícios / Ralos Financeiros */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs p-6 md:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center">
                <AlertOctagon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Relatório de Ralos Financeiros</h3>
                <p className="text-xs text-slate-400">Gastos classificados como supérfluos/desperdício no mês</p>
              </div>
            </div>

            <input
              type="month"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              className="px-3.5 py-1.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700"
            />
          </div>

          {/* Cards de Impacto */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-red-50 border border-red-100 text-red-900">
              <span className="text-xs font-bold text-red-600 block">Ralo do Mês:</span>
              <span className="text-2xl font-extrabold font-mono">
                R$ {parseFloat(waste?.total_waste_month || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-bold text-slate-500 block">Impacto Anualizado:</span>
              <span className="text-2xl font-extrabold text-slate-900 font-mono">
                R$ {parseFloat(waste?.total_waste_annualized || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-900">
              <span className="text-xs font-bold text-emerald-700 block">Potencial em 5 anos (10% a.a.):</span>
              <span className="text-2xl font-extrabold font-mono text-emerald-700">
                R$ {parseFloat(waste?.potential_patrimony_in_5_years || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          {/* Tabela de Ralos */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Data</th>
                  <th className="py-3 px-4">Descrição</th>
                  <th className="py-3 px-4">Categoria</th>
                  <th className="py-3 px-4 text-right">Valor Gasto</th>
                  <th className="py-3 px-4 text-right">Impacto Anual</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {waste?.waste_transactions?.map((item: any) => (
                  <tr key={item.transaction_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono text-slate-500">{item.transaction_date}</td>
                    <td className="py-3 px-4 font-bold text-slate-800">{item.description}</td>
                    <td className="py-3 px-4 text-slate-500">{item.category_name}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-red-600">
                      R$ {parseFloat(item.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-500">
                      R$ {parseFloat(item.annualized_impact).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal de Aporte */}
        {isDepositModalOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setIsDepositModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-lg font-bold text-slate-900">Aporte na Reserva de Emergência</h2>

              <form onSubmit={handleDeposit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Valor do Depósito (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(e.target.value)}
                    placeholder="1000.00"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold font-mono focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Origem do Dinheiro</label>
                  <select
                    value={selectedAccountId}
                    onChange={(e) => setSelectedAccountId(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                  >
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  Confirmar Aporte
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
