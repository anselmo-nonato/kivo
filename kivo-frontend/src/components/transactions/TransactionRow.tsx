"use client";

import React from "react";
import {
  CreditCard,
  ArrowDownLeft,
  ArrowUpRight,
  ArrowLeftRight,
  StickyNote,
  CheckCircle2,
  Clock,
  Pencil,
  Trash2,
} from "lucide-react";
import { cleanUserNotes } from "@/lib/utils";

interface TransactionRowProps {
  tx: any;
  accounts: any[];
  showNotes: boolean;
  onOpenEdit: (tx: any) => void;
  onDelete: (txId: string) => void;
  onConfirm: (txId: string) => void;
}

export function TransactionRow({
  tx,
  accounts,
  showNotes,
  onOpenEdit,
  onDelete,
  onConfirm,
}: TransactionRowProps) {
  const isTransfer = tx.type === "transfer";
  const isIncome = tx.type === "income";
  const isPending = tx.status === "pending";
  const isOutflowTransfer = isTransfer && tx.transfer_direction === "outflow";
  const isInflowTransfer = isTransfer && tx.transfer_direction === "inflow";

  const accName = tx.account_name || accounts.find((a) => a.id === tx.account_id)?.name || "Conta";
  const destAccName = tx.destination_account_name || accounts.find((a) => a.id === tx.destination_account_id)?.name;

  const isInvoicePayment =
    tx.description?.toLowerCase().includes("fatura") ||
    tx.description?.toLowerCase().includes("crédito pagamento");
  const userNotes = cleanUserNotes(tx.notes);
  const hasNotes = userNotes.length > 0;

  return (
    <tr
      className={`hover:bg-slate-50/80 transition-colors ${
        isPending ? "bg-amber-50/30" : isTransfer ? "bg-slate-50/30" : ""
      }`}
    >
      <td className="py-2.5 px-4 font-mono text-slate-500 whitespace-nowrap text-[11px]">
        {tx.transaction_date}
      </td>
      <td className="py-2.5 px-4">
        <div className="flex items-center gap-1.5 flex-wrap">
          {isInvoicePayment ? (
            <CreditCard className="w-3.5 h-3.5 text-purple-600 shrink-0" />
          ) : isTransfer ? (
            <ArrowLeftRight className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
          ) : isIncome ? (
            <ArrowDownLeft className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          ) : (
            <ArrowUpRight className="w-3.5 h-3.5 text-red-500 shrink-0" />
          )}
          <span className="font-bold text-slate-800 text-xs">{tx.description}</span>
        </div>

        <div className="text-[10px] text-slate-400 pl-5 flex items-center gap-1.5 mt-0.5">
          {isTransfer ? (
            <span className="font-semibold text-slate-600">
              🏦 {accName} {isOutflowTransfer ? "➔ 🏦 " + (destAccName || "Destino") : "⬅ 🏦 " + (destAccName || "Origem")}
            </span>
          ) : (
            <span>{accName}</span>
          )}
        </div>

        {/* Modo Visível Expandido */}
        {showNotes && hasNotes && (
          <div className="mt-1.5 ml-5 p-2 rounded-xl bg-amber-50/90 border border-amber-200/90 text-amber-950 text-xs flex items-start gap-1.5 max-w-lg shadow-2xs">
            <StickyNote className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <span className="font-semibold text-[9px] uppercase text-amber-800 tracking-wider block">
                Anotação:
              </span>
              <p className="font-medium whitespace-pre-wrap text-amber-900 leading-relaxed text-[11px]">
                {userNotes}
              </p>
            </div>
          </div>
        )}
      </td>
      <td className="py-2.5 px-4">
        <div className="flex flex-wrap gap-1">
          {tx.tags?.map((t: any) => (
            <span
              key={t.id}
              className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-600 border border-blue-200"
            >
              #{t.name}
            </span>
          ))}
        </div>
      </td>
      <td className="py-2.5 px-4 whitespace-nowrap">
        {isTransfer ? (
          isInvoicePayment ? (
            isOutflowTransfer ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
                <CreditCard className="w-3 h-3 text-purple-500" />
                <span>Pagamento Fatura</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
                <CreditCard className="w-3 h-3 text-purple-500" />
                <span>Restauração Limite</span>
              </span>
            )
          ) : isOutflowTransfer ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-300">
              <ArrowLeftRight className="w-3 h-3 text-slate-500" />
              <span>Transf. Enviada</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
              <ArrowLeftRight className="w-3 h-3 text-indigo-500" />
              <span>Transf. Recebida</span>
            </span>
          )
        ) : isPending ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
            <Clock className="w-3 h-3" />
            <span>{isIncome ? "A Receber" : "A Pagar"}</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3 h-3" />
            <span>{isIncome ? "Recebido" : "Pago"}</span>
          </span>
        )}
      </td>
      <td className="py-2.5 px-4 font-mono text-slate-400 whitespace-nowrap text-center text-xs">
        {tx.installment_total > 1
          ? `${tx.installment_current}/${tx.installment_total}`
          : isTransfer
          ? "Neutro"
          : "À vista"}
      </td>
      <td
        className={`py-2.5 px-4 text-right font-extrabold whitespace-nowrap font-mono text-xs ${
          isInflowTransfer
            ? "text-indigo-600 font-bold"
            : isOutflowTransfer
            ? "text-slate-700"
            : isIncome
            ? "text-emerald-600 font-bold"
            : "text-slate-900"
        }`}
      >
        {isIncome || isInflowTransfer ? "+" : "-"} R${" "}
        {parseFloat(tx.amount).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
      </td>
      <td className="py-2.5 px-4 text-right whitespace-nowrap">
        <div className="flex items-center justify-end gap-1">
          {/* Botão de Efetivar / Baixa Rápida */}
          {isPending && (
            <button
              onClick={() => onConfirm(tx.id)}
              className={`px-2 py-0.5 rounded-lg text-[11px] font-bold text-white flex items-center gap-1 transition-colors cursor-pointer ${
                isIncome ? "bg-emerald-600 hover:bg-emerald-700" : "bg-blue-600 hover:bg-blue-700"
              }`}
              title={isIncome ? "Confirmar Recebimento do Valor" : "Confirmar Pagamento Realizado"}
            >
              <CheckCircle2 className="w-3 h-3" />
              <span>{isIncome ? "Receber" : "Efetivar"}</span>
            </button>
          )}

          {/* Botão de Anotação (ao lado do lápis de editar) */}
          <div className="relative group/note inline-flex items-center">
            <button
              type="button"
              onClick={() => onOpenEdit(tx)}
              className={`p-1 rounded-md transition-colors cursor-pointer ${
                hasNotes
                  ? "bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200 shadow-2xs"
                  : "text-slate-300 hover:text-slate-600 hover:bg-slate-100"
              }`}
              title={hasNotes ? "Ver / Editar anotação" : "Adicionar anotação"}
            >
              <StickyNote
                className={`w-3.5 h-3.5 ${
                  hasNotes
                    ? "fill-amber-400 text-amber-700"
                    : "text-slate-300 group-hover/note:text-slate-600"
                }`}
              />
            </button>

            {/* Tooltip flutuante no hover */}
            <div className="absolute right-0 bottom-full mb-2 hidden group-hover/note:flex flex-col z-40 w-72 p-3 bg-slate-900 text-white rounded-2xl shadow-2xl border border-slate-700 pointer-events-none animate-in fade-in zoom-in-95 text-left whitespace-normal">
              <div className="flex items-center gap-1.5 text-[10px] font-bold mb-1 uppercase tracking-wider text-amber-400">
                <StickyNote className="w-3 h-3 text-amber-400" />
                <span>{hasNotes ? "Anotação do Lançamento" : "Sem Anotação"}</span>
              </div>
              <p className="text-xs text-slate-200 font-normal whitespace-pre-wrap leading-relaxed">
                {hasNotes ? userNotes : "Nenhuma anotação vinculada. Clique para adicionar."}
              </p>
              <div className="text-[9px] text-slate-400 mt-2 pt-1.5 border-t border-slate-800 flex items-center justify-between">
                <span>{hasNotes ? "Clique para editar" : "Clique para adicionar"}</span>
                <span>📝 KIVO</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onOpenEdit(tx)}
            className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer"
            title="Editar Transação"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onDelete(tx.id)}
            className="p-1 rounded-md hover:bg-red-50 text-slate-400 hover:text-red-600 cursor-pointer"
            title="Excluir Transação"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </td>
    </tr>
  );
}
