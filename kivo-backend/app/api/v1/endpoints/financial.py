from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_, or_, delete, case
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.models import (
    User,
    Workspace,
    WorkspaceMember,
    Account,
    CostCenter,
    Category,
    Tag,
    Transaction,
    transaction_tags,
    TransactionType,
    EssentialityGrade,
    TransactionStatus
)
from app.schemas.financial import (
    AccountCreateRequest,
    AccountUpdateRequest,
    AccountResponse,
    CostCenterCreateRequest,
    CostCenterResponse,
    CategoryCreateRequest,
    CategoryResponse,
    TagCreateRequest,
    TagResponse,
    TagReportItem,
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    MonthlyFinancialSummary
)
from app.api.deps import get_current_user
from app.api.v1.endpoints.workspaces import get_workspace_membership

router = APIRouter()

# ==================== 1. CONTAS BANCÁRIAS & CARTEIRAS ====================

@router.get("/{workspace_id}/accounts", response_model=List[AccountResponse], summary="Listar Contas")
async def list_accounts(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    
    stmt = select(Account).where(
        Account.workspace_id == workspace_id,
        Account.is_active == True
    )
    accounts = (await db.execute(stmt)).scalars().all()
    
    res = []
    for acc in accounts:
        # Calcula saldo atual (Saldo inicial + Receitas pagas - Despesas pagas)
        stmt_inc = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.type == TransactionType.INCOME,
            Transaction.status == TransactionStatus.PAID
        )
        stmt_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
            Transaction.status == TransactionStatus.PAID
        )
        total_inc = Decimal(str(await db.scalar(stmt_inc)))
        total_exp = Decimal(str(await db.scalar(stmt_exp)))
        current_bal = acc.initial_balance + total_inc - total_exp

        res.append(AccountResponse(
            id=acc.id,
            workspace_id=acc.workspace_id,
            owner_member_id=acc.owner_member_id,
            name=acc.name,
            type=acc.type,
            initial_balance=acc.initial_balance,
            current_balance=current_bal,
            credit_limit=acc.credit_limit,
            closing_day=acc.closing_day,
            due_day=acc.due_day,
            is_active=acc.is_active,
            created_at=acc.created_at
        ))
    return res


