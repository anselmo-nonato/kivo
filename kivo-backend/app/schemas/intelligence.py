from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

# ==================== EQUALIZAÇÃO DE CASAL (ISSUE #8) ====================
class MemberEqualizationDetail(BaseModel):
    member_id: UUID
    display_name: str
    declared_income: Decimal
    income_percentage: Decimal
    total_shared_paid: Decimal
    fair_share_amount: Decimal
    balance: Decimal # Positivo = tem a receber; Negativo = tem a pagar

class EqualizationReportResponse(BaseModel):
    workspace_id: UUID
    period_month: str # YYYY-MM
    total_shared_expenses: Decimal
    total_combined_income: Decimal
    members: List[MemberEqualizationDetail]
    settlement_suggestion: str # Ex: "Nathália deve transferir R$ 450,00 para Anselmo"
    amount_to_transfer: Decimal
    payer_member_id: Optional[UUID] = None
    payer_name: Optional[str] = None
    receiver_member_id: Optional[UUID] = None
    receiver_name: Optional[str] = None

class EqualizationSettleRequest(BaseModel):
    payer_member_id: UUID
    receiver_member_id: UUID
    amount: Decimal = Field(..., gt=0)
    account_id: UUID
    transaction_date: date = Field(default_factory=date.today)

# ==================== DÍVIDAS E AMORTIZAÇÃO (ISSUE #9) ====================
class DebtCreateRequest(BaseModel):
    member_id: UUID
    creditor_name: str = Field(..., min_length=2, max_length=150)
    original_amount: Decimal = Field(..., gt=0)
    current_balance: Decimal = Field(..., gt=0)
    monthly_interest_rate: Decimal = Field(..., ge=0, le=1) # Ex: 0.0450 (4.5% a.m.)
    installment_amount: Decimal = Field(..., gt=0)
    remaining_installments: int = Field(..., ge=1)
    due_day: int = Field(..., ge=1, le=31)

class DebtUpdateRequest(BaseModel):
    creditor_name: Optional[str] = Field(None, min_length=2, max_length=150)
    original_amount: Optional[Decimal] = Field(None, gt=0)
    current_balance: Optional[Decimal] = Field(None, ge=0)
    monthly_interest_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    installment_amount: Optional[Decimal] = Field(None, gt=0)
    remaining_installments: Optional[int] = Field(None, ge=0)
    due_day: Optional[int] = Field(None, ge=1, le=31)

class DebtPayInstallmentRequest(BaseModel):
    account_id: UUID
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_date: Optional[date] = None

class DebtAmortizationRequest(BaseModel):
    extra_amount: Decimal = Field(..., gt=0)
    account_id: UUID
    strategy: str = Field("reduce_term", pattern="^(reduce_term|reduce_installment)$")

class DebtResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    member_id: UUID
    creditor_name: str
    original_amount: Decimal
    current_balance: Decimal
    monthly_interest_rate: Decimal
    monthly_interest_rate_percentage: Decimal
    installment_amount: Decimal
    remaining_installments: int
    due_day: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== SIMULADOR DE QUITAÇÃO (ISSUE #10) ====================
class DebtSimulationPlan(BaseModel):
    strategy_name: str # "Avalanche (Menor Juros)" vs "Bola de Neve (Mais Rápida)"
    description: str
    months_to_payoff: int
    total_interest_paid: Decimal
    total_amount_paid: Decimal
    payoff_order: List[str]

class DebtSimulationResponse(BaseModel):
    monthly_extra_budget: Decimal
    current_monthly_installments_total: Decimal
    avalanche: DebtSimulationPlan
    snowball: DebtSimulationPlan
    recommendation: str

# ==================== DIAGNÓSTICO DTI (ISSUE #11) ====================
class DTIAnalysisResponse(BaseModel):
    workspace_id: UUID
    total_monthly_income: Decimal
    total_monthly_debt_commitments: Decimal
    dti_percentage: Decimal
    classification: str # "Saudável (<20%)", "Alerta (20-35%)", "Crítico (>35%)"
    status_color: str # "#10B981" (Verde), "#F59E0B" (Amarelo), "#EF4444" (Vermelho)
    actionable_advice: str
