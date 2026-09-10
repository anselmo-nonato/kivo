"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { X, AlertCircle, ArrowRightLeft } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface PayInvoiceModalProps {
  card: any | null;
  bankAccounts: any[];
  activeWorkspaceId: string;
  onClose: () => void;
  onSuccess: (amount: number) => void;
}

export function PayInvoiceModal({
  card,
  bankAccounts,
  activeWorkspaceId,
  onClose,
  onSuccess,
}: PayInvoiceModalProps) {
  const [paymentSourceAccountId, setPaymentSourceAccountId] = useState("");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 10));
  const [paymentNotes, setPaymentNotes] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (card) {
      if (bankAccounts.length > 0) {
        setPaymentSourceAccountId(bankAccounts[0].id);
      }
      setPaymentAmount(card.used_limit ? parseFloat(card.used_limit).toFixed(2) : "0.00");
      setPaymentDate(new Date().toISOString().slice(0, 10));
      setPaymentNotes(`Pagamento Fatura ${card.name}`);
      setError("");
    }
  }, [card, bankAccounts]);

  if (!card) return null;

  const handlePayInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const amt = parseFloat(paymentAmount);
    if (isNaN(amt) || amt <= 0) {
      setError("Informe um valor de pagamento válido maior que zero.");
      return;
    }

    if (!paymentSourceAccountId) {
      setError("Selecione a conta de débito.");
      return;
    }

    setLoading(true);
    try {
      await api.post(`/workspaces/${activeWorkspaceId}/accounts/${card.id}/pay-invoice`, {
        source_account_id: paymentSourceAccountId,
        amount: amt,
        payment_date: paymentDate,
        notes: paymentNotes.trim() || undefined,
      });

      onSuccess(amt);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao processar pagamento de fatura.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center">
            <ArrowRightLeft className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Pagar Fatura - {card.name}</h2>
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
                {formatCurrency(card.used_limit)}
              </span>
            </div>
            <div>
              <span className="text-purple-700 font-semibold block">Limite Total:</span>
              <span className="text-base font-extrabold text-slate-800">
                {formatCurrency(card.credit_limit)}
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
                  {acc.name} — Saldo: {formatCurrency(acc.current_balance)}
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
                  {formatCurrency(
                    Math.min(
                      parseFloat(card.credit_limit || "0"),
                      parseFloat(card.available_limit || "0") + parseFloat(paymentAmount || "0")
                    )
                  )}
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
            disabled={loading}
            className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-sm shadow-md shadow-purple-500/20 transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? "Processando..." : "Confirmar Pagamento da Fatura"}
          </button>
        </form>
      </div>
    </div>
  );
}
