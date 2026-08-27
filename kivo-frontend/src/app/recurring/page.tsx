"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  CalendarClock,
  Plus,
  Repeat,
  TrendingDown,
  TrendingUp,
  Scale,
  Building2,
  Calendar,
  CreditCard,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  CheckCircle2,
  Power,
  Wallet,
  Briefcase
} from "lucide-react";

export default function RecurringPage() {
  const { activeWorkspace } = useAuth();
  const [data, setData] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtro de Visualização
  const [activeTab, setActiveTab] = useState<"all" | "expenses" | "incomes">("all");

  // Modais
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedBillId, setSelectedBillId] = useState<string | null>(null);

  // Form
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [type, setType] = useState("expense");
  const [essentiality, setEssentiality] = useState("essential");
  const [frequency, setFrequency] = useState("monthly");
  const [dueDay, setDueDay] = useState("10");
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [endDate, setEndDate] = useState("");
  const [accountId, setAccountId] = useState("");
  const [paidByMemberId, setPaidByMemberId] = useState("");
  const [costCenterId, setCostCenterId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [error, setError] = useState("");

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [recRes, accRes, catRes, ccRes, wsRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/recurring`),
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}/categories`),
        api.get(`/workspaces/${activeWorkspace.id}/cost-centers`),
        api.get(`/workspaces/${activeWorkspace.id}`),
      ]);

      setData(recRes.data);
      setAccounts(accRes.data);
      setCategories(catRes.data);
      setCostCenters(ccRes.data);
      setMembers(wsRes.data.members || []);

      if (accRes.data.length > 0) setAccountId(accRes.data[0].id);
      if (wsRes.data.members?.length > 0) setPaidByMemberId(wsRes.data.members[0].id);
      if (ccRes.data.length > 0) setCostCenterId(ccRes.data[0].id);
      if (catRes.data.length > 0) setCategoryId(catRes.data[0].id);
    } catch (err) {
      console.error("Erro ao carregar despesas fixas:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  const handleOpenCreate = (targetType: "expense" | "income" = "expense") => {
    setIsEditMode(false);
    setSelectedBillId(null);
    setDescription("");
    setAmount("");
    setType(targetType);
    setEssentiality("essential");
    setFrequency("monthly");
    setDueDay(targetType === "income" ? "5" : "10");
    setStartDate(new Date().toISOString().slice(0, 10));
    setEndDate("");
    setIsActive(true);
    setError("");
    setIsModalOpen(true);
  };

  const handleOpenEdit = (b: any) => {
    setIsEditMode(true);
    setSelectedBillId(b.id);
    setDescription(b.description);
    setAmount(b.amount);
    setType(b.type);
    setEssentiality(b.essentiality);
    setFrequency(b.frequency);
    setDueDay(b.due_day.toString());
    setStartDate(b.start_date);
    setEndDate(b.end_date || "");
    setAccountId(b.account_id || "");
    setPaidByMemberId(b.paid_by_member_id || "");
    setCostCenterId(b.cost_center_id || "");
    setCategoryId(b.category_id || "");
    setIsActive(b.is_active);
    setError("");
    setIsModalOpen(true);
  };

  const handleSaveBill = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const payload = {
        description: description.trim(),
        amount: parseFloat(amount),
        type,
        essentiality,
        frequency,
        due_day: parseInt(dueDay),
        start_date: startDate,
        end_date: endDate ? endDate : null,
        account_id: accountId || null,
        paid_by_member_id: paidByMemberId || null,
        cost_center_id: costCenterId || null,
        category_id: categoryId || null,
        is_active: isActive,
      };

      if (isEditMode && selectedBillId) {
        await api.put(`/workspaces/${activeWorkspace?.id}/recurring/${selectedBillId}`, payload);
      } else {
        await api.post(`/workspaces/${activeWorkspace?.id}/recurring`, payload);
      }

      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar conta fixa.");
    }
  };

  const handleDeleteBill = async (id: string) => {
    if (!confirm("Tem certeza que deseja excluir esta conta recorrente?")) return;
    try {
      await api.delete(`/workspaces/${activeWorkspace?.id}/recurring/${id}`);
      loadData();
    } catch (err) {
      console.error("Erro ao excluir conta fixa:", err);
    }
  };

  const handleToggleActive = async (b: any) => {
    try {
      await api.put(`/workspaces/${activeWorkspace?.id}/recurring/${b.id}`, {
        is_active: !b.is_active,
      });
      loadData();
    } catch (err) {
      console.error("Erro ao alternar status:", err);
    }
  };

  // Filtragem por Tab
  const filteredBills = data?.bills?.filter((b: any) => {
    if (activeTab === "expenses") return b.type === "expense";
    if (activeTab === "incomes") return b.type === "income";
    return true;
  }) || [];

  return (
    <AppLayout>
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Contas & Rendas Fixas</h1>
            <p className="text-xs text-slate-500">
              Controle de salários, pró-labore, aluguel, assinaturas e previsibilidade de caixa
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleOpenCreate("income")}
              className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <TrendingUp className="w-4 h-4" />
              <span>+ Nova Renda Fixa (Salário)</span>
            </button>
            <button
              onClick={() => handleOpenCreate("expense")}
              className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <TrendingDown className="w-4 h-4 text-red-400" />
              <span>+ Nova Despesa Fixa</span>
            </button>
          </div>
        </div>

        {/* Cards de Resumo */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase tracking-wider">Custo Fixo Mensal</span>
              <TrendingDown className="w-5 h-5 text-red-500" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-red-600">
              R$ {parseFloat(data?.total_monthly_fixed_expenses || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-[11px] text-slate-400">Total comprometido por mês</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase tracking-wider">Receitas Fixas (Salários)</span>
              <TrendingUp className="w-5 h-5 text-emerald-500" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-emerald-600">
              R$ {parseFloat(data?.total_monthly_fixed_income || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-[11px] text-slate-400">Salários e rendas previsíveis</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase tracking-wider">Sobra Fixa Prevista</span>
              <Scale className="w-5 h-5 text-blue-500" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-slate-900">
              R$ {parseFloat(data?.net_fixed_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-[11px] text-slate-400">Disponível para variáveis e reserva</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase tracking-wider">Recorrências Ativas</span>
              <Repeat className="w-5 h-5 text-purple-500" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-purple-600">
              {data?.total_active_bills || 0}
            </div>
            <p className="text-[11px] text-slate-400">Contratos e salários cadastrados</p>
          </div>
        </div>

        {/* Abas e Tabela */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Tabs */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab("all")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                  activeTab === "all"
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                Todas ({data?.bills?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab("expenses")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                  activeTab === "expenses"
                    ? "bg-red-600 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                Despesas Fixas ({data?.bills?.filter((b: any) => b.type === "expense").length || 0})
              </button>
              <button
                onClick={() => setActiveTab("incomes")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                  activeTab === "incomes"
                    ? "bg-emerald-600 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                Receitas Fixas / Salários ({data?.bills?.filter((b: any) => b.type === "income").length || 0})
              </button>
            </div>

            <span className="text-xs font-semibold text-slate-400">
              {filteredBills.length} itens exibidos
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Descrição</th>
                  <th className="py-3.5 px-4">Tipo</th>
                  <th className="py-3.5 px-4">Categoria / Centro</th>
                  <th className="py-3.5 px-4">Dia do Crédito / Venc.</th>
                  <th className="py-3.5 px-4">Titular / Responsável</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Valor Mensal</th>
                  <th className="py-3.5 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredBills.map((b: any) => {
                  const isIncome = b.type === "income";
                  return (
                    <tr key={b.id} className={`hover:bg-slate-50/80 transition-colors ${!b.is_active ? "opacity-50" : ""}`}>
                      <td className="py-3.5 px-4">
                        <span className="font-bold text-slate-900 block">{b.description}</span>
                        <span className="text-[10px] text-slate-400">
                          {b.account_name ? `Conta: ${b.account_name}` : "Sem conta vinculada"} • Início: {b.start_date}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            isIncome
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {isIncome ? "Renda Fixa" : "Despesa Fixa"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-semibold text-slate-700 block">{b.category_name || "Geral"}</span>
                        <span className="text-[10px] text-slate-400">{b.cost_center_name || "Casa"}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-700">
                        Todo dia {b.due_day}
                      </td>
                      <td className="py-3.5 px-4 text-slate-700">
                        {b.paid_by_member_name || "—"}
                      </td>
                      <td className="py-3.5 px-4">
                        <button
                          onClick={() => handleToggleActive(b)}
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border cursor-pointer ${
                            b.is_active
                              ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                              : "bg-slate-100 text-slate-500 border-slate-300"
                          }`}
                        >
                          {b.is_active ? "Ativo" : "Pausado"}
                        </button>
                      </td>
                      <td
                        className={`py-3.5 px-4 text-right font-extrabold whitespace-nowrap font-mono text-sm ${
                          isIncome ? "text-emerald-600" : "text-slate-900"
                        }`}
                      >
                        {isIncome ? "+" : "-"} R${" "}
                        {parseFloat(b.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleOpenEdit(b)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                            title="Editar"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteBill(b.id)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="Excluir"
                          >
                            <Trash2 className="w-4 h-4" />
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

        {/* Modal: Novo / Editar Despesa ou Receita Fixa */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative max-h-[90vh] overflow-y-auto">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-2">
                {type === "income" ? (
                  <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-xl bg-red-100 text-red-700 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5" />
                  </div>
                )}
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {isEditMode
                      ? type === "income" ? "Editar Renda Fixa" : "Editar Despesa Fixa"
                      : type === "income" ? "Cadastrar Renda Fixa (Salário / Pró-labore)" : "Cadastrar Despesa Fixa"}
                  </h2>
                  <p className="text-xs text-slate-500">
                    {type === "income" ? "Receitas mensais certas e previsíveis" : "Contas e custos que se repetem todo mês"}
                  </p>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSaveBill} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    {type === "income" ? "Nome da Fonte de Renda" : "Descrição da Conta"}
                  </label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={type === "income" ? "Ex: Salário Empresa X, Pró-labore, Aluguel Imóvel..." : "Ex: Aluguel Apartamento, Internet Fibra, Netflix..."}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Valor Mensal (R$)</label>
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
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      {type === "income" ? "Dia do Crédito no Mês" : "Dia do Vencimento"}
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="31"
                      value={dueDay}
                      onChange={(e) => setDueDay(e.target.value)}
                      required
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-mono"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Tipo de Lançamento</label>
                    <select
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-semibold"
                    >
                      <option value="expense">Despesa Fixa</option>
                      <option value="income">Receita Fixa (Salário / Pró-labore)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      {type === "income" ? "Natureza / Tipo da Renda" : "Classificação 50-30-20"}
                    </label>
                    <select
                      value={essentiality}
                      onChange={(e) => setEssentiality(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-semibold"
                    >
                      {type === "income" ? (
                        <>
                          <option value="essential">💼 Renda Principal (Salário CLT / Pró-labore)</option>
                          <option value="lifestyle">🏠 Renda Imobiliária / Aluguel Recebido</option>
                          <option value="debt">🎓 Aposentadoria / Pensão / Benefício</option>
                          <option value="waste">📈 Rendimentos de Investimentos / Outros</option>
                        </>
                      ) : (
                        <>
                          <option value="essential">🏠 Essencial (50% - Moradia, Água, Luz, Condomínio)</option>
                          <option value="lifestyle">🍿 Estilo de Vida (30% - Streaming, Academia, Conforto)</option>
                          <option value="debt">💳 Dívidas & Financiamentos (20% - Parcelas, Empréstimos)</option>
                          <option value="waste">⚠️ Ralo / Desperdício (Assinatura não usada, Multas)</option>
                        </>
                      )}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      {type === "income" ? "Conta de Destino (Onde cai)" : "Conta de Débito Padrão"}
                    </label>
                    <select
                      value={accountId}
                      onChange={(e) => setAccountId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      <option value="">Sem conta vinculada</option>
                      {accounts.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      {type === "income" ? "Titular da Renda" : "Quem Paga (Responsável)"}
                    </label>
                    <select
                      value={paidByMemberId}
                      onChange={(e) => setPaidByMemberId(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    >
                      <option value="">Todos / Compartilhado</option>
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
                      <option value="">Geral</option>
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
                      <option value="">Casa</option>
                      {costCenters.map((cc) => (
                        <option key={cc.id} value={cc.id}>
                          {cc.name} ({cc.scope})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Data de Início do Contrato</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      required
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Data Término (Opcional)</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  {isEditMode ? "Salvar Alterações" : type === "income" ? "Cadastrar Renda Fixa" : "Cadastrar Despesa Fixa"}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
