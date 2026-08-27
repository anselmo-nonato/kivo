"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  ReceiptText,
  Plus,
  Filter,
  Search,
  Calendar,
  Tag as TagIcon,
  CreditCard,
  Building2,
  X,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Pencil,
  Trash2
} from "lucide-react";

export default function TransactionsPage() {
  const { activeWorkspace } = useAuth();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtros
  const [search, setSearch] = useState("");
  const [selectedTagFilter, setSelectedTagFilter] = useState("");
  const [selectedTypeFilter, setSelectedTypeFilter] = useState("");

  // Modal Novo / Editar Lançamento
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedTxId, setSelectedTxId] = useState<string | null>(null);

  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [type, setType] = useState("expense");
  const [essentiality, setEssentiality] = useState("essential");
  const [transactionDate, setTransactionDate] = useState(new Date().toISOString().slice(0, 10));
  const [accountId, setAccountId] = useState("");
  const [paidByMemberId, setPaidByMemberId] = useState("");
  const [costCenterId, setCostCenterId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [totalInstallments, setTotalInstallments] = useState("1");
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const [newTagName, setNewTagName] = useState("");
  const [error, setError] = useState("");

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

      if (accRes.data.length > 0) setAccountId(accRes.data[0].id);
      if (wsRes.data.members?.length > 0) setPaidByMemberId(wsRes.data.members[0].id);
      if (ccRes.data.length > 0) setCostCenterId(ccRes.data[0].id);
      if (catRes.data.length > 0) setCategoryId(catRes.data[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  // Criação rápida de Tag inline
  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    try {
      const res = await api.post(`/workspaces/${activeWorkspace?.id}/tags`, {
        name: newTagName.trim().replace("#", ""),
        color: "#3B82F6",
      });
      setTags([...tags, res.data]);
      setSelectedTagIds([...selectedTagIds, res.data.id]);
      setNewTagName("");
    } catch (err) {
      console.error("Erro ao criar tag:", err);
    }
  };

  const handleOpenCreate = () => {
    setIsEditMode(false);
    setSelectedTxId(null);
    setDescription("");
    setAmount("");
    setTotalInstallments("1");
    setSelectedTagIds([]);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (tx: any) => {
    setIsEditMode(true);
    setSelectedTxId(tx.id);
    setDescription(tx.description);
    setAmount(tx.amount);
    setType(tx.type);
    setEssentiality(tx.essentiality);
    setTransactionDate(tx.transaction_date);
    setAccountId(tx.account_id);
    setPaidByMemberId(tx.paid_by_member_id);
    setCostCenterId(tx.cost_center_id);
    setCategoryId(tx.category_id);
    setSelectedTagIds(tx.tags?.map((t: any) => t.id) || []);
    setIsModalOpen(true);
  };

  const handleDeleteTransaction = async (txId: string) => {
    if (!confirm("Tem certeza que deseja excluir esta transação?")) return;
    try {
      await api.delete(`/workspaces/${activeWorkspace?.id}/transactions/${txId}`);
      loadData();
    } catch (err) {
      console.error("Erro ao excluir transação:", err);
    }
  };

  const handleSaveTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      if (isEditMode && selectedTxId) {
        await api.put(`/workspaces/${activeWorkspace?.id}/transactions/${selectedTxId}`, {
          description: description.trim(),
          amount: parseFloat(amount),
          type,
          essentiality,
          transaction_date: transactionDate,
          account_id: accountId,
          paid_by_member_id: paidByMemberId,
          cost_center_id: costCenterId,
          category_id: categoryId,
          tag_ids: selectedTagIds,
        });
      } else {
        await api.post(`/workspaces/${activeWorkspace?.id}/transactions`, {
          description: description.trim(),
          amount: parseFloat(amount),
          type,
          essentiality,
          transaction_date: transactionDate,
          account_id: accountId,
          paid_by_member_id: paidByMemberId,
          cost_center_id: costCenterId,
          category_id: categoryId,
          total_installments: parseInt(totalInstallments) || 1,
          tag_ids: selectedTagIds,
        });
      }

      setIsModalOpen(false);
      setDescription("");
      setAmount("");
      setTotalInstallments("1");
      setSelectedTagIds([]);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar lançamento.");
    }
  };

  // Filtragem
  const filteredTransactions = transactions.filter((tx) => {
    const matchSearch = tx.description.toLowerCase().includes(search.toLowerCase());
    const matchType = !selectedTypeFilter || tx.type === selectedTypeFilter;
    const matchTag = !selectedTagFilter || tx.tags?.some((t: any) => t.id === selectedTagFilter);
    return matchSearch && matchType && matchTag;
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Extrato & Lançamentos</h1>
            <p className="text-xs text-slate-500">Histórico detalhado com filtros, edição e parcelamento</p>
          </div>
          <button
            onClick={handleOpenCreate}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Novo Lançamento</span>
          </button>
        </div>

        {/* Barra de Filtros */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-wrap items-center gap-3">
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

          <select
            value={selectedTypeFilter}
            onChange={(e) => setSelectedTypeFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700"
          >
            <option value="">Todos os Tipos</option>
            <option value="income">Receitas</option>
            <option value="expense">Despesas</option>
            <option value="debt_payment">Dívidas</option>
          </select>

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
        </div>

        {/* Tabela de Lançamentos */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Data</th>
                  <th className="py-3.5 px-4">Descrição</th>
                  <th className="py-3.5 px-4">Tags</th>
                  <th className="py-3.5 px-4">Essencialidade</th>
                  <th className="py-3.5 px-4">Parcela</th>
                  <th className="py-3.5 px-4 text-right">Valor</th>
                  <th className="py-3.5 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredTransactions.map((tx) => {
                  const isIncome = tx.type === "income";
                  return (
                    <tr key={tx.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-500 whitespace-nowrap">
                        {tx.transaction_date}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-bold text-slate-800 block">{tx.description}</span>
                        <span className="text-[11px] text-slate-400">
                          {accounts.find((a) => a.id === tx.account_id)?.name || "Conta"}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {tx.tags?.map((t: any) => (
                            <span
                              key={t.id}
                              className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-600 border border-blue-200"
                            >
                              #{t.name}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            tx.essentiality === "essential"
                              ? "bg-emerald-100 text-emerald-800"
                              : tx.essentiality === "waste"
                              ? "bg-red-100 text-red-800"
                              : tx.essentiality === "debt"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {tx.essentiality}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                        {tx.installment_total > 1 ? `${tx.installment_current}/${tx.installment_total}` : "À vista"}
                      </td>
                      <td
                        className={`py-3 px-4 text-right font-extrabold whitespace-nowrap ${
                          isIncome ? "text-emerald-600" : "text-slate-900"
                        }`}
                      >
                        {isIncome ? "+" : "-"} R${" "}
                        {parseFloat(tx.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleOpenEdit(tx)}
                            className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-700"
                            title="Editar Transação"
                          >
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteTransaction(tx.id)}
                            className="p-1 rounded-md hover:bg-red-50 text-slate-400 hover:text-red-600"
                            title="Excluir Transação"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal de Novo / Editar Lançamento */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative max-h-[90vh] overflow-y-auto">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-lg font-bold text-slate-900">
                {isEditMode ? "Editar Lançamento" : "Novo Lançamento Financeiro"}
              </h2>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSaveTransaction} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Descrição</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Ex: Supermercado, Aluguel, Salário..."
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 font-medium"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Valor (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="0.00"
                      required
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold font-mono focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Data</label>
                    <input
                      type="date"
                      value={transactionDate}
                      onChange={(e) => setTransactionDate(e.target.value)}
                      required
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Tipo</label>
                    <select
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                    >
                      <option value="expense">Despesa</option>
                      <option value="income">Receita</option>
                      <option value="debt_payment">Pagamento de Dívida</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Essencialidade (50-30-20)</label>
                    <select
                      value={essentiality}
                      onChange={(e) => setEssentiality(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold"
                    >
                      <option value="essential">Essencial (Sobrevivência / Moradia)</option>
                      <option value="lifestyle">Estilo de Vida (Lazer / Conforto)</option>
                      <option value="waste">Ralo / Desperdício (Evitável)</option>
                      <option value="debt">Dívida / Encargos</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Conta / Cartão</label>
                    <select
                      value={accountId}
                      onChange={(e) => setAccountId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      {accounts.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Quem Pagou</label>
                    <select
                      value={paidByMemberId}
                      onChange={(e) => setPaidByMemberId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      {members.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.display_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Categoria</label>
                    <select
                      value={categoryId}
                      onChange={(e) => setCategoryId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Centro de Custo</label>
                    <select
                      value={costCenterId}
                      onChange={(e) => setCostCenterId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      {costCenters.map((cc) => (
                        <option key={cc.id} value={cc.id}>
                          {cc.name} ({cc.scope})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Parcelamento (apenas no modo criação) */}
                {!isEditMode && (
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Parcelamento (1x a 120x)</label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      value={totalInstallments}
                      onChange={(e) => setTotalInstallments(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono"
                    />
                  </div>
                )}

                {/* Campo Dedicado de Tags */}
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <label className="block text-xs font-bold text-slate-700">Tags do Projeto / Evento (Campo Dedicado)</label>
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {tags.map((t) => {
                      const isSelected = selectedTagIds.includes(t.id);
                      return (
                        <button
                          key={t.id}
                          type="button"
                          onClick={() => {
                            if (isSelected) {
                              setSelectedTagIds(selectedTagIds.filter((id) => id !== t.id));
                            } else {
                              setSelectedTagIds([...selectedTagIds, t.id]);
                            }
                          }}
                          className={`px-2.5 py-1 rounded-full text-xs font-bold border transition-colors cursor-pointer ${
                            isSelected
                              ? "bg-blue-600 text-white border-blue-600"
                              : "bg-white text-slate-600 border-slate-300 hover:bg-slate-100"
                          }`}
                        >
                          #{t.name}
                        </button>
                      );
                    })}
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTagName}
                      onChange={(e) => setNewTagName(e.target.value)}
                      placeholder="Criar nova tag (ex: #Reforma2026)..."
                      className="flex-1 px-3 py-1.5 rounded-xl border border-slate-300 text-xs bg-white"
                    />
                    <button
                      type="button"
                      onClick={handleCreateTag}
                      className="px-3 py-1.5 rounded-xl bg-slate-800 text-white font-bold text-xs hover:bg-slate-900"
                    >
                      + Criar Tag
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  {isEditMode ? "Salvar Alterações" : "Salvar Lançamento"}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
