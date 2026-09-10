"use client";

import React from "react";
import Link from "next/link";
import { Wallet, Settings2, ReceiptText } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface BankAccountCardProps {
  account: any;
  onEdit: (account: any) => void;
}

export function BankAccountCard({ account, onEdit }: BankAccountCardProps) {
  const currentBal = parseFloat(account.current_balance || 0);
  const isNegative = currentBal < 0;

  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:border-slate-300 transition-all">
      <div className="space-y-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Wallet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base leading-snug">{account.name}</h3>
              <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                {account.type === "checking"
                  ? "Conta Corrente"
                  : account.type === "investment"
                  ? "Investimentos"
                  : "Carteira / Dinheiro"}
              </span>
            </div>
          </div>
          <button
            onClick={() => onEdit(account)}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            title="Editar Conta"
          >
            <Settings2 className="w-4 h-4" />
          </button>
        </div>

        {/* Caixa de Saldo em Tempo Real */}
        <div
          className={`p-4 rounded-2xl ${
            isNegative ? "bg-red-50/70 border border-red-100" : "bg-slate-50 border border-slate-100"
          } space-y-1`}
        >
          <span className="text-xs text-slate-500 font-semibold block">Saldo em Tempo Real</span>
          <div
            className={`text-2xl font-extrabold ${
              isNegative ? "text-red-600" : "text-slate-900"
            } tracking-tight`}
          >
            {formatCurrency(currentBal)}
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 flex justify-between items-center">
        <div>
          <span className="text-[10px] text-slate-400 block uppercase font-semibold">Saldo Inicial</span>
          <span className="font-bold text-slate-700">
            {formatCurrency(account.initial_balance)}
          </span>
        </div>
        <Link
          href={`/transactions?account_id=${account.id}`}
          className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition-colors"
        >
          <ReceiptText className="w-3.5 h-3.5 text-emerald-600" />
          <span>Ver Extrato</span>
        </Link>
      </div>
    </div>
  );
}
