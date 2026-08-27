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
  Building2
} from "lucide-react";

export default function ImportPage() {
  const { activeWorkspace } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState("");
  const [selectedMemberId, setSelectedMemberId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    if (!activeWorkspace) return;
    try {
      const [accRes, wsRes, ccRes] = await Promise.all([
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}`),
        api.get(`/workspaces/${activeWorkspace.id}/cost-centers`),
      ]);

      setAccounts(accRes.data);
      setMembers(wsRes.data.members || []);
      setCostCenters(ccRes.data);

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

    try {
      const res = await api.post(`/workspaces/${activeWorkspace?.id}/import/parse`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setParsedData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao processar arquivo OFX/CSV.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!parsedData || !parsedData.candidates) return;
    setLoading(true);
    setError("");

    try {
      const defaultCcId = costCenters.length > 0 ? costCenters[0].id : null;

      for (const cand of parsedData.candidates) {
        await api.post(`/workspaces/${activeWorkspace?.id}/transactions`, {
          account_id: selectedAccountId,
          paid_by_member_id: selectedMemberId,
          cost_center_id: defaultCcId,
          category_id: cand.suggested_category_id,
          amount: cand.amount,
          type: cand.type,
          essentiality: cand.suggested_essentiality,
          transaction_date: cand.transaction_date,
          description: cand.description,
          status: "paid",
        });
      }

      setSuccessMsg(`Sucesso! ${parsedData.candidates.length} transações foram conciliadas e importadas.`);
      setParsedData(null);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar transações importadas.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Importação & Conciliação de Extratos</h1>
          <p className="text-xs text-slate-500">
            Importe arquivos .OFX ou .CSV do seu banco com sugestão automática de categorias por IA
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
                Conta Bancária de Destino:
              </label>
              <select
                value={selectedAccountId}
                onChange={(e) => setSelectedAccountId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800"
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} ({a.type === "checking" ? "Conta Corrente" : "Cartão"})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Titular / Quem Pagou:
              </label>
              <select
                value={selectedMemberId}
                onChange={(e) => setSelectedMemberId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800"
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
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800">
                Selecione ou arraste seu extrato (.OFX ou .CSV)
              </p>
              <p className="text-xs text-slate-400">
                Compatível com Nubank, Itaú, Bradesco, Banco do Brasil, Inter, Sicoob, Caixa e outros.
              </p>
            </div>

            <label className="inline-block px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs cursor-pointer shadow-md transition-colors">
              <span>Procurar Arquivo</span>
              <input
                type="file"
                accept=".ofx,.csv"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {loading && (
              <div className="flex items-center justify-center gap-2 text-xs font-semibold text-emerald-600 pt-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processando arquivo e classificando transações...</span>
              </div>
            )}
          </div>
        </div>

        {/* 2. Pré-visualização da Conciliação */}
        {parsedData && (
          <div className="bg-white rounded-3xl border border-slate-200 shadow-xs p-6 md:p-8 space-y-6 animate-in fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 text-emerald-600 font-bold text-xs uppercase tracking-wider">
                  <Sparkles className="w-4 h-4" />
                  <span>Conciliação Pronta ({parsedData.format})</span>
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  {parsedData.total_found} transações encontradas em "{parsedData.filename}"
                </h3>
              </div>

              <button
                onClick={handleConfirmImport}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-colors cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Confirmar e Importar no Extrato</span>
              </button>
            </div>

            {/* Tabela de Pré-visualização */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Data</th>
                    <th className="py-3 px-4">Descrição Original</th>
                    <th className="py-3 px-4">Categoria Sugerida</th>
                    <th className="py-3 px-4">Essencialidade</th>
                    <th className="py-3 px-4 text-right">Valor</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {parsedData.candidates?.map((cand: any, idx: number) => {
                    const isIncome = cand.type === "income";
                    return (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-3 px-4 font-mono text-slate-500 whitespace-nowrap">
                          {cand.transaction_date}
                        </td>
                        <td className="py-3 px-4 font-bold text-slate-800">{cand.description}</td>
                        <td className="py-3 px-4">
                          <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 font-bold border border-emerald-200 text-[11px]">
                            {cand.suggested_category_name}
                          </span>
                        </td>
                        <td className="py-3 px-4 uppercase text-[10px] font-bold text-slate-500">
                          {cand.suggested_essentiality}
                        </td>
                        <td
                          className={`py-3 px-4 text-right font-mono font-extrabold whitespace-nowrap ${
                            isIncome ? "text-emerald-600" : "text-slate-900"
                          }`}
                        >
                          {isIncome ? "+" : "-"} R${" "}
                          {parseFloat(cand.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