@router.post("/{workspace_id}/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, summary="Criar Conta / Cartão")
async def create_account(
    workspace_id: UUID,
    req: AccountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    account = Account(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        owner_member_id=req.owner_member_id,
        name=req.name.strip(),
        type=req.type,
        initial_balance=req.initial_balance,
        credit_limit=req.credit_limit,
        closing_day=req.closing_day,
        due_day=req.due_day,
        is_active=True
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)

    return AccountResponse(
        id=account.id,
        workspace_id=account.workspace_id,
        owner_member_id=account.owner_member_id,
        name=account.name,
        type=account.type,
        initial_balance=account.initial_balance,
        current_balance=account.initial_balance,
        credit_limit=account.credit_limit,
        closing_day=account.closing_day,
        due_day=account.due_day,
        is_active=account.is_active,
        created_at=account.created_at
    )


# ==================== 2. CENTROS DE CUSTO & CATEGORIAS ====================

@router.get("/{workspace_id}/cost-centers", response_model=List[CostCenterResponse], summary="Listar Centros de Custo")
async def list_cost_centers(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    stmt = select(CostCenter).where(CostCenter.workspace_id == workspace_id).order_by(CostCenter.name)
    return (await db.execute(stmt)).scalars().all()


@router.post("/{workspace_id}/cost-centers", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED, summary="Criar Centro de Custo")
async def create_cost_center(
    workspace_id: UUID,
    req: CostCenterCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    cc = CostCenter(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name=req.name.strip(),
        scope=req.scope,
        assigned_member_id=req.assigned_member_id
    )
    db.add(cc)
    await db.commit()
    await db.refresh(cc)
    return cc


@router.get("/{workspace_id}/categories", response_model=List[CategoryResponse], summary="Listar Categorias")
async def list_categories(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    stmt = select(Category).where(Category.workspace_id == workspace_id).order_by(Category.name)
    return (await db.execute(stmt)).scalars().all()


@router.post("/{workspace_id}/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Criar Categoria")
async def create_category(
    workspace_id: UUID,
    req: CategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    cat = Category(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        parent_id=req.parent_id,
        name=req.name.strip(),
        icon=req.icon or "folder",
        color=req.color or "#00D084"
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


# ==================== 3. TAGS & RELATÓRIOS DE PROJETOS ====================

@router.get("/{workspace_id}/tags", response_model=List[TagResponse], summary="Listar Tags")
async def list_tags(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    stmt = select(Tag).where(Tag.workspace_id == workspace_id).order_by(Tag.name)
    return (await db.execute(stmt)).scalars().all()


@router.post("/{workspace_id}/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED, summary="Criar Nova Tag")
async def create_tag(
    workspace_id: UUID,
    req: TagCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    
    # Verifica duplicidade no workspace
    stmt_check = select(Tag).where(
        Tag.workspace_id == workspace_id,
        func.lower(Tag.name) == req.name.strip().lower()
    )
    existing = (await db.execute(stmt_check)).scalar_one_or_none()
    if existing:
        return existing

    tag = Tag(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name=req.name.strip(),
        color=req.color or "#3B82F6"
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.get("/{workspace_id}/tags/report", response_model=List[TagReportItem], summary="Relatório Consolidado por Tag (Projetos / Viagens)")
async def get_tag_report(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(
        Tag.id.label("tag_id"),
        Tag.name.label("tag_name"),
        Tag.color.label("tag_color"),
        func.coalesce(func.sum(
            case((Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]), Transaction.amount), else_=Decimal("0.00"))
        ), 0).label("total_expense"),
        func.coalesce(func.sum(
            case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=Decimal("0.00"))
        ), 0).label("total_income"),
        func.count(Transaction.id).label("tx_count")
    ).select_from(Tag).join(transaction_tags, Tag.id == transaction_tags.c.tag_id, isouter=True) \
     .join(Transaction, transaction_tags.c.transaction_id == Transaction.id, isouter=True) \
     .where(Tag.workspace_id == workspace_id) \
     .group_by(Tag.id, Tag.name, Tag.color) \
     .order_by(func.coalesce(func.sum(Transaction.amount), 0).desc())

    rows = (await db.execute(stmt)).all()

    return [
        TagReportItem(
            tag_id=r.tag_id,
            tag_name=r.tag_name,
            tag_color=r.tag_color,
            total_expense=Decimal(str(r.total_expense)),
            total_income=Decimal(str(r.total_income)),
            transaction_count=r.tx_count
        )
        for r in rows
    ]


# ==================== 4. TRANSAÇÕES & PARCELAMENTO ====================

def build_tx_response(tx: Transaction, tags: Optional[List[Tag]] = None) -> TransactionResponse:
    if tags is not None:
        actual_tags = tags
    else:
        try:
            actual_tags = tx.tags or []
        except Exception:
            actual_tags = []
            
    tags_list = [
        TagResponse(id=t.id, workspace_id=t.workspace_id, name=t.name, color=t.color, created_at=t.created_at)
        for t in actual_tags
    ]
    return TransactionResponse(
        id=tx.id,
        workspace_id=tx.workspace_id,
        account_id=tx.account_id,
        paid_by_member_id=tx.paid_by_member_id,
        cost_center_id=tx.cost_center_id,
        category_id=tx.category_id,
        amount=tx.amount,
        type=tx.type,
        essentiality=tx.essentiality,
        transaction_date=tx.transaction_date,
        status=tx.status,
        series_id=tx.series_id,
        installment_current=tx.installment_current,
        installment_total=tx.installment_total,
        description=tx.description,
        notes=tx.notes,
        tags=tags_list,
        created_at=tx.created_at
    )


@router.get("/{workspace_id}/transactions", response_model=List[TransactionResponse], summary="Listar Transações com Filtros")
async def list_transactions(
    workspace_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[UUID] = None,
    cost_center_id: Optional[UUID] = None,
    tag_id: Optional[UUID] = None,
    essentiality: Optional[EssentialityGrade] = None,
    type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Transaction).where(Transaction.workspace_id == workspace_id).options(
        selectinload(Transaction.tags)
    )

    if start_date:
        stmt = stmt.where(Transaction.transaction_date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.transaction_date <= end_date)
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
    if cost_center_id:
        stmt = stmt.where(Transaction.cost_center_id == cost_center_id)
    if essentiality:
        stmt = stmt.where(Transaction.essentiality == essentiality)
    if type:
        stmt = stmt.where(Transaction.type == type)
    if status:
        stmt = stmt.where(Transaction.status == status)
    if tag_id:
        stmt = stmt.join(Transaction.tags).where(Tag.id == tag_id)

    stmt = stmt.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    results = (await db.execute(stmt)).scalars().all()

    return [build_tx_response(tx) for tx in results]


@router.post("/{workspace_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED, summary="Criar Lançamento (com Parcelamento)")
async def create_transaction(
    workspace_id: UUID,
    req: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # Carrega tags
    selected_tags = []
    if req.tag_ids:
        stmt_tags = select(Tag).where(Tag.id.in_(req.tag_ids), Tag.workspace_id == workspace_id)
        selected_tags = (await db.execute(stmt_tags)).scalars().all()

    series_id = uuid.uuid4() if req.total_installments > 1 else None
    created_txs = []

    for i in range(1, req.total_installments + 1):
        # Calcula data de vencimento da parcela i
        tx_date = req.transaction_date + relativedelta(months=(i - 1))
        desc = req.description.strip()
        if req.total_installments > 1:
            desc = f"{req.description.strip()} ({i}/{req.total_installments})"

        tx = Transaction(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            account_id=req.account_id,
            paid_by_member_id=req.paid_by_member_id,
            cost_center_id=req.cost_center_id,
            category_id=req.category_id,
            amount=req.amount,
            type=req.type,
            essentiality=req.essentiality,
            transaction_date=tx_date,
            status=req.status if i == 1 else TransactionStatus.PENDING,
            series_id=series_id,
            installment_current=i,
            installment_total=req.total_installments,
            description=desc,
            notes=req.notes,
            tags=list(selected_tags)
        )
        db.add(tx)
        created_txs.append(tx)

    await db.commit()
    return [build_tx_response(tx, tags=selected_tags) for tx in created_txs]


@router.put("/{workspace_id}/transactions/{transaction_id}", response_model=TransactionResponse, summary="Atualizar Transação")
async def update_transaction(
    workspace_id: UUID,
    transaction_id: UUID,
    req: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.workspace_id == workspace_id
    ).options(selectinload(Transaction.tags))
    tx = (await db.execute(stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada.")

    if req.account_id is not None:
        tx.account_id = req.account_id
    if req.paid_by_member_id is not None:
        tx.paid_by_member_id = req.paid_by_member_id
    if req.cost_center_id is not None:
        tx.cost_center_id = req.cost_center_id
    if req.category_id is not None:
        tx.category_id = req.category_id
    if req.amount is not None:
        tx.amount = req.amount
    if req.type is not None:
        tx.type = req.type
    if req.essentiality is not None:
        tx.essentiality = req.essentiality
    if req.transaction_date is not None:
        tx.transaction_date = req.transaction_date
    if req.status is not None:
        tx.status = req.status
    if req.description is not None:
        tx.description = req.description.strip()
    if req.notes is not None:
        tx.notes = req.notes

    if req.tag_ids is not None:
        stmt_tags = select(Tag).where(Tag.id.in_(req.tag_ids), Tag.workspace_id == workspace_id)
        selected_tags = (await db.execute(stmt_tags)).scalars().all()
        tx.tags = list(selected_tags)

    await db.commit()
    await db.refresh(tx)
    return build_tx_response(tx, tags=tx.tags)


@router.delete("/{workspace_id}/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir Transação")
async def delete_transaction(
    workspace_id: UUID,
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.workspace_id == workspace_id
    )
    tx = (await db.execute(stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada.")

    await db.delete(tx)
    await db.commit()
    return None


@router.get("/{workspace_id}/summary", response_model=MonthlyFinancialSummary, summary="Resumo Financeiro Mensal")
async def get_monthly_summary(
    workspace_id: UUID,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="Formato YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    year, m = map(int, month.split("-"))
    start_dt = date(year, m, 1)
    end_dt = start_dt + relativedelta(months=1, days=-1)

    stmt = select(Transaction).where(
        Transaction.workspace_id == workspace_id,
        Transaction.transaction_date >= start_dt,
        Transaction.transaction_date <= end_dt
    ).options(selectinload(Transaction.tags))
    txs = (await db.execute(stmt)).scalars().all()

    total_income = Decimal("0.00")
    total_expense = Decimal("0.00")
    by_essentiality = {
        "essential": Decimal("0.00"),
        "lifestyle": Decimal("0.00"),
        "waste": Decimal("0.00"),
        "debt": Decimal("0.00"),
        "reserve": Decimal("0.00")
    }
    by_cost_center = {}

    for tx in txs:
        if tx.type == TransactionType.INCOME:
            total_income += tx.amount
        elif tx.type in [TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]:
            total_expense += tx.amount
            ess_key = tx.essentiality.value
            by_essentiality[ess_key] = by_essentiality.get(ess_key, Decimal("0.00")) + tx.amount

    net_savings = total_income - total_expense
    savings_rate = Decimal("0.00")
    if total_income > 0:
        savings_rate = round((net_savings / total_income) * 100, 2)

    return MonthlyFinancialSummary(
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        savings_rate_percentage=savings_rate,
        by_essentiality=by_essentiality,
        by_cost_center=by_cost_center
    )
