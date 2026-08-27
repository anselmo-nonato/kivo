import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Numeric, Integer, Date, Text, Enum as SQLEnum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

# ==================== ENUMS ====================
class WorkspaceType(str, enum.Enum):
    SOLO = "solo"
    FAMILY = "family"

class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class AccountType(str, enum.Enum):
    CHECKING = "checking"
    CREDIT_CARD = "credit_card"
    WALLET = "wallet"
    INVESTMENT = "investment"

class CostCenterScope(str, enum.Enum):
    HOME = "home"
    FAMILY = "family"
    COUPLE = "couple"
    INDIVIDUAL = "individual"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    DEBT_PAYMENT = "debt_payment"
    FUND_DEPOSIT = "fund_deposit"

class EssentialityGrade(str, enum.Enum):
    ESSENTIAL = "essential"
    LIFESTYLE = "lifestyle"
    WASTE = "waste"
    DEBT = "debt"
    RESERVE = "reserve"

class TransactionStatus(str, enum.Enum):
    PAID = "paid"
    PENDING = "pending"

# ==================== TABELA ASSOCIATIVA TAGS ====================
transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column("transaction_id", UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# ==================== TABELAS PRINCIPAIS ====================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True) # Segredo TOTP Base32
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    backup_codes = relationship("UserBackupCode", back_populates="user", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="owner")
    memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")


class UserBackupCode(Base):
    __tablename__ = "user_backup_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash = Column(String(255), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="backup_codes")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(WorkspaceType), default=WorkspaceType.SOLO, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    currency = Column(String(3), default="BRL", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="workspace", cascade="all, delete-orphan")
    cost_centers = relationship("CostCenter", back_populates="workspace", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="workspace", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="workspace", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="workspace", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="workspace", cascade="all, delete-orphan")
    emergency_fund = relationship("EmergencyFund", back_populates="workspace", uselist=False, cascade="all, delete-orphan")
    budget_limits = relationship("BudgetLimit", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    display_name = Column(String(100), nullable=False)
    declared_income = Column(Numeric(15, 2), default=0.00, nullable=False)
    custom_split_percentage = Column(Numeric(5, 2), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_member_id = Column(UUID(as_uuid=True), ForeignKey("workspace_members.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(AccountType), nullable=False)
    initial_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    closing_day = Column(Integer, nullable=True)
    due_day = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="accounts")


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    scope = Column(SQLEnum(CostCenterScope), nullable=False)
    assigned_member_id = Column(UUID(as_uuid=True), ForeignKey("workspace_members.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="cost_centers")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50), default="folder")
    color = Column(String(7), default="#00D084")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="categories")
    subcategories = relationship("Category", backref="parent", remote_side=[id])


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#3B82F6")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="tags")
    transactions = relationship("Transaction", secondary=transaction_tags, back_populates="tags")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    paid_by_member_id = Column(UUID(as_uuid=True), ForeignKey("workspace_members.id"), nullable=False, index=True)
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    essentiality = Column(SQLEnum(EssentialityGrade), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PAID, nullable=False)
    series_id = Column(UUID(as_uuid=True), nullable=True)
    installment_current = Column(Integer, default=1)
    installment_total = Column(Integer, default=1)
    description = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="transactions")
    category = relationship("Category")
    tags = relationship("Tag", secondary=transaction_tags, back_populates="transactions")


class Debt(Base):
    __tablename__ = "debts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("workspace_members.id"), nullable=False)
    creditor_name = Column(String(150), nullable=False)
    original_amount = Column(Numeric(15, 2), nullable=False)
    current_balance = Column(Numeric(15, 2), nullable=False)
    monthly_interest_rate = Column(Numeric(6, 4), nullable=False) # Ex: 0.0450 para 4.5% a.m.
    installment_amount = Column(Numeric(15, 2), nullable=False)
    remaining_installments = Column(Integer, nullable=False)
    due_day = Column(Integer, nullable=False)
    start_date = Column(Date, default=date.today, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="debts")


class EmergencyFund(Base):
    __tablename__ = "emergency_fund"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False)
    target_months = Column(Numeric(4, 1), default=6.0, nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="emergency_fund")


class BudgetLimit(Base):
    __tablename__ = "budget_limits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=True)
    limit_amount = Column(Numeric(15, 2), nullable=True)
    limit_percentage_income = Column(Numeric(5, 2), nullable=True)
    alert_threshold_percentage = Column(Numeric(5, 2), default=75.00, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="budget_limits")
    category = relationship("Category")
    cost_center = relationship("CostCenter")
