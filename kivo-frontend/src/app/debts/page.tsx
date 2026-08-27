"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  TrendingDown,
  Plus,
  Flame,
  Snowflake,
  Calculator,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  X,
  AlertCircle,
  Pencil,
  Trash2,
  CheckCircle,
  CreditCard
} from "lucide-react";

export default function DebtsPage() {
  const { activeWorkspace } = useAuth();
  const [debts, setDebts] = useState<any[]>([]);
  const [simulation, setSimulation] = useState<any>(null);
  const [extraBudget, setExtraBudget] = useState("500");
  const [loading, setLoading] = useState(true);

  // Modais
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAmortizeModalOpen, setIsAmortizeModalOpen] = useState(false);
  const [isPayInstallmentModalOpen, setIsPayInstallmentModalOpen] = useState(false);
  const [selectedDebt, setSelectedDebt] = useState<any>(null);

  // Form Amortização
  const [amortizeAmount, setAmortizeAmount] = useState("");
  const [amortizeStrategy, setAmortizeStrategy] = useState("reduce_term");

  // Form Pagamento de Parcela
  const [installmentPayAmount, setInstallmentPayAmount] = useState("");
  const [installmentPayDate, setInstallmentPayDate] = useState(new Date().toISOString().slice(0, 10));
  const [payAccountId, setPayAccountId] = useState("");

  // Form Criar / Editar Dívida
  const [creditorName, setCreditorName] = useState("");
  const [originalAmount, setOriginalAmount] = useState("");
  const [currentBalance, setCurrentBalance] = useState("");
  const [interestRate, setInterestRate] = useState("0.0");
  const [installmentAmount, setInstallmentAmount] = useState("");
  const [remainingInstallments, setRemainingInstallments] = useState("12");
  const [dueDay, setDueDay] = useState("10");
  const [memberId, setMemberId] = useState("");
  const [members, setMembers] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [error, setError] = useState("");

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [debtsRes, simRes, wsRes, accRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/debts`),
        api.get(`/workspaces/${activeWorkspace.id}/debts/simulate?extra_monthly_budget=${extraBudget}`),
        api.get(`/workspaces/${activeWorkspace.id}`),
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
      ]);

      setDebts(debtsRes.data);
      setSimulation(simRes.data);
      setMembers(wsRes.data.members || []);
      setAccounts(accRes.data);

      if (wsRes.data.members?.length > 0) setMemberId(wsRes.data.members[0].id);
      if (accRes.data.length > 0) setPayAccountId(accRes.data[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace, extraBudget]);

  const handleOpenEdit = (debt: any) => {
    setSelectedDebt(debt);
    setCreditorName(debt.creditor_name);
    setOriginalAmount(debt.original_amount);
    setCurrentBalance(debt.current_balance);
    setInterestRate(debt.monthly_interest_rate_percentage);
    setInstallmentAmount(debt.installment_amount);
    setRemainingInstallments(debt.remaining_installments);
    setDueDay(debt.due_day);
    setIsEditModalOpen(true);
  };

  const handleOpenPayInstallment = (debt: any) => {
    setSelectedDebt(debt);
    setInstallmentPayAmount(debt.installment_amount);
    setInstallmentPayDate(new Date().toISOString().slice(0, 10));
    setIsPayInstallmentModalOpen(true);
  };

  const handleCreateDebt = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/debts`, {
        member_id: memberId,
        creditor_name: creditorName.trim(),
        original_amount: parseFloat(originalAmount),
        current_balance: parseFloat(currentBalance),
        monthly_interest_rate: parseFloat(interestRate) / 100,
        installment_amount: parseFloat(installmentAmount),
        remaining_installments: parseInt(remainingInstallments),
        due_day: parseInt(dueDay),
      });

      setIsCreateModalOpen(false);
      resetForm();
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao cadastrar dívida.");
    }
  };

  const handleUpdateDebt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDebt) return;
    setError("");
    try {
      await api.put(`/workspaces/${activeWorkspace?.id}/debts/${selectedDebt.id}`, {
        creditor_name: creditorName.trim(),
        original_amount: parseFloat(originalAmount),
        current_balance: parseFloat(currentBalance),
        monthly_interest_rate: parseFloat(interestRate) / 100,
        installment_amount: parseFloat(installmentAmount),
        remaining_installments: parseInt(remainingInstallments),
        due_day: parseInt(dueDay),
      });

      setIsEditModalOpen(false);
      resetForm();
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao atualizar dívida.");
    }
  };

  const handleDeleteDebt = async (debtId: string) => {
    if (!confirm("Tem certeza que deseja excluir este contrato de dívida?")) return;
    try {
      await api.delete(`/workspaces/${activeWorkspace?.id}/debts/${debtId}`);
      loadData();
    } catch (err) {
      console.error("Erro ao excluir dívida:", err);
    }
  };

  const handlePayInstallment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDebt) return;
    setError("");
    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/debts/${selectedDebt.id}/pay-installment`, {
        account_id: payAccountId,
        amount: parseFloat(installmentPayAmount),
        payment_date: installmentPayDate,
      });

      setIsPayInstallmentModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao registrar pagamento da parcela.");
    }
  };

  const handleAmortize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDebt) return;
    setError("");
    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/debts/${selectedDebt.id}/amortize`, {
        extra_amount: parseFloat(amortizeAmount),
        account_id: payAccountId,
        strategy: amortizeStrategy,
      });

      setIsAmortizeModalOpen(false);
      setAmortizeAmount("");
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao amortizar dívida.");
    }
  };

  const resetForm = () => {
    setCreditorName("");
    setOriginalAmount("");
    setCurrentBalance("");
    setInterestRate("0.0");
    setInstallmentAmount("");
    setRemainingInstallments("12");
    setDueDay("10");
    setSelectedDebt(null);
  };

  return (
    <AppLayout>
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Passivos & Quitação Inteligente</h1>
            <p className="text-xs text-slate-500">
              Controle de dívidas, pagamento de parcelas, edição de contratos e simulador comparativo
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setIsCreateModalOpen(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-sm shadow-md shadow-red-500/20 flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Cadastrar Dívida / Passivo</span>
          </button>
        </div>

        {/* Tabela de Dívidas Ativas */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-lg">Contratos de Dívidas e Passivos</h3>
            <span className="text-xs font-semibold text-slate-400">{debts.length} contratos</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Credor / Contrato</th>
                  <th className="py-3.5 px-4">Taxa de Juros (a.m.)</th>
                  <th className="py-3.5 px-4">Parcela Mensal</th>
                  <th className="py-3.5 px-4">Prazo Restante</th>
                  <th className="py-3.5 px-4">Saldo Devedor</th>
                  <th className="py-3.5 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {debts.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-slate-900 block">{d.creditor_name}</span>
                      <span className="text-[10px] text-slate-400">Vencimento: dia {d.due_day}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-red-600">
                      {d.monthly_interest_rate_percentage}% a.m.
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-700">
                      R$ {parseFloat(d.installment_amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">{d.remaining_installments} meses</td>
                    <td className="py-3.5 px-4 font-mono font-extrabold text-slate-900">
                      R$ {parseFloat(d.current_balance).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* Botão Pagar Parcela */}
                        <button
                          onClick={() => handleOpenPayInstallment(d)}
                          className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer flex items-center gap-1"
                          title="Lançar Pagamento de Parcela"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Pagar Parcela</span>
                        </button>

                        {/* Botão Amortizar */}
                        <button
                          onClick={() => {
                            setSelectedDebt(d);
                            setIsAmortizeModalOpen(true);
                          }}
                          className="px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-xs border border-emerald-200 transition-colors cursor-pointer"
                        >
                          Amortizar
                        </button>

                        {/* Botão Editar */}
                        <button
                          onClick={() => handleOpenEdit(d)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
                          title="Editar / Corrigir Dívida"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>

                        {/* Botão Excluir */}
                        <button
                          onClick={() => handleDeleteDebt(d.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                          title="Excluir Dívida"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Simulador Interativo Avalanche vs Bola de Neve */}
        <div className="p-6 md:p-8 rounded-3xl bg-slate-900 text-white shadow-xl space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
                <Calculator className="w-4 h-4" />
                <span>Simulador de Estratégias de Quitação</span>
              </div>
              <h2 className="text-xl font-bold text-white">Compare os Métodos com Aporte Extra</h2>
            </div>

            <div className="flex items-center gap-3 bg-slate-800/90 p-2.5 rounded-2xl border border-slate-700">
              <span className="text-xs font-bold text-slate-300">Aporte Extra Mensal:</span>
              <div className="flex items-center gap-1 font-mono font-bold text-emerald-400">
                <span>R$</span>
                <input
                  type="number"
                  step="50"
                  value={extraBudget}
                  onChange={(e) => setExtraBudget(e.target.value)}
                  className="w-24 px-2 py-1 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm font-bold text-right"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="p-6 rounded-2xl bg-linear-to-br from-amber-500/10 to-orange-500/5 border border-amber-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold text-amber-400">
                  <Flame className="w-5 h-5" />
                  <span>Método Avalanche</span>
                </div>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300">
                  Economiza Dinheiro
                </span>
              </div>

              <p className="text-xs text-slate-400">
                Ataca primeiro as dívidas com as <strong>maiores taxas de juros mensais</strong> para estancar o custo financeiro.
              </p>

              <div className="pt-2 grid grid-cols-2 gap-2 text-xs border-t border-amber-500/20">
                <div>
                  <span className="text-slate-400 block">Tempo de Quitação:</span>
                  <span className="text-lg font-extrabold text-white">
                    {simulation?.avalanche?.months_to_payoff || 0} meses
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Total de Juros:</span>
                  <span className="text-lg font-extrabold text-amber-400 font-mono">
                    R$ {parseFloat(simulation?.avalanche?.total_interest_paid || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-linear-to-br from-blue-500/10 to-cyan-500/5 border border-blue-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold text-blue-400">
                  <Snowflake className="w-5 h-5" />
                  <span>Método Bola de Neve</span>
                </div>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300">
                  Alívio Emocional Rápido
                </span>
              </div>

              <p className="text-xs text-slate-400">
                Ataca primeiro as dívidas de <strong>menor saldo devedor</strong> para eliminá-las no menor tempo possível.
              </p>

              <div className="pt-2 grid grid-cols-2 gap-2 text-xs border-t border-blue-500/20">
                <div>
                  <span className="text-slate-400 block">Tempo de Quitação:</span>
                  <span className="text-lg font-extrabold text-white">
                    {simulation?.snowball?.months_to_payoff || 0} meses
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Total de Juros:</span>
                  <span className="text-lg font-extrabold text-blue-400 font-mono">
                    R$ {parseFloat(simulation?.snowball?.total_interest_paid || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700 text-xs text-emerald-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{simulation?.recommendation}</span>
          </div>
        </div>

        {/* Modal: Pagar Parcela */}
        {isPayInstallmentModalOpen && selectedDebt && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setIsPayInstallmentModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <CheckCircle className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Pagar Parcela de Dívida</h2>
                  <p className="text-xs text-slate-500">{selectedDebt.creditor_name}</p>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handlePayInstallment} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Valor da Parcela (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={installmentPayAmount}
                    onChange={(e) => setInstallmentPayAmount(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold font-mono focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Conta Bancária de Pagamento</label>
                  <select
                    value={payAccountId}
                    onChange={(e) => setPayAccountId(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                  >
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name} (Saldo: R$ {parseFloat(a.current_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Data do Pagamento</label>
                  <input
                    type="date"
                    value={installmentPayDate}
                    onChange={(e) => setInstallmentPayDate(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                  />
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs text-slate-500 space-y-1">
                  <p>• Esta ação criará um lançamento de despesa no seu extrato bancário.</p>
                  <p>• Abaterá 1 parcela do prazo restante e o valor do saldo devedor.</p>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  Confirmar Pagamento da Parcela
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Amortização Extraordinária */}
        {isAmortizeModalOpen && selectedDebt && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setIsAmortizeModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-lg font-bold text-slate-900">Amortização Extraordinária</h2>
              <p className="text-xs text-slate-500">{selectedDebt.creditor_name}</p>

              <form onSubmit={handleAmortize} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Valor do Aporte Extra (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={amortizeAmount}
                    onChange={(e) => setAmortizeAmount(e.target.value)}
                    placeholder="1000.00"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold font-mono focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Estratégia de Amortização</label>
                  <select
                    value={amortizeStrategy}
                    onChange={(e) => setAmortizeStrategy(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                  >
                    <option value="reduce_term">Reduzir Prazo (Economiza mais juros)</option>
                    <option value="reduce_installment">Reduzir Parcela (Alivia fluxo de caixa mensal)</option>
                  </select>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  Confirmar Amortização
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Criar / Editar Dívida */}
        {(isCreateModalOpen || isEditModalOpen) && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setIsEditModalOpen(false);
                }}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-lg font-bold text-slate-900">
                {isEditModalOpen ? "Editar / Corrigir Dívida" : "Cadastrar Dívida / Passivo"}
              </h2>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={isEditModalOpen ? handleUpdateDebt : handleCreateDebt} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Credor / Contrato</label>
                  <input
                    type="text"
                    value={creditorName}
                    onChange={(e) => setCreditorName(e.target.value)}
                    placeholder="Ex: Loft Fiança (Seguro Aluguel)..."
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Saldo Devedor (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={currentBalance}
                      onChange={(e) => {
                        setCurrentBalance(e.target.value);
                        if (!originalAmount) setOriginalAmount(e.target.value);
                      }}
                      placeholder="3440.04"
                      required
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono font-bold"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Taxa Juros (% a.m.)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={interestRate}
                      onChange={(e) => setInterestRate(e.target.value)}
                      placeholder="0.0"
                      required
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono font-bold text-red-600"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Valor Parcela (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={installmentAmount}
                      onChange={(e) => setInstallmentAmount(e.target.value)}
                      placeholder="286.67"
                      required
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono font-bold"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Parcelas Restantes</label>
                    <input
                      type="number"
                      value={remainingInstallments}
                      onChange={(e) => setRemainingInstallments(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Dia do Vencimento</label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={dueDay}
                    onChange={(e) => setDueDay(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  {isEditModalOpen ? "Salvar Alterações" : "Salvar Dívida"}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
