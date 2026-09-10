"use client";

import React from "react";
import Link from "next/link";
import { CreditCard, Settings2, ReceiptText, ArrowRightLeft } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface CreditCardCardProps {
  card: any;
  onEdit: (card: any) => void;
  onPayInvoice: (card: any) => void;
}

export function CreditCardCard({ card, onEdit, onPayInvoice }: CreditCardCardProps) {
  const totalLimit = parseFloat(card.credit_limit || 0);
  const usedLimit = parseFloat(card.used_limit || 0);
  const availableLimit = parseFloat(card.available_limit || 0);
  const usedPercentage = totalLimit > 0 ? Math.min(100, Math.round((usedLimit / totalLimit) * 100)) : 0;

  let progressColor = "bg-emerald-500";
  if (usedPercentage > 80) progressColor = "bg-red-500";
  else if (usedPercentage > 50) progressColor = "bg-amber-500";

  return (
    <div className="p-6 rounded-3xl bg-white border border-purple-100 shadow-xs flex flex-col justify-between space-y-4 relative overflow-hidden hover:border-purple-200 transition-all">
      {/* Barra de destaque superior */}
      <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-purple-500 to-indigo-600" />

      <div className="space-y-4">
        {/* Topo do Card */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base leading-snug">{card.name}</h3>
              <span className="text-[10px] uppercase font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-100">
                Cartão de Crédito
              </span>
            </div>
          </div>
          <button
            onClick={() => onEdit(card)}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            title="Ajustar Limite / Configurações"
          >
            <Settings2 className="w-4 h-4" />
          </button>
        </div>

        {/* Caixa de Limite Disponível */}
        <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100/80 space-y-1">
          <span className="text-xs text-emerald-800 font-semibold block">Limite Disponível</span>
          <div className="text-2xl font-extrabold text-emerald-700 tracking-tight">
            {formatCurrency(availableLimit)}
          </div>
        </div>

        {/* Barra de Progresso do Limite */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-500">Limite Usado ({usedPercentage}%)</span>
            <span className="text-slate-800 font-bold">
              {formatCurrency(usedLimit)}
            </span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full ${progressColor} transition-all duration-500 rounded-full`}
              style={{ width: `${usedPercentage}%` }}
            />
          </div>
        </div>

        {/* Detalhes de Fechamento e Vencimento */}
        <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-1.5">
          <div className="flex justify-between">
            <span>Limite Total:</span>
            <span className="font-bold text-slate-800">
              {formatCurrency(totalLimit)}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Fechamento / Vencimento:</span>
            <span className="font-bold text-slate-800">
              Dia {card.closing_day || 5} • Dia {card.due_day || 12}
            </span>
          </div>
        </div>
      </div>

      {/* Botões de Fatura e Pagamento */}
      <div className="grid grid-cols-2 gap-2 mt-2">
        <Link
          href={`/transactions?account_id=${card.id}`}
          className="py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
        >
          <ReceiptText className="w-3.5 h-3.5 text-purple-600" />
          <span>Ver Fatura</span>
        </Link>
        <button
          onClick={() => onPayInvoice(card)}
          className="py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-md shadow-purple-500/20 flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
        >
          <ArrowRightLeft className="w-3.5 h-3.5" />
          <span>Pagar Fatura</span>
        </button>
      </div>
    </div>
  );
}
