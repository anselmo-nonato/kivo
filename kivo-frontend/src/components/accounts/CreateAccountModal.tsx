"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { X, AlertCircle } from "lucide-react";

interface CreateAccountModalProps {
  isOpen: boolean;
  members: any[];
  activeWorkspaceId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateAccountModal({
  isOpen,
  members,
  activeWorkspaceId,
  onClose,
  onSuccess,
}: CreateAccountModalProps) {
  const [name, setName] = useState("");
  const [type, setType] = useState("checking");
  const [ownerMemberId, setOwnerMemberId] = useState("");
  const [initialBalance, setInitialBalance] = useState("0.00");
  const [creditLimit, setCreditLimit] = useState("");
  const [closingDay, setClosingDay] = useState("5");
  const [dueDay, setDueDay] = useState("12");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setName("");
      setType("checking");
      setInitialBalance("0.00");
      setCreditLimit("");
      setClosingDay("5");
      setDueDay("12");
      if (members.length > 0) {
        setOwnerMemberId(members[0].id);
      }
      setError("");
    }
  }, [isOpen, members]);

  if (!isOpen) return null;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post(`/workspaces/${activeWorkspaceId}/accounts`, {
        name: name.trim(),
        type,
        owner_member_id: ownerMemberId,
        initial_balance: parseFloat(initialBalance) || 0,
        credit_limit: type === "credit_card" && creditLimit ? parseFloat(creditLimit) : null,
        closing_day: type === "credit_card" ? parseInt(closingDay) : null,
        due_day: type === "credit_card" ? parseInt(dueDay) : null,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar conta.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-bold text-slate-900">Nova Conta Bancária ou Cartão</h2>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleCreate} className="space-y-4">
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
                <label className="block text-xs font-bold text-purple-900 mb-1">
                  Fatura / Limite Já Utilizado Inicial (R$)
                </label>
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
            disabled={loading}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? "Salvando..." : "Salvar Conta"}
          </button>
        </form>
      </div>
    </div>
  );
}
