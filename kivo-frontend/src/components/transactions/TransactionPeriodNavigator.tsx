"use client";

import React from "react";
import { Calendar, ChevronLeft, ChevronRight, TrendingUp, TrendingDown, Layers } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface TransactionPeriodNavigatorProps {
  periodMode: "month" | "all" | "custom";
  setPeriodMode: (mode: "month" | "all" | "custom") => void;
  selectedMonth: string;
  setSelectedMonth: (month: string) => void;
  currentMonthStr: string;
  customStartDate: string;
  setCustomStartDate: (date: string) => void;
  customEndDate: string;
  setCustomEndDate: (date: string) => void;
  periodTotalIncome: number;
  periodTotalExpense: number;
  periodNetBalance: number;
  filteredCount: number;
}

const MONTHS = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
];

export function TransactionPeriodNavigator({
  periodMode,
  setPeriodMode,
  selectedMonth,
  setSelectedMonth,
  currentMonthStr,
  customStartDate,
  setCustomStartDate,
  customEndDate,
  setCustomEndDate,
  periodTotalIncome,
  periodTotalExpense,
  periodNetBalance,
  filteredCount,
}: TransactionPeriodNavigatorProps) {
  const handlePrevMonth = () => {
    const [year, month] = (selectedMonth || currentMonthStr).split("-").map(Number);
    const prevDate = new Date(year, month - 2, 1);
    const prevStr = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, "0")}`;
    setSelectedMonth(prevStr);
    setPeriodMode("month");
  };

  const handleNextMonth = () => {
    const [year, month] = (selectedMonth || currentMonthStr).split("-").map(Number);
    const nextDate = new Date(year, month, 1);
    const nextStr = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, "0")}`;
    setSelectedMonth(nextStr);
    setPeriodMode("month");
  };

  const handleCurrentMonth = () => {
    setSelectedMonth(currentMonthStr);
    setPeriodMode("month");
  };

  const formatSelectedMonthName = (monthStr: string) => {
    if (!monthStr) return "Mês Selecionado";
    const [year, month] = monthStr.split("-").map(Number);
    return `${MONTHS[month - 1]} de ${year}`;
  };

  return (
    <div className="p-3.5 md:p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Navegador de Mês */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            type="button"
            onClick={handlePrevMonth}
            className="p-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
            title="Mês Anterior"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <div className="relative flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 cursor-pointer group">
            <Calendar className="w-4 h-4 text-emerald-600" />
            <span className="font-bold text-slate-800 text-xs sm:text-sm whitespace-nowrap">
              {periodMode === "month"
                ? formatSelectedMonthName(selectedMonth)
                : periodMode === "all"
                ? "Todo o Histórico"
                : "Período Personalizado"}
            </span>
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => {
                if (e.target.value) {
                  setSelectedMonth(e.target.value);
                  setPeriodMode("month");
                }
              }}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              title="Clique para escolher mês e ano"
            />
          </div>

          <button
            type="button"
            onClick={handleNextMonth}
            className="p-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
            title="Próximo Mês"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={handleCurrentMonth}
            className={`px-2.5 py-1.5 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${
              selectedMonth === currentMonthStr && periodMode === "month"
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
            }`}
          >
            Mês Atual
          </button>
        </div>

        {/* Modos de Visualização de Período */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-xl self-start sm:self-auto">
          <button
            type="button"
            onClick={() => {
              setPeriodMode("month");
              if (!selectedMonth) setSelectedMonth(currentMonthStr);
            }}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              periodMode === "month"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            Por Mês
          </button>
          <button
            type="button"
            onClick={() => setPeriodMode("all")}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              periodMode === "all"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            Todo o Histórico
          </button>
          <button
            type="button"
            onClick={() => setPeriodMode("custom")}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              periodMode === "custom"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            Personalizado
          </button>
        </div>
      </div>

      {/* Seletor de Datas Personalizado */}
      {periodMode === "custom" && (
        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 flex flex-wrap items-center gap-3 animate-in fade-in">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-bold text-slate-600">De:</span>
            <input
              type="date"
              value={customStartDate}
              onChange={(e) => setCustomStartDate(e.target.value)}
              className="px-2.5 py-1 bg-white rounded-lg border border-slate-300 text-xs font-medium text-slate-800"
            />
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="font-bold text-slate-600">Até:</span>
            <input
              type="date"
              value={customEndDate}
              onChange={(e) => setCustomEndDate(e.target.value)}
              className="px-2.5 py-1 bg-white rounded-lg border border-slate-300 text-xs font-medium text-slate-800"
            />
          </div>
          {(customStartDate || customEndDate) && (
            <button
              type="button"
              onClick={() => {
                setCustomStartDate("");
                setCustomEndDate("");
              }}
              className="text-xs text-red-500 hover:text-red-700 font-bold ml-auto cursor-pointer"
            >
              Limpar Datas
            </button>
          )}
        </div>
      )}

      {/* 4 Cards de Totais do Período Filtrado */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 pt-2 border-t border-slate-100">
        {/* 1. Entradas */}
        <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-100/80 flex items-center justify-between gap-2">
          <div>
            <span className="text-[10px] uppercase font-bold text-emerald-700 block">Entradas / Receitas</span>
            <div className="text-base sm:text-lg font-extrabold text-emerald-600 tracking-tight">
              + {formatCurrency(periodTotalIncome)}
            </div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 hidden sm:flex items-center justify-center shrink-0">
            <TrendingUp className="w-4 h-4" />
          </div>
        </div>

        {/* 2. Saídas */}
        <div className="p-3 rounded-xl bg-red-50/60 border border-red-100/80 flex items-center justify-between gap-2">
          <div>
            <span className="text-[10px] uppercase font-bold text-red-700 block">Saídas / Despesas</span>
            <div className="text-base sm:text-lg font-extrabold text-red-600 tracking-tight">
              - {formatCurrency(periodTotalExpense)}
            </div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-red-100 text-red-700 hidden sm:flex items-center justify-center shrink-0">
            <TrendingDown className="w-4 h-4" />
          </div>
        </div>

        {/* 3. Saldo Líquido do Período */}
        <div
          className={`p-3 rounded-xl border flex items-center justify-between gap-2 ${
            periodNetBalance >= 0 ? "bg-slate-50 border-slate-200" : "bg-amber-50/60 border-amber-200"
          }`}
        >
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Resultado do Período</span>
            <div
              className={`text-base sm:text-lg font-extrabold tracking-tight ${
                periodNetBalance >= 0 ? "text-slate-900" : "text-amber-700"
              }`}
            >
              {periodNetBalance >= 0 ? "+" : "-"} {formatCurrency(Math.abs(periodNetBalance))}
            </div>
          </div>
        </div>

        {/* 4. Total de Lançamentos */}
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-2">
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Lançamentos</span>
            <div className="text-base sm:text-lg font-extrabold text-slate-800 tracking-tight">
              {filteredCount} {filteredCount === 1 ? "item" : "itens"}
            </div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-slate-200/70 text-slate-600 hidden sm:flex items-center justify-center shrink-0">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
}
