"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  X,
  AlertCircle,
  ReceiptText,
  TrendingUp,
  TrendingDown,
  ArrowLeftRight,
  CreditCard,
  StickyNote,
} from "lucide-react";
import { cleanUserNotes } from "@/lib/utils";

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  isEditMode: boolean;
  editingTransaction?: any | null;
  initialType?: "expense" | "income" | "transfer";
  accounts: any[];
  categories: any[];
  costCenters: any[];
  tags: any[];
  members: any[];
  activeWorkspaceId: string;
  onSuccess: () => void;
}

export function TransactionModal({
  isOpen,
  onClose,
  isEditMode,
  editingTransaction,
  initialType = "expense",
  accounts,
  categories,
  costCenters,
  tags: initialTags,
  members,
  activeWorkspaceId,
  onSuccess,
}: TransactionModalProps) {
  const [type, setType] = useState<"expense" | "income" | "transfer">(initialType);
  const [description, setDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("paid");
  const [essentiality, setEssentiality] = useState("essential");
  const [transactionDate, setTransactionDate] = useState(new Date().toISOString().slice(0, 10));
  const [accountId, setAccountId] = useState("");
  const [destinationAccountId, setDestinationAccountId] = useState("");
  const [paidByMemberId, setPaidByMemberId] = useState("");
  const [costCenterId, setCostCenterId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [totalInstallments, setTotalInstallments] = useState("1");
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const [tags, setTags] = useState<any[]>(initialTags);
  const [newTagName, setNewTagName] = useState("");
  const [hasCardFee, setHasCardFee] = useState(false);
  const [cardFeePercentage, setCardFeePercentage] = useState("5.0");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setTags(initialTags);
  }, [initialTags]);

  useEffect(() => {
    if (!isOpen) return;

    if (isEditMode && editingTransaction) {
      setType(editingTransaction.type || "expense");
      setDescription(editingTransaction.description || "");
      setNotes(cleanUserNotes(editingTransaction.notes || ""));
      setAmount(editingTransaction.amount ? String(editingTransaction.amount) : "");
      setStatus(editingTransaction.status || "paid");
      setEssentiality(editingTransaction.essentiality || "essential");
      setTransactionDate(editingTransaction.transaction_date || new Date().toISOString().slice(0, 10));
      setAccountId(editingTransaction.account_id || (accounts[0]?.id ?? ""));
      setDestinationAccountId(editingTransaction.destination_account_id || "");
      setPaidByMemberId(editingTransaction.paid_by_member_id || (members[0]?.id ?? ""));
      setCostCenterId(editingTransaction.cost_center_id || (costCenters[0]?.id ?? ""));
      setCategoryId(editingTransaction.category_id || (categories[0]?.id ?? ""));
      setSelectedTagIds(editingTransaction.tags?.map((t: any) => t.id) || []);
      setHasCardFee(false);
    } else {
      setType(initialType);
      setDescription("");
      setNotes("");
      setAmount("");
      setStatus("paid");
      setEssentiality("essential");
      setTransactionDate(new Date().toISOString().slice(0, 10));
      setTotalInstallments("1");
      setSelectedTagIds([]);
      setHasCardFee(false);
      if (accounts.length > 0) {
        setAccountId(accounts[0].id);
        if (accounts.length > 1) {
          setDestinationAccountId(accounts[1].id);
        }
      }
      if (members.length > 0) setPaidByMemberId(members[0].id);
      if (costCenters.length > 0) setCostCenterId(costCenters[0].id);
      if (categories.length > 0) setCategoryId(categories[0].id);
    }
    setError("");
  }, [isOpen, isEditMode, editingTransaction, initialType]);

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    try {
      const res = await api.post(`/workspaces/${activeWorkspaceId}/tags`, {
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

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (type === "transfer") {
        if (!accountId || !destinationAccountId) {
          setError("Selecione a conta de origem e a conta de destino.");
          setLoading(false);
          return;
        }
        if (accountId === destinationAccountId) {
          setError("A conta de origem e a conta de destino não podem ser iguais.");
          setLoading(false);
          return;
        }
        await api.post(`/workspaces/${activeWorkspaceId}/transfers`, {
          source_account_id: accountId,
          destination_account_id: destinationAccountId,
          amount: parseFloat(amount),
          transaction_date: transactionDate,
          paid_by_member_id: paidByMemberId || undefined,
          description: description.trim() || undefined,
          notes: notes.trim() || undefined,
        });
      } else if (isEditMode && editingTransaction?.id) {
        await api.put(`/workspaces/${activeWorkspaceId}/transactions/${editingTransaction.id}`, {
          description: description.trim(),
          notes: notes.trim() || null,
          amount: parseFloat(amount),
          type,
          status,
          essentiality,
          transaction_date: transactionDate,
          account_id: accountId,
          destination_account_id: destinationAccountId || undefined,
          paid_by_member_id: paidByMemberId,
          cost_center_id: costCenterId,
          category_id: categoryId,
          tag_ids: selectedTagIds,
        });
      } else {
        await api.post(`/workspaces/${activeWorkspaceId}/transactions`, {
          description: description.trim(),
          notes: notes.trim() || null,
          amount: parseFloat(amount),
          type,
          status,
          essentiality,
          transaction_date: transactionDate,
          account_id: accountId,
          destination_account_id: destinationAccountId || undefined,
          paid_by_member_id: paidByMemberId,
          cost_center_id: costCenterId,
          category_id: categoryId,
          total_installments: parseInt(totalInstallments) || 1,
          tag_ids: selectedTagIds,
        });
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar lançamento.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Seletor de Tipo no Topo do Modal (Modo Criação) */}
        {!isEditMode && (
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 rounded-2xl">
            <button
              type="button"
              onClick={() => setType("expense")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                type === "expense"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              <TrendingDown className="w-3.5 h-3.5 text-red-500" />
              <span>Despesa</span>
            </button>
            <button
              type="button"
              onClick={() => setType("income")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                type === "income"
                  ? "bg-white text-emerald-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
              <span>Receita</span>
            </button>
            <button
              type="button"
              onClick={() => setType("transfer")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                type === "transfer"
                  ? "bg-white text-indigo-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              <ArrowLeftRight className="w-3.5 h-3.5 text-indigo-600" />
              <span>Transferência</span>
            </button>
          </div>
        )}

        <div className="flex items-center gap-2">
          {type === "transfer" ? (
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
              <ArrowLeftRight className="w-5 h-5" />
            </div>
          ) : type === "income" ? (
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-xl bg-slate-100 text-slate-800 flex items-center justify-center">
              <ReceiptText className="w-5 h-5" />
            </div>
          )}
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {isEditMode
                ? "Editar Lançamento"
                : type === "transfer"
                ? "Transferência entre Contas Próprias"
                : type === "income"
                ? "Nova Receita / Recebível Avulso"
                : "Nova Despesa"}
            </h2>
            <p className="text-xs text-slate-500">
              {type === "transfer"
                ? "Movimentação neutra de recursos entre bancos ou carteiras (Ativo ➔ Ativo)"
                : type === "income"
                ? "Freelances, consultorias, reembolsos, bônus e recebíveis futuros"
                : "Gastos, contas a pagar, compras à vista ou parceladas"}
            </p>
          </div>
        </div>

        {type === "transfer" && (
          <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-2xl text-[11px] text-indigo-900 leading-relaxed">
            💡 <b>Neutro Financeiramente:</b> O valor transferido reduzirá o saldo da conta de origem e aumentará a conta de destino, sem inflacionar artificialmente suas receitas ou despesas nos relatórios e DRE.
          </div>
        )}

        {error && (
          <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {type === "transfer" ? "Descrição / Finalidade da Transferência" : "Descrição"}
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={
                type === "transfer"
                  ? "Ex: Transferência Pró-labore para Sicoob, Aporte em Investimento..."
                  : type === "income"
                  ? "Ex: Consultoria Cliente X, Freelance Design, Restituição IR..."
                  : "Ex: Supermercado, Farmácia, Restaurante..."
              }
              required={type !== "transfer"}
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
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {type === "transfer" ? "Data da Transferência" : "Data (Início / 1ª Parcela)"}
              </label>
              <input
                type="date"
                value={transactionDate}
                onChange={(e) => setTransactionDate(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm"
              />
            </div>
          </div>

          {type === "transfer" ? (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Conta de Origem (Saída):
                </label>
                <select
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-semibold"
                  required
                >
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.type === "credit_card" ? "💳 " : "🏦 "} {a.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Conta de Destino (Entrada):
                </label>
                <select
                  value={destinationAccountId}
                  onChange={(e) => setDestinationAccountId(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-semibold"
                  required
                >
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id} disabled={a.id === accountId}>
                      {a.type === "credit_card" ? "💳 " : "🏦 "} {a.name} {a.id === accountId ? "(Origem)" : ""}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Tipo</label>
                  <select
                    value={type}
                    onChange={(e: any) => setType(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold"
                  >
                    <option value="income">Receita / Recebível</option>
                    <option value="expense">Despesa</option>
                    <option value="debt_payment">Pagamento de Dívida</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Status da Entrada / Saída</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-emerald-700"
                  >
                    <option value="paid">{type === "income" ? "Já Recebido (Na Conta)" : "Já Pago"}</option>
                    <option value="pending">{type === "income" ? "A Receber (Previsão Futura)" : "A Pagar (Pendente)"}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    {type === "income" ? "Conta de Depósito" : "Conta / Cartão"}
                  </label>
                  <select
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs"
                  >
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.type === "credit_card" ? "💳 Cartão: " : "🏦 Conta: "}
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    {type === "income" ? "Quem Recebeu" : "Quem Pagou"}
                  </label>
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
            </>
          )}

          {/* Calculadora Opcional de Taxa do Cartão para Boletos/Despesas */}
          {type === "expense" && accounts.find((a) => a.id === accountId)?.type === "credit_card" && (
            <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-2xl space-y-2 animate-in fade-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900">
                  <CreditCard className="w-3.5 h-3.5 text-blue-600" />
                  <span>Pagamento de Boleto/Conta no Cartão com Taxa</span>
                </div>
                <label className="flex items-center gap-1 cursor-pointer text-xs font-semibold text-blue-800">
                  <input
                    type="checkbox"
                    checked={hasCardFee}
                    onChange={(e) => {
                      const next = e.target.checked;
                      setHasCardFee(next);
                      if (next && amount) {
                        const base = parseFloat(amount) || 0;
                        const fee = (base * (parseFloat(cardFeePercentage) || 5.0)) / 100;
                        setAmount((base + fee).toFixed(2));
                      }
                    }}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Aplicar Taxa</span>
                </label>
              </div>
              {hasCardFee && (
                <div className="flex items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-600 font-medium">Taxa do App (%):</span>
                    <input
                      type="number"
                      step="0.1"
                      value={cardFeePercentage}
                      onChange={(e) => setCardFeePercentage(e.target.value)}
                      className="w-16 px-2 py-1 rounded-lg border border-blue-200 bg-white text-xs font-bold text-slate-800 font-mono"
                    />
                    <span className="font-bold text-slate-400">%</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const base = parseFloat(amount) || 0;
                      const fee = (base * (parseFloat(cardFeePercentage) || 5.0)) / 100;
                      setAmount((base + fee).toFixed(2));
                    }}
                    className="px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px] hover:bg-blue-700 transition-colors"
                  >
                    Recalcular (+{cardFeePercentage}%)
                  </button>
                </div>
              )}
            </div>
          )}

          {type !== "transfer" && (
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Categoria</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs"
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
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs"
                >
                  {costCenters.map((cc) => (
                    <option key={cc.id} value={cc.id}>
                      {cc.name} ({cc.scope})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  {type === "income" ? "Natureza da Renda" : "Classificação (50-30-20)"}
                </label>
                <select
                  value={essentiality}
                  onChange={(e) => setEssentiality(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-semibold"
                >
                  {type === "income" ? (
                    <>
                      <option value="essential">💼 Renda Principal (Salário/Pró-labore)</option>
                      <option value="lifestyle">🤝 Renda Extra / Freelance</option>
                      <option value="debt">🎁 Bônus / PLR / 13º</option>
                      <option value="waste">🏠 Aluguel / Investimentos / Reembolso</option>
                    </>
                  ) : (
                    <>
                      <option value="essential">🏠 Essencial (50%)</option>
                      <option value="lifestyle">🍿 Estilo de Vida (30%)</option>
                      <option value="debt">💳 Dívida / Encargos (20%)</option>
                      <option value="waste">⚠️ Ralo / Desperdício</option>
                    </>
                  )}
                </select>
              </div>
            </div>
          )}

          {/* Parcelamento (apenas no modo criação e não-transferência) */}
          {!isEditMode && type !== "transfer" && (
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {type === "income" ? "Parcelamento do Recebível (1x a 120x)" : "Parcelamento da Compra (1x a 120x)"}
              </label>
              <input
                type="number"
                min="1"
                max="120"
                value={totalInstallments}
                onChange={(e) => setTotalInstallments(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-mono"
              />
              <p className="text-[10px] text-slate-400 mt-1">
                Ex: Se o cliente vai pagar em 3x, as parcelas 2 e 3 serão criadas automaticamente como "A Receber" nos próximos meses.
              </p>
            </div>
          )}

          {/* Campo Dedicado de Tags (não-transferência) */}
          {type !== "transfer" && (
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <label className="block text-xs font-bold text-slate-700">Tags do Projeto / Cliente / Evento</label>
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
                  placeholder="Criar nova tag (ex: #ProjetoFreelance)..."
                  className="flex-1 px-3 py-1.5 rounded-xl border border-slate-300 text-xs bg-white"
                />
                <button
                  type="button"
                  onClick={handleCreateTag}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 text-white font-bold text-xs hover:bg-slate-900 cursor-pointer"
                >
                  + Criar Tag
                </button>
              </div>
            </div>
          )}

          {/* Campo de Anotações / Observações */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1.5">
              <StickyNote className="w-3.5 h-3.5 text-amber-600" />
              <span>Anotações / Observações (Opcional)</span>
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Adicione detalhes, observações ou comprovante para facilitar a identificação manual futura..."
              rows={2}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-400 focus:border-amber-400 resize-none font-medium text-slate-700 bg-amber-50/20"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-xl text-white font-bold text-sm shadow-md transition-colors cursor-pointer disabled:opacity-50 ${
              type === "transfer"
                ? "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-500/20"
                : "bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20"
            }`}
          >
            {loading
              ? "Salvando..."
              : isEditMode
              ? "Salvar Alterações"
              : type === "transfer"
              ? "Confirmar Transferência entre Contas"
              : type === "income"
              ? "Salvar Receita"
              : "Salvar Despesa"}
          </button>
        </form>
      </div>
    </div>
  );
}
