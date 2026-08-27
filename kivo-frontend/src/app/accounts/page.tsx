"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { CreditCard, Wallet, Plus, Building2, Calendar, X, AlertCircle } from "lucide-react";

export default function AccountsPage() {
  const { activeWorkspace } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Formulário
  const [name, setName] = useState("");
  const [type, setType] = useState("checking");
  const [ownerMemberId, setOwnerMemberId] = useState("");
  const [initialBalance, setInitialBalance] = useState("0.00");
  const [creditLimit, setCreditLimit] = useState("");
  const [closingDay, setClosingDay] = useState("5");
  const [dueDay, setDueDay] = useState("12");
  const [error, setError] = useState("");

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

      setIsModalOpen(false);
      setName("");
      setInitialBalance("0.00");
      setCreditLimit("");
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar conta.");
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Contas Bancárias & Cartões</h1>
            <p className="text-xs text-slate-500">Gerencie todos os seus bancos, carteiras e cartões de crédito</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Adicionar Conta / Cartão</span>
          </button>
        </div>

        {/* Grid de Contas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {accounts.map((acc) => (
            <div key={acc.id} className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-10 h-10 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center">
                    {acc.type === "credit_card" ? (
                      <CreditCard className="w-5 h-5 text-purple-600" />
                    ) : (
                      <Wallet className="w-5 h-5 text-emerald-600" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">{acc.name}</h3>
                    <span className="text-[10px] uppercase font-bold text-slate-400">
                      {acc.type === "checking" ? "Conta Corrente" : acc.type === "credit_card" ? "Cartão de Crédito" : "Carteira"}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <span className="text-xs text-slate-400 font-semibold block">Saldo em Tempo Real</span>
                <div className="text-2xl font-extrabold text-slate-900 mt-0.5">
                  R$ {parseFloat(acc.current_balance || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </div>
              </div>

              {acc.type === "credit_card" && (
                <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Limite Total:</span>
                    <span className="font-bold text-slate-700">
                      R$ {parseFloat(acc.credit_limit || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fechamento / Vencimento:</span>
                    <span className="font-bold text-slate-700">
                      Dia {acc.closing_day} / Dia {acc.due_day}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Modal de Criação de Conta */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400"
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
                    placeholder="Ex: Nubank, Sicoob, Cartão XP..."
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

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Saldo Inicial (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={initialBalance}
                    onChange={(e) => setInitialBalance(e.target.value)}
                    placeholder="0.00"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-mono"
                  />
                </div>

                {type === "credit_card" && (
                  <div className="p-3.5 rounded-2xl bg-purple-50 border border-purple-100 space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-purple-900 mb-1">Limite do Cartão (R$)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={creditLimit}
                        onChange={(e) => setCreditLimit(e.target.value)}
                        placeholder="10000.00"
                        className="w-full px-3 py-2 rounded-xl border border-purple-200 text-sm bg-white font-mono"
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
                )}

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors"
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
