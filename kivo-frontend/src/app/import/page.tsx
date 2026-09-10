"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Loader2,
  Building2,
  FileText,
  Calendar,
  Wallet,
  CheckSquare,
  Square,
  Filter,
  ShieldCheck,
  AlertTriangle,
  ArrowLeftRight
} from "lucide-react";

export default function ImportPage() {
  const { activeWorkspace } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState("");
  const [selectedMemberId, setSelectedMemberId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<any>(null);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    if (!activeWorkspace) return;
    try {
      const [accRes, wsRes, ccRes, catRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}`),
        api.get(`/workspaces/${activeWorkspace.id}/cost-centers`),
        api.get(`/workspaces/${activeWorkspace.id}/categories`),
      ]);

      setAccounts(accRes.data);
      setMembers(wsRes.data.members || []);
      setCostCenters(ccRes.data);
      setCategories(catRes.data);

      if (accRes.data.length > 0) setSelectedAccountId(accRes.data[0].id);
      if (wsRes.data.members?.length > 0) setSelectedMemberId(wsRes.data.members[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    setError("");
    setSuccessMsg("");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);
    if (selectedAccountId) {
      formData.append("account_id", selectedAccountId);
    }

    try {
      const res = await api.post(`/workspaces/${activeWorkspace?.id}/import/parse`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const data = res.data;
      setParsedData(data);

      // Auto-seleciona apenas transações reais que NÃO são duplicadas
      const initialSelected = new Set<number>();
      data.candidates?.forEach((c: any, idx: number) => {
        if (!c.is_duplicate && !c.is_future) {
          initialSelected.add(idx);
        }
      });
      setSelectedIndices(initialSelected);

    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao processar arquivo (PDF/OFX/CSV).");
    } finally {
      setLoading(false);
    }
  };

  const toggleSelectIndex = (idx: number) => {
    const next = new Set(selectedIndices);
    if (next.has(idx)) {
      next.delete(idx);
    } else {
      next.add(idx);
    }
    setSelectedIndices(next);
  };

  const selectOnlyNew = () => {
    const next = new Set<number>();
    parsedData?.candidates?.forEach((c: any, idx: number) => {
      if (!c.is_duplicate && !c.is_future) next.add(idx);
    });
    setSelectedIndices(next);
  };

  const selectAll = () => {
    const next = new Set<number>();
    parsedData?.candidates?.forEach((_: any, idx: number) => next.add(idx));
    setSelectedIndices(next);
  };

  const deselectAll = () => {
    setSelectedIndices(new Set());
  };

  const handleCategoryChange = (idx: number, catId: string) => {
    if (!parsedData) return;
    const catObj = categories.find((c) => c.id === catId);
    const updatedCandidates = [...parsedData.candidates];
    updatedCandidates[idx] = {
      ...updatedCandidates[idx],
      suggested_category_id: catId,
      suggested_category_name: catObj ? catObj.name : updatedCandidates[idx].suggested_category_name,
    };
    setParsedData({ ...parsedData, candidates: updatedCandidates });
  };

  const handleTypeChange = (idx: number, newType: string, destAccId?: string) => {
    if (!parsedData) return;
    const updatedCandidates = [...parsedData.candidates];
    updatedCandidates[idx] = {
      ...updatedCandidates[idx],
      type: newType,
      destination_account_id: destAccId !== undefined ? destAccId : updatedCandidates[idx].destination_account_id,
    };
    setParsedData({ ...parsedData, candidates: updatedCandidates });
  };

  const handleConfirmImport = async () => {
    if (!parsedData || !parsedData.candidates) return;
    const toImport = parsedData.candidates.filter((_: any, idx: number) => selectedIndices.has(idx));
    if (toImport.length === 0) {
      setError("Nenhuma transação selecionada para importação.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const defaultCcId = costCenters.length > 0 ? costCenters[0].id : null;
      const defaultCatId = categories.length > 0 ? categories[0].id : null;

      for (const cand of toImport) {
        if (cand.type === "transfer" && cand.destination_account_id) {
          // Transferência entre contas próprias
          await api.post(`/workspaces/${activeWorkspace?.id}/transfers`, {
            source_account_id: cand.transfer_direction === "inflow" ? cand.destination_account_id : selectedAccountId,
            destination_account_id: cand.transfer_direction === "inflow" ? selectedAccountId : cand.destination_account_id,
            amount: cand.amount,
            transaction_date: cand.transaction_date,
            paid_by_member_id: selectedMemberId,
            description: cand.description,
            notes: cand.notes,
          });
        } else {
          await api.post(`/workspaces/${activeWorkspace?.id}/transactions`, {
            account_id: selectedAccountId,
            paid_by_member_id: selectedMemberId,
            cost_center_id: defaultCcId,
            category_id: cand.suggested_category_id || defaultCatId,
            amount: cand.amount,
            type: cand.type,
            essentiality: cand.suggested_essentiality,
            transaction_date: cand.transaction_date,
            description: cand.description,
            notes: cand.notes,
            status: "paid",
          });
        }
      }

      setSuccessMsg(`Sucesso! ${toImport.length} transações foram conciliadas e importadas.`);
      setParsedData(null);
      setFile(null);
      setSelectedIndices(new Set());
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar transações importadas.");
    } finally {
      setLoading(false);
    }
  };

  // Cálculos dos itens selecionados
  const selectedCandidates = parsedData?.candidates?.filter((_: any, idx: number) => selectedIndices.has(idx)) || [];
  const selectedIncome = selectedCandidates
    .filter((c: any) => c.type === "income")
    .reduce((acc: number, c: any) => acc + parseFloat(c.amount), 0);
  const selectedExpense = selectedCandidates
    .filter((c: any) => c.type === "expense")
    .reduce((acc: number, c: any) => acc + parseFloat(c.amount), 0);
  const selectedTransfers = selectedCandidates
    .filter((c: any) => c.type === "transfer")
    .reduce((acc: number, c: any) => acc + parseFloat(c.amount), 0);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Importação & Conciliação Bancária</h1>
          <p className="text-xs text-slate-500">
            Importe extratos PDF (Sicoob SISBR), arquivos .OFX ou .CSV com conciliação inteligente, detecção de transferências e prevenção de duplicidades.
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-bold flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* 1. Seleção de Conta de Destino e Upload */}
        <div className="p-6 md:p-8 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Conta Bancária do Extrato (Origem/Destino):
              </label>
              <select
                value={selectedAccountId}
                onChange={(e) => setSelectedAccountId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500 outline-none"
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} ({a.type === "checking" ? "Conta Corrente" : a.type === "credit_card" ? "Cartão" : "Carteira"})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Titular / Responsável Padrão:
              </label>
              <select
                value={selectedMemberId}
                onChange={(e) => setSelectedMemberId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500 outline-none"
              >
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Área de Drag & Drop */}
          <div className="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-3xl p-8 text-center space-y-3 transition-colors bg-slate-50/50">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto shadow-xs">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800">
                Arraste seu extrato bancário aqui ou clique para selecionar
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Formatos aceitos: <b>PDF do Sicoob</b>, <b>.OFX</b> de qualquer banco ou <b>.CSV</b>
              </p>
            </div>

            <label className="inline-block">
              <span className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md transition-colors cursor-pointer inline-flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4" />
                <span>Procurar Arquivo</span>
              </span>
              <input
                type="file"
                accept=".pdf,.ofx,.csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={loading}
              />
            </label>

            {loading && (
              <div className="flex items-center justify-center gap-2 text-xs font-bold text-emerald-600 pt-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processando e conciliando movimentações...</span>
              </div>
            )}
          </div>
        </div>

        {/* 2. Resultados da Leitura e Conciliação */}
        {parsedData && (
          <div className="space-y-6 animate-in fade-in">
            {/* Card de Metadados do Extrato */}
            <div className="p-6 rounded-3xl bg-slate-900 text-white shadow-xl space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold">{parsedData.filename}</h2>
                    <p className="text-[11px] text-slate-400">
                      Formato: <span className="text-emerald-400 font-semibold">{parsedData.format}</span>
                      {parsedData.detected_coop && ` • Coop: ${parsedData.detected_coop}`}
                      {parsedData.detected_account && ` • Conta: ${parsedData.detected_account}`}
                    </p>
                  </div>
                </div>

                {parsedData.period_start && parsedData.period_end && (
                  <div className="flex items-center gap-1.5 text-xs text-slate-300 font-mono bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
                    <Calendar className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{parsedData.period_start} a {parsedData.period_end}</span>
                  </div>
                )}
              </div>

              {/* Grid de Saldos do Extrato */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                <div className="p-3.5 rounded-2xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Lançamentos</span>
                  <span className="text-lg font-black text-white">{parsedData.total_found}</span>
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Total Entradas</span>
                  <span className="text-lg font-black text-emerald-400 font-mono">
                    R$ {parseFloat(parsedData.total_amount_income).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Total Saídas</span>
                  <span className="text-lg font-black text-red-400 font-mono">
                    R$ {parseFloat(parsedData.total_amount_expense).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="p-3.5 rounded-2xl bg-emerald-950/40 border border-emerald-800/40">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300 block">Saldo Oficial do Extrato</span>
                  <span className="text-lg font-black text-emerald-300 font-mono">
                    {parsedData.statement_balance !== null
                      ? `R$ ${parseFloat(parsedData.statement_balance).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`
                      : "—"}
                  </span>
                </div>
              </div>
            </div>

            {/* Ações de Seleção e Tabela */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <div>
                    <h3 className="text-sm font-extrabold text-slate-900">Pré-Conciliação de Movimentações</h3>
                    <p className="text-[11px] text-slate-500">
                      Revise o tipo (Receita, Despesa ou Transferência entre Contas) e selecione os itens que deseja importar.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={selectOnlyNew}
                    type="button"
                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold transition-colors cursor-pointer"
                  >
                    Apenas Novos ({parsedData.candidates?.filter((c: any) => !c.is_duplicate && !c.is_future).length})
                  </button>
                  <button
                    onClick={selectAll}
                    type="button"
                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold transition-colors cursor-pointer"
                  >
                    Marcar Todos
                  </button>
                  <button
                    onClick={deselectAll}
                    type="button"
                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold transition-colors cursor-pointer"
                  >
                    Desmarcar
                  </button>
                </div>
              </div>

              {/* Tabela de Candidatos */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-600">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-3 px-4 w-10 text-center">
                        <input
                          type="checkbox"
                          checked={
                            parsedData.candidates?.length > 0 &&
                            selectedIndices.size === parsedData.candidates?.length
                          }
                          onChange={(e) => {
                            if (e.target.checked) selectAll();
                            else deselectAll();
                          }}
                          className="rounded text-emerald-600 focus:ring-emerald-500 cursor-pointer"
                        />
                      </th>
                      <th className="py-3 px-4">Status / Conciliação</th>
                      <th className="py-3 px-4">Data</th>
                      <th className="py-3 px-4">Descrição & Classificação</th>
                      <th className="py-3 px-4">Categoria</th>
                      <th className="py-3 px-4">Essencialidade</th>
                      <th className="py-3 px-4 text-right">Valor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {parsedData.candidates?.map((cand: any, idx: number) => {
                      const isTransfer = cand.type === "transfer";
                      const isIncome = cand.type === "income";
                      const isSelected = selectedIndices.has(idx);

                      return (
                        <tr
                          key={idx}
                          className={`transition-colors ${
                            isSelected ? "bg-white hover:bg-slate-50/80" : "bg-slate-50/40 text-slate-400 hover:bg-slate-50"
                          }`}
                        >
                          <td className="py-3 px-4 text-center">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => toggleSelectIndex(idx)}
                              className="rounded text-emerald-600 focus:ring-emerald-500 cursor-pointer"
                            />
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap">
                            {cand.is_duplicate ? (
                              <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 font-bold border border-amber-200 text-[11px] inline-flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                <span>Já no KIVO</span>
                              </span>
                            ) : cand.is_future ? (
                              <span className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 font-bold border border-blue-200 text-[11px] inline-flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                <span>Futuro / Agendado</span>
                              </span>
                            ) : cand.is_transfer ? (
                              <span className="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 font-bold border border-indigo-200 text-[11px] inline-flex items-center gap-1">
                                <ArrowLeftRight className="w-3 h-3" />
                                <span>Transferência</span>
                              </span>
                            ) : (
                              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 font-bold border border-emerald-200 text-[11px] inline-flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" />
                                <span>Novo</span>
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 font-mono whitespace-nowrap">
                            {cand.transaction_date}
                          </td>
                          <td className="py-3 px-4">
                            <p className="font-bold text-slate-800">{cand.description}</p>
                            {cand.notes && cand.notes !== cand.description && (
                              <p className="text-[11px] text-slate-400 font-mono truncate max-w-xs" title={cand.notes}>
                                {cand.notes}
                              </p>
                            )}

                            {/* Seletor Rápido de Tipo & Conta Contraparte */}
                            <div className="flex flex-wrap items-center gap-2 mt-1">
                              <select
                                value={cand.type}
                                onChange={(e) => handleTypeChange(idx, e.target.value)}
                                className={`px-2 py-0.5 rounded-md text-[11px] font-bold border ${
                                  cand.type === "transfer"
                                    ? "bg-indigo-50 text-indigo-700 border-indigo-300"
                                    : cand.type === "income"
                                    ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                                    : "bg-slate-100 text-slate-700 border-slate-300"
                                }`}
                              >
                                <option value="transfer">🔄 Transferência entre Contas</option>
                                <option value="income">🟢 Receita / Entrada</option>
                                <option value="expense">🔴 Despesa / Saída</option>
                              </select>

                              {cand.type === "transfer" && (
                                <select
                                  value={cand.destination_account_id || cand.suggested_counterparty_account_id || ""}
                                  onChange={(e) => handleTypeChange(idx, "transfer", e.target.value)}
                                  className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-white text-slate-800 border border-indigo-200"
                                >
                                  <option value="">Selecione a outra conta...</option>
                                  {accounts
                                    .filter((a) => a.id !== selectedAccountId)
                                    .map((a) => (
                                      <option key={a.id} value={a.id}>
                                        {a.type === "credit_card" ? "💳 " : "🏦 "} {a.name}
                                      </option>
                                    ))}
                                </select>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            {cand.type === "transfer" ? (
                              <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-1 rounded-lg border border-indigo-100">
                                Transferência Própria
                              </span>
                            ) : (
                              <select
                                value={cand.suggested_category_id || ""}
                                onChange={(e) => handleCategoryChange(idx, e.target.value)}
                                className="px-2.5 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                              >
                                <option value="">{cand.suggested_category_name || "Sem categoria"}</option>
                                {categories.map((c) => (
                                  <option key={c.id} value={c.id}>
                                    {c.name}
                                  </option>
                                ))}
                              </select>
                            )}
                          </td>
                          <td className="py-3 px-4 uppercase text-[10px] font-bold">
                            {cand.type === "transfer" ? (
                              <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700">
                                NEUTRO
                              </span>
                            ) : (
                              <span
                                className={`px-2 py-0.5 rounded ${
                                  cand.suggested_essentiality === "essential"
                                    ? "bg-slate-100 text-slate-700"
                                    : cand.suggested_essentiality === "waste"
                                    ? "bg-red-100 text-red-700"
                                    : "bg-blue-100 text-blue-700"
                                }`}
                              >
                                {cand.suggested_essentiality}
                              </span>
                            )}
                          </td>
                          <td
                            className={`py-3 px-4 text-right font-mono font-extrabold whitespace-nowrap ${
                              isTransfer
                                ? "text-indigo-600 font-bold"
                                : isIncome
                                ? "text-emerald-600"
                                : "text-slate-900"
                            }`}
                          >
                            {isTransfer ? "🔄" : isIncome ? "+" : "-"} R${" "}
                            {parseFloat(cand.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Barra de Totais Selecionados */}
              <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs font-bold text-slate-600">
                <div className="flex flex-wrap items-center gap-4">
                  <span>Selecionados: <b className="text-slate-900 font-extrabold">{selectedIndices.size}</b></span>
                  <span className="text-emerald-600">
                    + Receitas: R$ {selectedIncome.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-slate-900">
                    - Despesas: R$ {selectedExpense.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                  {selectedTransfers > 0 && (
                    <span className="text-indigo-600">
                      🔄 Transferências: R$ {selectedTransfers.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} (Neutro)
                    </span>
                  )}
                </div>

                <button
                  onClick={handleConfirmImport}
                  disabled={loading || selectedIndices.size === 0}
                  className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-colors cursor-pointer"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Confirmar e Salvar {selectedIndices.size} Transações</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

