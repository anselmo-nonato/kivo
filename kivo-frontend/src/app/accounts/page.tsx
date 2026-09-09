"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  CreditCard,
  Wallet,
  Plus,
  Building2,
  Calendar,
  X,
  AlertCircle,
  CheckCircle2,
  ArrowRightLeft,
  Settings2,
  Sparkles,
  Layers,
  Landmark,
  ReceiptText
} from "lucide-react";

export default function AccountsPage() {
  const { activeWorkspace } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal de Criação
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState("checking");
  const [ownerMemberId, setOwnerMemberId] = useState("");
  const [initialBalance, setInitialBalance] = useState("0.00");
  const [creditLimit, setCreditLimit] = useState("");
  const [closingDay, setClosingDay] = useState("5");
  const [dueDay, setDueDay] = useState("12");

  // Modal de Pagamento de Fatura
  const [selectedCardForPayment, setSelectedCardForPayment] = useState<any | null>(null);
  const [paymentSourceAccountId, setPaymentSourceAccountId] = useState("");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 10));
  const [paymentNotes, setPaymentNotes] = useState("");

  // Modal de Edição / Ajuste de Limite
  const [selectedAccountForEdit, setSelectedAccountForEdit] = useState<any | null>(null);
  const [editName, setEditName] = useState("");
  const [editCreditLimit, setEditCreditLimit] = useState("");
  const [editAdjustedAvailableLimit, setEditAdjustedAvailableLimit] = useState("");
  const [editClosingDay, setEditClosingDay] = useState("");
  const [editDueDay, setEditDueDay] = useState("");
  const [editInitialBalance, setEditInitialBalance] = useState("");

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [accRes, wsRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}`),
      ]);
      setAccounts(accRes.data);
      setMembers(wsRes.data.members || []);
      if (wsRes.data.members?.length > 0) {
        setOwnerMemberId(wsRes.data.members[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/accounts`, {
        name: name.trim(),
        type,
        owner_member_id: ownerMemberId,
        initial_balance: parseFloat(initialBalance) || 0,
        credit_limit: type === "credit_card" && creditLimit ? parseFloat(creditLimit) : null,
        closing_day: type === "credit_card" ? parseInt(closingDay) : null,
        due_day: type === "credit_card" ? parseInt(dueDay) : null,
      });

      setIsCreateModalOpen(false);
      setName("");
      setInitialBalance("0.00");
      setCreditLimit("");
      setSuccessMessage("Conta cadastrada com sucesso!");
      setTimeout(() => setSuccessMessage(""), 4000);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar conta.");
    }
  };

  const openPayInvoiceModal = (card: any) => {
    setSelectedCardForPayment(card);
    const bankAccounts = accounts.filter((a) => a.type !== "credit_card" && a.id !== card.id);
    if (bankAccounts.length > 0) {
      setPaymentSourceAccountId(bankAccounts[0].id);
    }
    setPaymentAmount(card.used_limit ? parseFloat(card.used_limit).toFixed(2) : "0.00");
    setPaymentDate(new Date().toISOString().slice(0, 10));
    setPaymentNotes(`Pagamento Fatura ${card.name}`);
    setError("");
  };

  const handlePayInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!selectedCardForPayment || !paymentSourceAccountId) return;

    const amt = parseFloat(paymentAmount);
    if (isNaN(amt) || amt <= 0) {
      setError("Informe um valor de pagamento válido maior que zero.");
      return;
    }

    try {
      await api.post(`/workspaces/${activeWorkspace?.id}/accounts/${selectedCardForPayment.id}/pay-invoice`, {
        source_account_id: paymentSourceAccountId,
        amount: amt,
        payment_date: paymentDate,
        notes: paymentNotes.trim() || undefined,
      });

      setSelectedCardForPayment(null);
      setSuccessMessage(`Fatura de R$ ${amt.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} paga com sucesso! Limite restaurado.`);
      setTimeout(() => setSuccessMessage(""), 4000);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao processar pagamento de fatura.");
    }
  };

  const openEditAccountModal = (acc: any) => {
    setSelectedAccountForEdit(acc);
    setEditName(acc.name);
    setEditCreditLimit(acc.credit_limit ? String(acc.credit_limit) : "");
    setEditAdjustedAvailableLimit(acc.available_limit ? String(acc.available_limit) : "");
    setEditClosingDay(acc.closing_day ? String(acc.closing_day) : "5");
    setEditDueDay(acc.due_day ? String(acc.due_day) : "12");
    setEditInitialBalance(acc.initial_balance ? String(acc.initial_balance) : "0.00");
    setError("");
  };

  const handleEditAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!selectedAccountForEdit) return;

    try {
      const payload: any = {
        name: editName.trim(),
      };

      if (selectedAccountForEdit.type === "credit_card") {
        if (editCreditLimit) payload.credit_limit = parseFloat(editCreditLimit);
        if (editClosingDay) payload.closing_day = parseInt(editClosingDay);
        if (editDueDay) payload.due_day = parseInt(editDueDay);
        if (editAdjustedAvailableLimit !== "") {
          payload.adjusted_available_limit = parseFloat(editAdjustedAvailableLimit);
        }
      } else {
        if (editInitialBalance !== "") {
          payload.initial_balance = parseFloat(editInitialBalance);
        }
      }

      await api.put(`/workspaces/${activeWorkspace?.id}/accounts/${selectedAccountForEdit.id}`, payload);
      setSelectedAccountForEdit(null);
      setSuccessMessage("Conta atualizada com sucesso!");
      setTimeout(() => setSuccessMessage(""), 4000);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao atualizar conta.");
    }
  };

  const bankAccounts = accounts.filter((a) => a.type !== "credit_card");
  const creditCards = accounts.filter((a) => a.type === "credit_card");

  return (
    <AppLayout>
      <div className="space-y-8 pb-12">
        {/* Notificação de Sucesso */}
        {successMessage && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold flex items-center gap-2.5 animate-in fade-in">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Cabeçalho da Página */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Contas Bancárias & Cartões</h1>
            <p className="text-xs text-slate-500">
              Gerencie seus bancos, saldos disponíveis, limites de cartões e faturas
            </p>
          </div>
          <button
            onClick={() => {
              setIsCreateModalOpen(true);
              setError("");
            }}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Adicionar Conta / Cartão</span>
          </button>
        </div>

        {/* SEÇÃO 1: CARTÕES DE CRÉDITO */}
        {creditCards.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center">
                  <CreditCard className="w-4 h-4" />
                </div>
                <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-700">
                  Cartões de Crédito ({creditCards.length})
                </h2>
              </div>
              <span className="text-xs text-slate-400 font-medium">Controle de limites e faturas</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {creditCards.map((card) => {
                const totalLimit = parseFloat(card.credit_limit || 0);
                const usedLimit = parseFloat(card.used_limit || 0);
                const availableLimit = parseFloat(card.available_limit || 0);
                const usedPercentage = totalLimit > 0 ? Math.min(100, Math.round((usedLimit / totalLimit) * 100)) : 0;

                let progressColor = "bg-emerald-500";
                if (usedPercentage > 80) progressColor = "bg-red-500";
                else if (usedPercentage > 50) progressColor = "bg-amber-500";

                return (
                  <div
                    key={card.id}
                    className="p-6 rounded-3xl bg-white border border-purple-100 shadow-xs flex flex-col justify-between space-y-4 relative overflow-hidden hover:border-purple-200 transition-all"
                  >
                    {/* Barra de destaque superior */}
                    <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-purple-500 to-indigo-600" />

                    <div className="space-y-4">
                      {/* Topo do Card */}
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
                            <CreditCard className="w-5 h-5" />
                          </div>
                          <div>
                            <h3 className="font-bold text-slate-900 text-base leading-snug">{card.name}</h3>
                            <span className="text-[10px] uppercase font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-100">
                              Cartão de Crédito
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => openEditAccountModal(card)}
                          className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                          title="Ajustar Limite / Configurações"
                        >
                          <Settings2 className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Caixa de Limite Disponível */}
                      <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100/80 space-y-1">
                        <span className="text-xs text-emerald-800 font-semibold block">Limite Disponível</span>
                        <div className="text-2xl font-extrabold text-emerald-700 tracking-tight">
                          R$ {availableLimit.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                        </div>
                      </div>

                      {/* Barra de Progresso do Limite */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between text-xs font-semibold">
                          <span className="text-slate-500">Limite Usado ({usedPercentage}%)</span>
                          <span className="text-slate-800 font-bold">
                            R$ {usedLimit.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${progressColor} transition-all duration-500 rounded-full`}
                            style={{ width: `${usedPercentage}%` }}
                          />
                        </div>
                      </div>

                      {/* Detalhes de Fechamento e Vencimento */}
                      <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-1.5">
                        <div className="flex justify-between">
                          <span>Limite Total:</span>
                          <span className="font-bold text-slate-800">
                            R$ {totalLimit.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Fechamento / Vencimento:</span>
                          <span className="font-bold text-slate-800">
                            Dia {card.closing_day || 5} • Dia {card.due_day || 12}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Botões de Fatura e Pagamento */}
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      <Link
                        href={`/transactions?account_id=${card.id}`}
                        className="py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
                      >
                        <ReceiptText className="w-3.5 h-3.5 text-purple-600" />
                        <span>Ver Fatura</span>
                      </Link>
                      <button
                        onClick={() => openPayInvoiceModal(card)}
                        className="py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-md shadow-purple-500/20 flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                      >
                        <ArrowRightLeft className="w-3.5 h-3.5" />
                        <span>Pagar Fatura</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* SEÇÃO 2: CONTAS BANCÁRIAS & CARTEIRAS */}
        <div className="space-y-4 pt-6 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
                <Landmark className="w-4 h-4" />
              </div>
              <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-700">
                Contas Correntes, Carteiras & Investimentos ({bankAccounts.length})
              </h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Saldos monetários líquidos</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {bankAccounts.map((acc) => {
              const currentBal = parseFloat(acc.current_balance || 0);
              const isNegative = currentBal < 0;

              return (
                <div
                  key={acc.id}
                  className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:border-slate-300 transition-all"
                >
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                          <Wallet className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-900 text-base leading-snug">{acc.name}</h3>
                          <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                            {acc.type === "checking"
                              ? "Conta Corrente"
                              : acc.type === "investment"
                              ? "Investimentos"
                              : "Carteira / Dinheiro"}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => openEditAccountModal(acc)}
                        className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                        title="Editar Conta"
                      >
                        <Settings2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Caixa de Saldo em Tempo Real */}
                    <div className={`p-4 rounded-2xl ${isNegative ? "bg-red-50/70 border border-red-100" : "bg-slate-50 border border-slate-100"} space-y-1`}>
                      <span className="text-xs text-slate-500 font-semibold block">Saldo em Tempo Real</span>
                      <div className={`text-2xl font-extrabold ${isNegative ? "text-red-600" : "text-slate-900"} tracking-tight`}>
                        R$ {currentBal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 flex justify-between items-center">
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-semibold">Saldo Inicial</span>
                      <span className="font-bold text-slate-700">
                        R$ {parseFloat(acc.initial_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <Link
                      href={`/transactions?account_id=${acc.id}`}
                      className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition-colors"
                    >
                      <ReceiptText className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Ver Extrato</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* MODAL DE PAGAMENTO DE FATURA */}
        {selectedCardForPayment && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setSelectedCardForPayment(null)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center">
                  <ArrowRightLeft className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Pagar Fatura - {selectedCardForPayment.name}</h2>
                  <p className="text-xs text-slate-500">Debita da conta bancária e restabelece o limite disponível</p>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handlePayInvoice} className="space-y-4">
                {/* Resumo Atual do Cartão */}
                <div className="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-purple-50/70 border border-purple-100 text-xs">
                  <div>
                    <span className="text-purple-700 font-semibold block">Limite Usado (Fatura):</span>
                    <span className="text-base font-extrabold text-purple-950">
                      R$ {parseFloat(selectedCardForPayment.used_limit || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div>
                    <span className="text-purple-700 font-semibold block">Limite Total:</span>
                    <span className="text-base font-extrabold text-slate-800">
                      R$ {parseFloat(selectedCardForPayment.credit_limit || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Seleção da Conta de Débito */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Conta de Débito (De onde sairá o dinheiro?)
                  </label>
                  <select
                    value={paymentSourceAccountId}
                    onChange={(e) => setPaymentSourceAccountId(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-purple-500"
                  >
                    {bankAccounts.map((acc) => (
                      <option key={acc.id} value={acc.id}>
                        {acc.name} — Saldo: R$ {parseFloat(acc.current_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Valor do Pagamento e Data */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Valor do Pagamento (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={paymentAmount}
                      onChange={(e) => setPaymentAmount(e.target.value)}
                      required
                      placeholder="0.00"
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Data do Pagamento</label>
                    <input
                      type="date"
                      value={paymentDate}
                      onChange={(e) => setPaymentDate(e.target.value)}
                      required
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>

                {/* Simulação do Novo Limite */}
                {parseFloat(paymentAmount) > 0 && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 space-y-1">
                    <div className="flex justify-between font-semibold items-center">
                      <span>Novo Limite Disponível Estimado:</span>
                      <span className="font-extrabold text-sm text-emerald-700">
                        R${" "}
                        {Math.min(
                          parseFloat(selectedCardForPayment.credit_limit || 0),
                          parseFloat(selectedCardForPayment.available_limit || 0) + parseFloat(paymentAmount || 0)
                        ).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Observações (Opcional)</label>
                  <input
                    type="text"
                    value={paymentNotes}
                    onChange={(e) => setPaymentNotes(e.target.value)}
                    placeholder="Ex: Pagamento integral fatura Setembro"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-sm shadow-md shadow-purple-500/20 transition-colors cursor-pointer"
                >
                  Confirmar Pagamento da Fatura
                </button>
              </form>
            </div>
          </div>
        )}

        {/* MODAL DE EDIÇÃO / AJUSTE DE LIMITE */}
        {selectedAccountForEdit && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setSelectedAccountForEdit(null)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center">
                  <Settings2 className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Configurar Conta / Limites</h2>
                  <p className="text-xs text-slate-500">{selectedAccountForEdit.name}</p>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleEditAccount} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Nome da Conta / Cartão</label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                {selectedAccountForEdit.type === "credit_card" ? (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-purple-900 mb-1">Limite Total do Cartão (R$)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editCreditLimit}
                        onChange={(e) => setEditCreditLimit(e.target.value)}
                        placeholder="6200.00"
                        className="w-full px-3.5 py-2.5 rounded-xl border border-purple-200 text-sm bg-purple-50/50"
                      />
                    </div>

                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        <span>Recalibrar Limite Disponível Atual</span>
                      </div>
                      <p className="text-[11px] text-slate-500 leading-relaxed">
                        Se o limite disponível no aplicativo do banco for diferente do calculado, informe o valor exato
                        abaixo para sincronizar perfeitamente:
                      </p>
                      <input
                        type="number"
                        step="0.01"
                        value={editAdjustedAvailableLimit}
                        onChange={(e) => setEditAdjustedAvailableLimit(e.target.value)}
                        placeholder="Ex: 5800.00"
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm font-bold bg-white text-emerald-600"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Dia Fechamento</label>
                        <input
                          type="number"
                          min="1"
                          max="31"
                          value={editClosingDay}
                          onChange={(e) => setEditClosingDay(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Dia Vencimento</label>
                        <input
                          type="number"
                          min="1"
                          max="31"
                          value={editDueDay}
                          onChange={(e) => setEditDueDay(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Saldo Inicial (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editInitialBalance}
                      onChange={(e) => setEditInitialBalance(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                    />
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  Salvar Alterações
                </button>
              </form>
            </div>
          </div>
        )}

        {/* MODAL DE CRIAÇÃO DE CONTA */}
        {isCreateModalOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-lg font-bold text-slate-900">Nova Conta Bancária ou Cartão</h2>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleCreateAccount} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Nome do Banco / Conta</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Ex: Nubank, Cartão Sicoob, XP..."
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Tipo</label>
                    <select
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-medium"
                    >
                      <option value="checking">Conta Corrente</option>
                      <option value="credit_card">Cartão de Crédito</option>
                      <option value="wallet">Carteira / Dinheiro</option>
                      <option value="investment">Investimentos</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Titular</label>
                    <select
                      value={ownerMemberId}
                      onChange={(e) => setOwnerMemberId(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-medium"
                    >
                      {members.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.display_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {type === "credit_card" ? (
                  <div className="p-3.5 rounded-2xl bg-purple-50 border border-purple-100 space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-purple-900 mb-1">Limite Total do Cartão (R$)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={creditLimit}
                        onChange={(e) => setCreditLimit(e.target.value)}
                        placeholder="6200.00"
                        required
                        className="w-full px-3 py-2 rounded-xl border border-purple-200 text-sm bg-white font-bold"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-purple-900 mb-1">Fatura / Limite Já Utilizado Inicial (R$)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={initialBalance}
                        onChange={(e) => setInitialBalance(e.target.value)}
                        placeholder="0.00"
                        className="w-full px-3 py-2 rounded-xl border border-purple-200 text-sm bg-white"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs font-bold text-purple-900 mb-1">Dia Fechamento</label>
                        <input
                          type="number"
                          min="1"
                          max="31"
                          value={closingDay}
                          onChange={(e) => setClosingDay(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-purple-200 text-sm bg-white"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-purple-900 mb-1">Dia Vencimento</label>
                        <input
                          type="number"
                          min="1"
                          max="31"
                          value={dueDay}
                          onChange={(e) => setDueDay(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-purple-200 text-sm bg-white"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Saldo Inicial (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={initialBalance}
                      onChange={(e) => setInitialBalance(e.target.value)}
                      placeholder="0.00"
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
                    />
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer"
                >
                  Salvar Conta
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}


