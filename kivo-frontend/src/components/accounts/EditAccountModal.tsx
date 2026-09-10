"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { X, AlertCircle, Settings2, Sparkles } from "lucide-react";

interface EditAccountModalProps {
  account: any | null;
  activeWorkspaceId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditAccountModal({
  account,
  activeWorkspaceId,
  onClose,
  onSuccess,
}: EditAccountModalProps) {
  const [editName, setEditName] = useState("");
  const [editCreditLimit, setEditCreditLimit] = useState("");
  const [editAdjustedAvailableLimit, setEditAdjustedAvailableLimit] = useState("");
  const [editClosingDay, setEditClosingDay] = useState("");
  const [editDueDay, setEditDueDay] = useState("");
  const [editInitialBalance, setEditInitialBalance] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (account) {
      setEditName(account.name || "");
      setEditCreditLimit(account.credit_limit ? String(account.credit_limit) : "");
      setEditAdjustedAvailableLimit(account.available_limit ? String(account.available_limit) : "");
      setEditClosingDay(account.closing_day ? String(account.closing_day) : "5");
      setEditDueDay(account.due_day ? String(account.due_day) : "12");
      setEditInitialBalance(account.initial_balance ? String(account.initial_balance) : "0.00");
      setError("");
    }
  }, [account]);

  if (!account) return null;

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const payload: any = {
        name: editName.trim(),
      };

      if (account.type === "credit_card") {
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

      await api.put(`/workspaces/${activeWorkspaceId}/accounts/${account.id}`, payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao atualizar conta.");
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

        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center">
            <Settings2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Configurar Conta / Limites</h2>
            <p className="text-xs text-slate-500">{account.name}</p>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleEdit} className="space-y-4">
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

          {account.type === "credit_card" ? (
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
            disabled={loading}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? "Salvando..." : "Salvar Alterações"}
          </button>
        </form>
      </div>
    </div>
  );
}
