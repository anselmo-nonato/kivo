"use client";

import React from "react";
import { TransactionRow } from "./TransactionRow";

interface TransactionTableProps {
  transactions: any[];
  accounts: any[];
  showNotes: boolean;
  onOpenEdit: (tx: any) => void;
  onDelete: (txId: string) => void;
  onConfirm: (txId: string) => void;
}

export function TransactionTable({
  transactions,
  accounts,
  showNotes,
  onOpenEdit,
  onDelete,
  onConfirm,
}: TransactionTableProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50/90 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-4 w-28 whitespace-nowrap">Data</th>
              <th className="py-3 px-4 min-w-[280px]">Descrição & Contas</th>
              <th className="py-3 px-4 w-36">Tags</th>
              <th className="py-3 px-4 w-44 whitespace-nowrap">Status / Tipo</th>
              <th className="py-3 px-4 w-24 text-center whitespace-nowrap">Parcela</th>
              <th className="py-3 px-4 w-36 text-right whitespace-nowrap">Valor</th>
              <th className="py-3 px-4 w-28 text-right whitespace-nowrap">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium">
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  Nenhum lançamento encontrado para o período ou filtros selecionados.
                </td>
              </tr>
            ) : (
              transactions.map((tx) => (
                <TransactionRow
                  key={tx.id}
                  tx={tx}
                  accounts={accounts}
                  showNotes={showNotes}
                  onOpenEdit={onOpenEdit}
                  onDelete={onDelete}
                  onConfirm={onConfirm}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
