from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

# ==================== RADAR & TETOS ORÇAMENTÁRIOS (ISSUE #12) ====================
class BudgetLimitCreateRequest(BaseModel):
    category_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    limit_amount: Optional[Decimal] = Field(None, gt=0)
    limit_percentage_income: Optional[Decimal] = Field(None, ge=0, le=100)
    alert_threshold_percentage: Decimal = Field(default=Decimal("75.00"), ge=0, le=100)

class BudgetLimitItemResponse(BaseModel):
    id: UUID
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    cost_center_id: Optional[UUID] = None
    cost_center_name: Optional[str] = None
    limit_amount: Decimal
    spent_amount: Decimal
    percentage_consumed: Decimal
    month_progress_percentage: Decimal # % do mês decorrido
    consumption_pace_status: str # "Normal" (Verde), "Acelerado" (Amarelo), "Estourado" (Vermelho)
    status_color: str # "#10B981", "#F59E0B", "#EF4444"

class BudgetRadarResponse(BaseModel):
    workspace_id: UUID
    month: str
    total_budget_limit: Decimal
    total_spent: Decimal
    overall_percentage: Decimal
    month_progress_percentage: Decimal
    budgets: List[BudgetLimitItemResponse]

# ==================== RELATÓRIO DE DESPERDÍCIOS / RALOS (ISSUE #13) ====================
class WasteItemResponse(BaseModel):
    transaction_id: UUID
    description: str
    amount: Decimal
    transaction_date: date
    category_name: str
    annualized_impact: Decimal # amount * 12
    opportunity_cost_3_years: Decimal # Se investido a 10% a.a.

class WasteReportResponse(BaseModel):
    workspace_id: UUID
    month: str
    total_waste_month: Decimal
    total_waste_annualized: Decimal
    waste_percentage_of_expenses: Decimal
    potential_patrimony_in_5_years: Decimal
    waste_transactions: List[WasteItemResponse]

# ==================== COFRE DA RESERVA DE EMERGÊNCIA (ISSUE #14) ====================
class EmergencyFundConfig(BaseModel):
    target_months: Decimal = Field(default=Decimal("6.0"), ge=1, le=24)
    current_balance: Decimal = Field(default=Decimal("0.00"), ge=0)

class EmergencyFundDepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    account_id: UUID

class EmergencyFundStatusResponse(BaseModel):
    workspace_id: UUID
    target_months: Decimal
    average_monthly_essential_cost: Decimal
    calculated_target_amount: Decimal
    current_balance: Decimal
    progress_percentage: Decimal
    months_covered: Decimal
    status_classification: str # "Iniciando (< 3 meses)", "Sólida (3 a 6 meses)", "Blindada (> 6 meses)"

# ==================== FLUXO DE CAIXA 12 MESES & SIMULADOR (ISSUE #15) ====================
class CashFlowMonthProjection(BaseModel):
    month: str # YYYY-MM
    projected_income: Decimal
    projected_fixed_expenses: Decimal
    projected_installments: Decimal
    projected_debt_payments: Decimal
    total_projected_outflow: Decimal
    projected_net_balance: Decimal
    accumulated_cash_reserve: Decimal

class CashFlow12MonthsResponse(BaseModel):
    workspace_id: UUID
    current_starting_cash: Decimal
    projections: List[CashFlowMonthProjection]

class ScenarioSimulationRequest(BaseModel):
    income_variation_percentage: Decimal = Field(default=Decimal("0.00")) # Ex: -20.00 para queda de 20%
    one_off_extra_expense: Decimal = Field(default=Decimal("0.00"), ge=0) # Ex: 5000.00
    one_off_expense_month: Optional[str] = None # YYYY-MM

class ScenarioSimulationResponse(BaseModel):
    scenario_description: str
    original_cash_12_months: Decimal
    simulated_cash_12_months: Decimal
    impact_difference: Decimal
    is_resilient: bool
    diagnosis: str

# ==================== PARSER DE EXTRATO E FATURA OFX / CSV (ISSUE #16) ====================
class ImportedTransactionCandidate(BaseModel):
    external_id: Optional[str] = None
    transaction_date: date
    amount: Decimal
    type: str # income / expense
    description: str
    suggested_category_id: Optional[UUID] = None
    suggested_category_name: str
    suggested_essentiality: str
    confidence_score: float # 0.0 a 1.0

class ImportParseResponse(BaseModel):
    filename: str
    format: str # OFX ou CSV
    total_found: int
    total_amount_income: Decimal
    total_amount_expense: Decimal
    candidates: List[ImportedTransactionCandidate]
