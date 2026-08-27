"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import Link from "next/link";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  AlertTriangle,
  CheckCircle2,
  Plus,
  ArrowUpRight,
  ShieldCheck,
  CreditCard,
  PieChart as PieIcon,
  Sparkles
} from "lucide-react";

export default function DashboardPage() {
  const { activeWorkspace } = useAuth();
  const [summary, setSummary] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [dti, setDti] = useState<any>(null);
  const [radar, setRadar] = useState<any>(null);
  const [waste, setWaste] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const currentMonth = new Date().toISOString().slice(0, 7);

  const loadDashboardData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [sumRes, accRes, dtiRes, radarRes, wasteRes] = await Promise.allSettled([
        api.get(`/workspaces/${activeWorkspace.id}/summary?month=${currentMonth}`),
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}/debts/dti`),
        api.get(`/workspaces/${activeWorkspace.id}/radar?month=${currentMonth}`),
        api.get(`/workspaces/${activeWorkspace.id}/waste?month=${currentMonth}`),
      ]);

      if (sumRes.status === "fulfilled") setSummary(sumRes.value.data);
      if (accRes.status === "fulfilled") setAccounts(accRes.value.data);
      if (dtiRes.status === "fulfilled") setDti(dtiRes.value.data);
      if (radarRes.status === "fulfilled") setRadar(radarRes.value.data);
      if (wasteRes.status === "fulfilled") setWaste(wasteRes.value.data);
    } catch (err) {
      console.error("Erro ao carregar dados do dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [activeWorkspace]);

  // Cálculos consolidados
  const totalBalance = accounts.reduce((acc, a) => acc + parseFloat(a.current_balance || 0), 0);
  const totalIncome = parseFloat(summary?.total_income || 0);
  const totalExpense = parseFloat(summary?.total_expense || 0);
  const netSavings = parseFloat(summary?.net_savings || 0);
  const savingsRate = summary?.savings_rate_percentage || 0;

  const essentialVal = parseFloat(summary?.by_essentiality?.essential || 0);
  const lifestyleVal = parseFloat(summary?.by_essentiality?.lifestyle || 0);
  const wasteVal = parseFloat(summary?.by_essentiality?.waste || 0);

  const totalEssSum = essentialVal + lifestyleVal + wasteVal || 1;
  const essPct = Math.round((essentialVal / totalEssSum) * 100);
  const lifePct = Math.round((lifestyleVal / totalEssSum) * 100);
  const wastePct = Math.round((wasteVal / totalEssSum) * 100);

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header do Dashboard */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Visão Geral Financeira
            </h1>
            <p className="text-sm text-slate-500">
              Espaço: <span className="font-semibold text-emerald-600">{activeWorkspace?.name}</span> • Mês de Referência: <span className="font-semibold text-slate-700">{currentMonth}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/import"
              className="px-4 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-bold flex items-center gap-2 transition-colors"
            >
              <span>Importar Extrato</span>
            </Link>
            <Link
              href="/transactions"
              className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Novo Lançamento</span>
            </Link>
          </div>
        </div>

        {/* 4 Cards de Métricas Principais */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Saldo Consolidado */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Saldo em Bancos</span>
              <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <Wallet className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-slate-900">
              R$ {totalBalance.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-slate-500 font-medium">
              {accounts.length} conta{accounts.length === 1 ? "" : "s"} ativa{accounts.length === 1 ? "" : "s"}
            </p>
          </div>

          {/* Card 2: Entradas do Mês */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Entradas (Mês)</span>
              <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-slate-900">
              R$ {totalIncome.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-blue-600 font-medium flex items-center gap-1">
              <span>Receitas confirmadas</span>
            </p>
          </div>

          {/* Card 3: Saídas do Mês */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Saídas (Mês)</span>
              <div className="w-9 h-9 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
                <TrendingDown className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-slate-900">
              R$ {totalExpense.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-red-500 font-medium">
              Despesas e parcelas ativas
            </p>
          </div>

          {/* Card 4: Economia Líquida */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Poupança Líquida</span>
              <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <PiggyBank className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-emerald-600">
              R$ {netSavings.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs font-bold text-slate-700">
              Taxa de Poupança: <span className="text-emerald-600">{savingsRate}%</span>
            </p>
          </div>
        </div>

        {/* Linha 2: Essencialidade (50-30-20) e Termômetro DTI */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Distribuição por Essencialidade */}
          <div className="lg:col-span-2 p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <PieIcon className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-slate-900 text-lg">Distribuição dos Gastos (50-30-20)</h3>
              </div>
              <span className="text-xs text-slate-400 font-medium">Classificação Automática</span>
            </div>

            {/* Barra Visual Segmentada */}
            <div className="space-y-2">
              <div className="h-4 w-full rounded-full bg-slate-100 flex overflow-hidden">
                <div style={{ width: `${essPct}%` }} className="bg-emerald-500 h-full transition-all" title={`Essencial: ${essPct}%`} />
                <div style={{ width: `${lifePct}%` }} className="bg-blue-500 h-full transition-all" title={`Estilo de Vida: ${lifePct}%`} />
                <div style={{ width: `${wastePct}%` }} className="bg-red-500 h-full transition-all" title={`Ralos: ${wastePct}%`} />
              </div>

              {/* Legenda */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-100 text-xs">
                <div>
                  <div className="flex items-center gap-1.5 font-bold text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                    <span>Essencial ({essPct}%)</span>
                  </div>
                  <p className="font-extrabold text-slate-900 text-sm mt-0.5">
                    R$ {essentialVal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-[10px] text-slate-400">Meta: ~50%</span>
                </div>

                <div>
                  <div className="flex items-center gap-1.5 font-bold text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                    <span>Estilo de Vida ({lifePct}%)</span>
                  </div>
                  <p className="font-extrabold text-slate-900 text-sm mt-0.5">
                    R$ {lifestyleVal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-[10px] text-slate-400">Meta: ~30%</span>
                </div>

                <div>
                  <div className="flex items-center gap-1.5 font-bold text-red-600">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                    <span>Ralos / Desperdício ({wastePct}%)</span>
                  </div>
                  <p className="font-extrabold text-red-600 text-sm mt-0.5">
                    R$ {wasteVal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-[10px] text-red-400">Meta: 0%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Termômetro DTI (Endividamento) */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-900 text-lg">Termômetro DTI</h3>
                <span
                  className="px-2.5 py-1 rounded-full text-xs font-bold"
                  style={{
                    backgroundColor: `${dti?.status_color || "#10B981"}20`,
                    color: dti?.status_color || "#10B981",
                  }}
                >
                  {dti?.classification || "Calculando..."}
                </span>
              </div>

              <div className="text-center py-4">
                <div className="text-4xl font-extrabold text-slate-900">
                  {dti?.dti_percentage || 0}%
                </div>
                <p className="text-xs text-slate-400 mt-1">da sua renda mensal comprometida com parcelas de dívidas</p>
              </div>

              <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
                {dti?.actionable_advice || "Mantenha o endividamento abaixo de 20% para liberdade financeira."}
              </p>
            </div>

            <Link
              href="/debts"
              className="w-full py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Ver Simulador de Quitação</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Linha 3: Contas Bancárias Cadastradas */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-lg">Suas Contas e Cartões</h3>
            <Link href="/accounts" className="text-xs font-bold text-emerald-600 hover:underline">
              Gerenciar Contas →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {accounts.map((acc) => (
              <div key={acc.id} className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                  <span className="uppercase">{acc.type === "checking" ? "Conta Corrente" : acc.type === "credit_card" ? "Cartão de Crédito" : "Carteira"}</span>
                  <CreditCard className="w-4 h-4 text-slate-400" />
                </div>
                <h4 className="font-bold text-slate-900 text-base">{acc.name}</h4>
                <div className="text-xl font-extrabold text-slate-900">
                  R$ {parseFloat(acc.current_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </div>
                {acc.credit_limit && (
                  <p className="text-[11px] text-slate-400">
                    Limite: R$ {parseFloat(acc.credit_limit).toLocaleString("pt-BR", { minimumFractionDigits: 2 })} • Venc: dia {acc.due_day}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
