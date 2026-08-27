from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from app.models import (
    AccountType,
    CostCenterScope,
    TransactionType,
    EssentialityGrade,
    TransactionStatus
)

# ==================== CONTAS ====================
class AccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: AccountType
    owner_member_id: UUID
    initial_balance: Decimal = Field(default=Decimal("0.00"))
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    closing_day: Optional[int] = Field(None, ge=1, le=31)
    due_day: Optional[int] = Field(None, ge=1, le=31)

class AccountUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    closing_day: Optional[int] = Field(None, ge=1, le=31)
    due_day: Optional[int] = Field(None, ge=1, le=31)
    is_active: Optional[bool] = None

class AccountResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    owner_member_id: UUID
    name: str
    type: AccountType
    initial_balance: Decimal
    current_balance: Decimal = Decimal("0.00")
    credit_limit: Optional[Decimal] = None
    closing_day: Optional[int] = None
    due_day: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== CENTROS DE CUSTO ====================
class CostCenterCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    scope: CostCenterScope
    assigned_member_id: Optional[UUID] = None

class CostCenterResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    scope: CostCenterScope
    assigned_member_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== CATEGORIAS ====================
class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    parent_id: Optional[UUID] = None
    icon: Optional[str] = "folder"
    color: Optional[str] = "#00D084"

class CategoryResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    parent_id: Optional[UUID] = None
    name: str
    icon: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== TAGS ====================
class TagCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = "#3B82F6"

class TagResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True

class TagReportItem(BaseModel):
    tag_id: UUID
    tag_name: str
    tag_color: str
    total_expense: Decimal
    total_income: Decimal
    transaction_count: int

# ==================== TRANSAÇÕES ====================
class TransactionCreateRequest(BaseModel):
    account_id: UUID
    paid_by_member_id: UUID
    cost_center_id: UUID
    category_id: UUID
    amount: Decimal = Field(..., gt=0)
    type: TransactionType
    essentiality: EssentialityGrade
    transaction_date: date
    description: str = Field(..., min_length=1, max_length=255)
    status: TransactionStatus = TransactionStatus.PAID
    notes: Optional[str] = None
    tag_ids: List[UUID] = []
    # Suporte a Parcelamento / Recorrência
    total_installments: int = Field(default=1, ge=1, le=120)

class TransactionUpdateRequest(BaseModel):
    account_id: Optional[UUID] = None
    paid_by_member_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    essentiality: Optional[EssentialityGrade] = None
    transaction_date: Optional[date] = None
    status: Optional[TransactionStatus] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    notes: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None

class TransactionResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    account_name: Optional[str] = None
    paid_by_member_id: UUID
    paid_by_member_name: Optional[str] = None
    cost_center_id: UUID
    cost_center_name: Optional[str] = None
    cost_center_scope: Optional[CostCenterScope] = None
    category_id: UUID
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    amount: Decimal
    type: TransactionType
    essentiality: EssentialityGrade
    transaction_date: date
    status: TransactionStatus
    series_id: Optional[UUID] = None
    installment_current: int
    installment_total: int
    description: str
    notes: Optional[str] = None
    tags: List[TagResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class MonthlyFinancialSummary(BaseModel):
    month: str # YYYY-MM
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal
    savings_rate_percentage: Decimal
    by_essentiality: dict
    by_cost_center: dict
