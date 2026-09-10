"use client";

import React from "react";
import { Search, StickyNote } from "lucide-react";

interface TransactionFiltersProps {
  search: string;
  setSearch: (search: string) => void;
  selectedAccountFilter: string;
  setSelectedAccountFilter: (account: string) => void;
  selectedTypeFilter: string;
  setSelectedTypeFilter: (type: string) => void;
  selectedStatusFilter: string;
  setSelectedStatusFilter: (status: string) => void;
  selectedTagFilter: string;
  setSelectedTagFilter: (tag: string) => void;
  showNotes: boolean;
  setShowNotes: (show: boolean) => void;
  accounts: any[];
  tags: any[];
}

export function TransactionFilters({
  search,
  setSearch,
  selectedAccountFilter,
  setSelectedAccountFilter,
  selectedTypeFilter,
  setSelectedTypeFilter,
  selectedStatusFilter,
  setSelectedStatusFilter,
  selectedTagFilter,
  setSelectedTagFilter,
  showNotes,
  setShowNotes,
  accounts,
  tags,
}: TransactionFiltersProps) {
  return (
    <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-wrap items-center gap-3">
      {/* Barra de Pesquisa */}
      <div className="relative flex-1 min-w-[200px]">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por descrição..."
          className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500"
        />
      </div>

      {/* Filtro por Conta / Cartão */}
      <select
        value={selectedAccountFilter}
        onChange={(e) => setSelectedAccountFilter(e.target.value)}
        className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 bg-white"
      >
        <option value="">Todas as Contas & Cartões</option>
        <optgroup label="Cartões de Crédito">
          {accounts
            .filter((a) => a.type === "credit_card")
            .map((a) => (
              <option key={a.id} value={a.id}>
                💳 {a.name}
              </option>
            ))}
        </optgroup>
        <optgroup label="Contas Bancárias & Carteiras">
          {accounts
            .filter((a) => a.type !== "credit_card")
            .map((a) => (
              <option key={a.id} value={a.id}>
                🏦 {a.name}
              </option>
            ))}
        </optgroup>
      </select>

      {/* Filtro por Tipo */}
      <select
        value={selectedTypeFilter}
        onChange={(e) => setSelectedTypeFilter(e.target.value)}
        className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700"
      >
        <option value="">Todos os Tipos</option>
        <option value="income">Receitas / Recebíveis</option>
        <option value="expense">Despesas</option>
        <option value="transfer">🔄 Transferências entre Contas</option>
        <option value="debt_payment">Dívidas</option>
      </select>

      {/* Filtro por Status */}
      <select
        value={selectedStatusFilter}
        onChange={(e) => setSelectedStatusFilter(e.target.value)}
        className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700"
      >
        <option value="">Todos os Status</option>
        <option value="paid">Efetivados / Realizados</option>
        <option value="pending">Pendentes (A Receber / A Pagar)</option>
      </select>

      {/* Filtro por Tag */}
      <select
        value={selectedTagFilter}
        onChange={(e) => setSelectedTagFilter(e.target.value)}
        className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700"
      >
        <option value="">Todas as Tags</option>
        {tags.map((t) => (
          <option key={t.id} value={t.id}>
            #{t.name}
          </option>
        ))}
      </select>

      {/* Botão de Exibir/Ocultar Anotações na Tabela */}
      <button
        type="button"
        onClick={() => setShowNotes(!showNotes)}
        className={`px-3 py-2 rounded-xl border text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
          showNotes
            ? "bg-amber-100 text-amber-900 border-amber-300 shadow-xs"
            : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-slate-800"
        }`}
        title={showNotes ? "Ocultar anotações na tabela (ver apenas ao passar o mouse)" : "Exibir anotações visíveis diretamente na tabela"}
      >
        <StickyNote className={`w-3.5 h-3.5 ${showNotes ? "text-amber-700" : "text-slate-400"}`} />
        <span>{showNotes ? "Anotações Visíveis" : "Anotações"}</span>
      </button>
    </div>
  );
}
