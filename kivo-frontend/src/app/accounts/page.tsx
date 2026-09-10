"use client";

import React, { useState, useEffect } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  CreditCard,
  Plus,
  CheckCircle2,
  Landmark,
} from "lucide-react";
import { CardsExecutiveSummary } from "@/components/accounts/CardsExecutiveSummary";
import { CreditCardCard } from "@/components/accounts/CreditCardCard";
import { BankAccountCard } from "@/components/accounts/BankAccountCard";
import { PayInvoiceModal } from "@/components/accounts/PayInvoiceModal";
import { CreateAccountModal } from "@/components/accounts/CreateAccountModal";
import { EditAccountModal } from "@/components/accounts/EditAccountModal";

export default function AccountsPage() {
  const { activeWorkspace } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [cardsSummary, setCardsSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Modais
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedCardForPayment, setSelectedCardForPayment] = useState<any | null>(null);
  const [selectedAccountForEdit, setSelectedAccountForEdit] = useState<any | null>(null);

  const [successMessage, setSuccessMessage] = useState("");

  const showSuccess = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(""), 4000);
  };

  const loadData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const [accRes, wsRes, cardsSumRes] = await Promise.allSettled([
        api.get(`/workspaces/${activeWorkspace.id}/accounts`),
        api.get(`/workspaces/${activeWorkspace.id}`),
        api.get(`/workspaces/${activeWorkspace.id}/cards/summary`),
      ]);
      if (accRes.status === "fulfilled") setAccounts(accRes.value.data);
      if (wsRes.status === "fulfilled") {
        setMembers(wsRes.value.data.members || []);
      }
      if (cardsSumRes.status === "fulfilled") setCardsSummary(cardsSumRes.value.data);
    } catch (err) {
      console.error("Erro ao carregar contas:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspace]);

  const bankAccounts = accounts.filter((a) => a.type !== "credit_card");
  const creditCards = accounts.filter((a) => a.type === "credit_card");

  return (
    <AppLayout>
      <div className="space-y-8 pb-12">
        {/* Notificação de Sucesso */}
        {successMessage && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold flex items-center gap-2.5 animate-in fade-in">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Cabeçalho da Página */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900">Contas Bancárias & Cartões</h1>
            <p className="text-xs text-slate-500">
              Gerencie seus bancos, saldos disponíveis, limites de cartões e faturas
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Adicionar Conta / Cartão</span>
          </button>
        </div>

        {/* SEÇÃO 1: CARTÕES DE CRÉDITO */}
        {creditCards.length > 0 && (
          <div className="space-y-6">
            {/* Banner Executivo Consolidado dos Cartões */}
            <CardsExecutiveSummary
              cardsSummary={cardsSummary}
              creditCardsCount={creditCards.length}
            />

            {/* Lista de Cartões Individuais */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center">
                  <CreditCard className="w-4 h-4" />
                </div>
                <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-700">
                  Cartões Individuais ({creditCards.length})
                </h2>
              </div>
              <span className="text-xs text-slate-400 font-medium">Controle de limites e faturas individuais</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {creditCards.map((card) => (
                <CreditCardCard
                  key={card.id}
                  card={card}
                  onEdit={setSelectedAccountForEdit}
                  onPayInvoice={setSelectedCardForPayment}
                />
              ))}
            </div>
          </div>
        )}

        {/* SEÇÃO 2: CONTAS BANCÁRIAS & CARTEIRAS */}
        <div className="space-y-4 pt-6 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
                <Landmark className="w-4 h-4" />
              </div>
              <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-700">
                Contas Correntes, Carteiras & Investimentos ({bankAccounts.length})
              </h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Saldos monetários líquidos</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {bankAccounts.map((acc) => (
              <BankAccountCard
                key={acc.id}
                account={acc}
                onEdit={setSelectedAccountForEdit}
              />
            ))}
          </div>
        </div>

        {/* Modal de Pagamento de Fatura */}
        {activeWorkspace && (
          <PayInvoiceModal
            card={selectedCardForPayment}
            bankAccounts={bankAccounts}
            activeWorkspaceId={activeWorkspace.id}
            onClose={() => setSelectedCardForPayment(null)}
            onSuccess={(amt) => {
              showSuccess(
                `Fatura de R$ ${amt.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} paga com sucesso! Limite restaurado.`
              );
              loadData();
            }}
          />
        )}

        {/* Modal de Edição / Ajuste */}
        {activeWorkspace && (
          <EditAccountModal
            account={selectedAccountForEdit}
            activeWorkspaceId={activeWorkspace.id}
            onClose={() => setSelectedAccountForEdit(null)}
            onSuccess={() => {
              showSuccess("Conta atualizada com sucesso!");
              loadData();
            }}
          />
        )}

        {/* Modal de Criação */}
        {activeWorkspace && (
          <CreateAccountModal
            isOpen={isCreateModalOpen}
            members={members}
            activeWorkspaceId={activeWorkspace.id}
            onClose={() => setIsCreateModalOpen(false)}
            onSuccess={() => {
              showSuccess("Conta cadastrada com sucesso!");
              loadData();
            }}
          />
        )}
      </div>
    </AppLayout>
  );
}
