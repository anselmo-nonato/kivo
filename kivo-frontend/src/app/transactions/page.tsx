"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { cleanUserNotes } from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  ArrowLeftRight,
} from "lucide-react";
import { TransactionPeriodNavigator } from "@/components/transactions/TransactionPeriodNavigator";
import { TransactionFilters } from "@/components/transactions/TransactionFilters";
import { TransactionTable } from "@/components/transactions/TransactionTable";
import { TransactionModal } from "@/components/transactions/TransactionModal";

export default function TransactionsPage() {
  const { activeWorkspace } = useAuth();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtros de Período
  const now = new Date();
  const currentMonthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

  const [periodMode, setPeriodMode] = useState<"month" | "all" | "custom">("month");
  const [selectedMonth, setSelectedMonth] = useState<string>(currentMonthStr);
  const [customStartDate, setCustomStartDate] = useState<string>("");
  const [customEndDate, setCustomEndDate] = useState<string>("");

  // Filtros Gerais
  const [search, setSearch] = useState("");
  const [selectedAccountFilter, setSelectedAccountFilter] = useState("");
  const [selectedTagFilter, setSelectedTagFilter] = useState("");
  const [selectedTypeFilter, setSelectedTypeFilter] = useState("");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState("");
  const [showNotes, setShowNotes] = useState(false);

  // Estado do Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [modalInitialType, setModalInitialType] = useState<"expense" | "income" | "transfer">("expense");
  const [editingTransaction, setEditingTransaction] = useState<any | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const accParam = params.get("account_id");
      if (accParam) {
        setSelectedAccountFilter(accParam);
      }
    }
  }, []);

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [txRes, accRes, catRes, ccRes, tagRes, wsRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/transactions`),
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}/categories`),
        api.get(`/workspaces/${activeWorkspace.id}/cost-centers`),
        api.get(`/workspaces/${activeWorkspace.id}/tags`),
        api.get(`/workspaces/${activeWorkspace.id}`),
      ]);

      setTransactions(txRes.data);
      setAccounts(accRes.data);
      setCategories(catRes.data);
      setCostCenters(ccRes.data);
      setTags(tagRes.data);
      setMembers(wsRes.data.members || []);
    } catch (err) {
      console.error("Erro ao carregar dados:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  const handleOpenCreate = (type: "expense" | "income" | "transfer" = "expense") => {
    setIsEditMode(false);
    setEditingTransaction(null);
    setModalInitialType(type);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (tx: any) => {
    setIsEditMode(true);
    setEditingTransaction(tx);
    setIsModalOpen(true);
  };

  const handleDeleteTransaction = async (txId: string) => {
    if (
      !confirm(
        "Tem certeza que deseja excluir esta transação? Caso seja uma transferência, o espelho vinculado também será removido."
      )
    )
      return;
    try {
      await api.delete(`/workspaces/${activeWorkspace?.id}/transactions/${txId}`);
      loadData();
    } catch (err) {
      console.error("Erro ao excluir transação:", err);
    }
  };

  const handleConfirmTransaction = async (txId: string) => {
    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/transactions/${txId}/confirm`);
      loadData();
    } catch (err) {
      console.error("Erro ao confirmar lançamento:", err);
    }
  };

  // Filtragem
  const filteredTransactions = transactions.filter((tx) => {
    const cleanNotesText = cleanUserNotes(tx.notes);
    const matchSearch =
      tx.description.toLowerCase().includes(search.toLowerCase()) ||
      cleanNotesText.toLowerCase().includes(search.toLowerCase()) ||
      (tx.account_name && tx.account_name.toLowerCase().includes(search.toLowerCase()));
    const matchType = !selectedTypeFilter || tx.type === selectedTypeFilter;
    const matchStatus = !selectedStatusFilter || tx.status === selectedStatusFilter;
    const matchTag = !selectedTagFilter || tx.tags?.some((t: any) => t.id === selectedTagFilter);
    const matchAccount = !selectedAccountFilter || tx.account_id === selectedAccountFilter;

    let matchPeriod = true;
    if (periodMode === "month" && selectedMonth) {
      matchPeriod = tx.transaction_date.startsWith(selectedMonth);
    } else if (periodMode === "custom") {
      if (customStartDate && tx.transaction_date < customStartDate) matchPeriod = false;
      if (customEndDate && tx.transaction_date > customEndDate) matchPeriod = false;
    }

    return matchSearch && matchType && matchStatus && matchTag && matchAccount && matchPeriod;
  });

  // Totais do Período Filtrado
  const periodTotalIncome = filteredTransactions
    .filter((tx) => tx.type === "income")
    .reduce((acc, tx) => acc + parseFloat(tx.amount || 0), 0);

  const periodTotalExpense = filteredTransactions
    .filter((tx) => tx.type === "expense" || tx.type === "debt_payment")
    .reduce((acc, tx) => acc + parseFloat(tx.amount || 0), 0);

  const periodNetBalance = periodTotalIncome - periodTotalExpense;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Extrato, Recebíveis & Despesas</h1>
            <p className="text-xs text-slate-500">
              Histórico de lançamentos, transferências entre contas, receitas avulsas e filtros
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleOpenCreate("transfer")}
              className="px-3.5 py-2.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold text-xs shadow-xs flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <ArrowLeftRight className="w-4 h-4 text-indigo-600" />
              <span>🔄 Transferência</span>
            </button>
            <button
              onClick={() => handleOpenCreate("income")}
              className="px-3.5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <TrendingUp className="w-4 h-4" />
              <span>+ Receita</span>
            </button>
            <button
              onClick={() => handleOpenCreate("expense")}
              className="px-3.5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <TrendingDown className="w-4 h-4 text-red-400" />
              <span>+ Despesa</span>
            </button>
          </div>
        </div>

        {/* Navegador e Seletor de Período */}
        <TransactionPeriodNavigator
          periodMode={periodMode}
          setPeriodMode={setPeriodMode}
          selectedMonth={selectedMonth}
          setSelectedMonth={setSelectedMonth}
          currentMonthStr={currentMonthStr}
          customStartDate={customStartDate}
          setCustomStartDate={setCustomStartDate}
          customEndDate={customEndDate}
          setCustomEndDate={setCustomEndDate}
          periodTotalIncome={periodTotalIncome}
          periodTotalExpense={periodTotalExpense}
          periodNetBalance={periodNetBalance}
          filteredCount={filteredTransactions.length}
        />

        {/* Filtros */}
        <TransactionFilters
          search={search}
          setSearch={setSearch}
          selectedAccountFilter={selectedAccountFilter}
          setSelectedAccountFilter={setSelectedAccountFilter}
          selectedTypeFilter={selectedTypeFilter}
          setSelectedTypeFilter={setSelectedTypeFilter}
          selectedStatusFilter={selectedStatusFilter}
          setSelectedStatusFilter={setSelectedStatusFilter}
          selectedTagFilter={selectedTagFilter}
          setSelectedTagFilter={setSelectedTagFilter}
          showNotes={showNotes}
          setShowNotes={setShowNotes}
          accounts={accounts}
          tags={tags}
        />

        {/* Tabela de Lançamentos */}
        <TransactionTable
          transactions={filteredTransactions}
          accounts={accounts}
          showNotes={showNotes}
          onOpenEdit={handleOpenEdit}
          onDelete={handleDeleteTransaction}
          onConfirm={handleConfirmTransaction}
        />

        {/* Modal de Criação / Edição */}
        {activeWorkspace && (
          <TransactionModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            isEditMode={isEditMode}
            editingTransaction={editingTransaction}
            initialType={modalInitialType}
            accounts={accounts}
            categories={categories}
            costCenters={costCenters}
            tags={tags}
            members={members}
            activeWorkspaceId={activeWorkspace.id}
            onSuccess={loadData}
          />
        )}
      </div>
    </AppLayout>
  );
}
