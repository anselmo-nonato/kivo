from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_, or_, delete, case
from typing import Optional, List, Dict
from uuid import UUID
from datetime import date, datetime, timezone
import calendar
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.models import (
    User,
    Workspace,
    WorkspaceMember,
    Account,
    AccountType,
    CostCenter,
    CostCenterScope,
    Category,
    Tag,
    Transaction,
    transaction_tags,
    TransactionType,
    EssentialityGrade,
    TransactionStatus,
    RecurringBill
)
from app.schemas.financial import (
    AccountCreateRequest,
    AccountUpdateRequest,
    InvoicePaymentRequest,
    AccountResponse,
    CostCenterCreateRequest,
    CostCenterResponse,
    CategoryCreateRequest,
    CategoryResponse,
    TagCreateRequest,
    TagResponse,
    TagReportItem,
    TransferCreateRequest,
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    MonthlyFinancialSummary,
    RecurringBillCreateRequest,
    RecurringBillUpdateRequest,
    RecurringBillResponse,
    RecurringSummaryResponse,
    CardsExecutiveSummaryResponse,
    CardMonthlyForecast,
    CardDetailForecast
)
from app.api.deps import get_current_user
from app.api.v1.endpoints.workspaces import get_workspace_membership

router = APIRouter()

# ==================== 1. CONTAS BANCÁRIAS & CARTEIRAS ====================

async def compute_account_details(acc: Account, db: AsyncSession) -> AccountResponse:
    if acc.type == AccountType.CREDIT_CARD:
        # 1. Total de despesas e parcelas ativas no cartão (consomem o limite)
        stmt_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT])
        )
        # 2. Total de pagamentos de fatura / créditos aplicados a este cartão
        stmt_inc = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            or_(
                Transaction.type == TransactionType.INCOME,
                and_(
                    Transaction.type == TransactionType.TRANSFER,
                    or_(
                        Transaction.notes.ilike("%[transfer_direction:inflow]%"),
                        Transaction.description.ilike("Transferência de %"),
                        Transaction.description.ilike("Crédito Pagamento%"),
                        Transaction.description.ilike("Pagamento de Fatura%"),
                        Transaction.description.ilike("Pagamento Fatura%")
                    )
                )
            )
        )
        total_exp = Decimal(str(await db.scalar(stmt_exp)))
        total_inc = Decimal(str(await db.scalar(stmt_inc)))

        # initial_balance para cartão representa limite utilizado prévio (se houver)
        used_lim = max(Decimal("0.00"), acc.initial_balance + total_exp - total_inc)
        credit_lim = acc.credit_limit or Decimal("0.00")
        avail_lim = max(Decimal("0.00"), credit_lim - used_lim)

        return AccountResponse(
            id=acc.id,
            workspace_id=acc.workspace_id,
            owner_member_id=acc.owner_member_id,
            name=acc.name,
            type=acc.type,
            initial_balance=acc.initial_balance,
            current_balance=used_lim,
            credit_limit=acc.credit_limit,
            used_limit=used_lim,
            available_limit=avail_lim,
            closing_day=acc.closing_day,
            due_day=acc.due_day,
            is_active=acc.is_active,
            created_at=acc.created_at
        )
    else:
        # Conta corrente, carteira ou investimento
        # Entradas: receitas + transferências recebidas (inflow)
        stmt_inc = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.status == TransactionStatus.PAID,
            or_(
                Transaction.type == TransactionType.INCOME,
                and_(
                    Transaction.type == TransactionType.TRANSFER,
                    or_(
                        Transaction.notes.ilike("%[transfer_direction:inflow]%"),
                        Transaction.description.ilike("Transferência de %"),
                        Transaction.description.ilike("Crédito %")
                    )
                )
            )
        )
        # Saídas: despesas + quitação de dívidas + transferências enviadas (outflow)
        stmt_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.status == TransactionStatus.PAID,
            or_(
                Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
                and_(
                    Transaction.type == TransactionType.TRANSFER,
                    or_(
                        Transaction.notes.ilike("%[transfer_direction:outflow]%"),
                        Transaction.description.ilike("Transferência para %"),
                        Transaction.description.ilike("Pagamento Fatura%"),
                        Transaction.description.ilike("Pagamento de Fatura%")
                    )
                )
            )
        )
        total_inc = Decimal(str(await db.scalar(stmt_inc)))
        total_exp = Decimal(str(await db.scalar(stmt_exp)))
        current_bal = acc.initial_balance + total_inc - total_exp

        return AccountResponse(
            id=acc.id,
            workspace_id=acc.workspace_id,
            owner_member_id=acc.owner_member_id,
            name=acc.name,
            type=acc.type,
            initial_balance=acc.initial_balance,
            current_balance=current_bal,
            credit_limit=None,
            used_limit=None,
            available_limit=current_bal,
            closing_day=acc.closing_day,
            due_day=acc.due_day,
            is_active=acc.is_active,
            created_at=acc.created_at
        )


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
    
    return [await compute_account_details(acc, db) for acc in accounts]


@router.get("/{workspace_id}/cards/summary", response_model=CardsExecutiveSummaryResponse, summary="Resumo Executivo Consolidado de Cartões de Crédito & Previsibilidade de Faturas")
async def get_cards_executive_summary(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # 1. Carrega todos os cartões de crédito ativos do workspace
    stmt = select(Account).where(
        Account.workspace_id == workspace_id,
        Account.type == AccountType.CREDIT_CARD,
        Account.is_active == True
    )
    card_accounts = (await db.execute(stmt)).scalars().all()

    if not card_accounts:
        return CardsExecutiveSummaryResponse(
            total_credit_limit=Decimal("0.00"),
            total_used_limit=Decimal("0.00"),
            total_available_limit=Decimal("0.00"),
            usage_percentage=0.0,
            cards_count=0,
            current_month_invoice_total=Decimal("0.00"),
            monthly_forecast=[]
        )

    # Computa detalhes de cada cartão
    card_details = [await compute_account_details(c, db) for c in card_accounts]

    total_credit_limit = sum((c.credit_limit or Decimal("0.00")) for c in card_details)
    total_used_limit = sum((c.used_limit or Decimal("0.00")) for c in card_details)
    total_available_limit = sum((c.available_limit or Decimal("0.00")) for c in card_details)
    usage_pct = float(round((total_used_limit / total_credit_limit * 100), 1)) if total_credit_limit > 0 else 0.0

    card_ids = [c.id for c in card_accounts]
    card_name_map = {c.id: c.name for c in card_accounts}

    # 2. Gera previsão para os próximos 6 meses (Mês Atual + 5 meses seguintes)
    MONTH_NAMES = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    today = date.today()
    current_month_str = today.strftime("%Y-%m")
    
    forecast_list: List[CardMonthlyForecast] = []
    current_month_invoice_total = Decimal("0.00")

    for m_offset in range(6):
        target_date = today + relativedelta(months=m_offset)
        m_str = target_date.strftime("%Y-%m")
        m_name = f"{MONTH_NAMES[target_date.month]}/{str(target_date.year)[2:]}"
        
        start_of_month = date(target_date.year, target_date.month, 1)
        end_of_month = date(target_date.year, target_date.month, calendar.monthrange(target_date.year, target_date.month)[1])

        stmt_txs = select(Transaction).where(
            Transaction.workspace_id == workspace_id,
            Transaction.account_id.in_(card_ids),
            Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
            Transaction.transaction_date >= start_of_month,
            Transaction.transaction_date <= end_of_month
        )
        txs = (await db.execute(stmt_txs)).scalars().all()

        month_total = Decimal("0.00")
        card_totals: Dict[UUID, Decimal] = {cid: Decimal("0.00") for cid in card_ids}

        for tx in txs:
            month_total += tx.amount
            if tx.account_id in card_totals:
                card_totals[tx.account_id] += tx.amount

        by_card_list = [
            CardDetailForecast(
                card_id=cid,
                card_name=card_name_map.get(cid, "Cartão"),
                amount=amt
            )
            for cid, amt in card_totals.items() if amt > 0
        ]

        if m_str == current_month_str:
            current_month_invoice_total = month_total

        forecast_list.append(
            CardMonthlyForecast(
                month=m_str,
                month_name=m_name,
                total_amount=month_total,
                transaction_count=len(txs),
                by_card=by_card_list
            )
        )

    return CardsExecutiveSummaryResponse(
        total_credit_limit=total_credit_limit,
        total_used_limit=total_used_limit,
        total_available_limit=total_available_limit,
        usage_percentage=usage_pct,
        cards_count=len(card_accounts),
        current_month_invoice_total=current_month_invoice_total,
        monthly_forecast=forecast_list
    )


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

    return await compute_account_details(account, db)


@router.put("/{workspace_id}/accounts/{account_id}", response_model=AccountResponse, summary="Atualizar Conta / Cartão / Ajustar Limite")
async def update_account(
    workspace_id: UUID,
    account_id: UUID,
    req: AccountUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Account).where(
        Account.id == account_id,
        Account.workspace_id == workspace_id
    )
    acc = (await db.execute(stmt)).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")

    if req.name is not None:
        acc.name = req.name.strip()
    if req.credit_limit is not None:
        acc.credit_limit = req.credit_limit
    if req.closing_day is not None:
        acc.closing_day = req.closing_day
    if req.due_day is not None:
        acc.due_day = req.due_day
    if req.is_active is not None:
        acc.is_active = req.is_active
    if req.initial_balance is not None:
        acc.initial_balance = req.initial_balance

    # Recalibração de Limite Disponível fornecida diretamente pelo usuário
    if req.adjusted_available_limit is not None and acc.type == AccountType.CREDIT_CARD:
        stmt_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT])
        )
        stmt_inc = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id,
            Transaction.type.in_([TransactionType.INCOME, TransactionType.TRANSFER])
        )
        total_exp = Decimal(str(await db.scalar(stmt_exp)))
        total_inc = Decimal(str(await db.scalar(stmt_inc)))

        credit_lim = acc.credit_limit or Decimal("0.00")
        target_used = max(Decimal("0.00"), credit_lim - req.adjusted_available_limit)
        acc.initial_balance = target_used - (total_exp - total_inc)

    await db.commit()
    await db.refresh(acc)
    return await compute_account_details(acc, db)


@router.delete("/{workspace_id}/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir / Inativar Conta")
async def delete_account(
    workspace_id: UUID,
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Account).where(
        Account.id == account_id,
        Account.workspace_id == workspace_id
    )
    acc = (await db.execute(stmt)).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")

    stmt_tx = select(func.count(Transaction.id)).where(Transaction.account_id == account_id)
    tx_count = await db.scalar(stmt_tx)
    if tx_count and tx_count > 0:
        acc.is_active = False
        await db.commit()
    else:
        await db.delete(acc)
        await db.commit()
    return None


@router.post("/{workspace_id}/accounts/{account_id}/pay-invoice", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, summary="Pagar Fatura do Cartão")
async def pay_card_invoice(
    workspace_id: UUID,
    account_id: UUID,
    req: InvoicePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    member = await get_workspace_membership(workspace_id, current_user.id, db)

    # 1. Valida cartão de crédito
    stmt_card = select(Account).where(
        Account.id == account_id,
        Account.workspace_id == workspace_id,
        Account.is_active == True
    )
    card = (await db.execute(stmt_card)).scalar_one_or_none()
    if not card or card.type != AccountType.CREDIT_CARD:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A conta de destino deve ser um Cartão de Crédito ativo.")

    # 2. Valida conta bancária de origem
    stmt_src = select(Account).where(
        Account.id == req.source_account_id,
        Account.workspace_id == workspace_id,
        Account.is_active == True
    )
    src_acc = (await db.execute(stmt_src)).scalar_one_or_none()
    if not src_acc or src_acc.type == AccountType.CREDIT_CARD:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A conta de origem do pagamento deve ser uma Conta Corrente ou Carteira válida.")

    # 3. Localiza ou cria categoria padrão para Pagamento de Cartão
    stmt_cat = select(Category).where(
        Category.workspace_id == workspace_id,
        Category.name.ilike("%Fatura%")
    )
    cat = (await db.execute(stmt_cat)).scalars().first()
    if not cat:
        stmt_any_cat = select(Category).where(Category.workspace_id == workspace_id)
        cat = (await db.execute(stmt_any_cat)).scalars().first()
        if not cat:
            cat = Category(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="Pagamento de Cartão",
                icon="credit-card",
                color="#8B5CF6"
            )
            db.add(cat)
            await db.flush()

    # 4. Localiza Centro de Custo padrão
    stmt_cc = select(CostCenter).where(CostCenter.workspace_id == workspace_id)
    cost_center = (await db.execute(stmt_cc)).scalars().first()
    if not cost_center:
        cost_center = CostCenter(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name="Geral",
            scope=CostCenterScope.FAMILY
        )
        db.add(cost_center)
        await db.flush()

    paid_by_id = req.paid_by_member_id or member.id
    pay_date = req.payment_date or date.today()
    desc = req.notes or f"Pagamento Fatura - {card.name}"
    series_id = uuid.uuid4()

    # 5. Cria débito na conta bancária de saída (Transferência / Liquidação)
    tx_debit = Transaction(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        account_id=src_acc.id,
        destination_account_id=card.id,
        paid_by_member_id=paid_by_id,
        cost_center_id=cost_center.id,
        category_id=cat.id,
        amount=req.amount,
        type=TransactionType.TRANSFER,
        essentiality=EssentialityGrade.ESSENTIAL,
        transaction_date=pay_date,
        status=TransactionStatus.PAID,
        series_id=series_id,
        installment_current=1,
        installment_total=1,
        description=f"Pagamento Fatura {card.name}",
        notes=f"{desc} [transfer_direction:outflow]".strip()
    )
    db.add(tx_debit)

    # 6. Cria crédito de liquidação no cartão de crédito (restaura limite de forma neutra)
    tx_credit = Transaction(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        account_id=card.id,
        destination_account_id=src_acc.id,
        paid_by_member_id=paid_by_id,
        cost_center_id=cost_center.id,
        category_id=cat.id,
        amount=req.amount,
        type=TransactionType.TRANSFER,
        essentiality=EssentialityGrade.ESSENTIAL,
        transaction_date=pay_date,
        status=TransactionStatus.PAID,
        series_id=series_id,
        installment_current=1,
        installment_total=1,
        description=f"Crédito Pagamento Fatura ({src_acc.name})",
        notes=f"{desc} [transfer_direction:inflow]".strip()
    )
    db.add(tx_credit)

    await db.commit()
    await db.refresh(card)

    return await compute_account_details(card, db)



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

    transfer_dir = None
    if tx.type == TransactionType.TRANSFER:
        if tx.notes and "[transfer_direction:inflow]" in tx.notes:
            transfer_dir = "inflow"
        elif tx.notes and "[transfer_direction:outflow]" in tx.notes:
            transfer_dir = "outflow"
        elif tx.description and tx.description.lower().startswith("transferência de"):
            transfer_dir = "inflow"
        elif tx.description and tx.description.lower().startswith("transferência para"):
            transfer_dir = "outflow"
        elif tx.destination_account_id:
            transfer_dir = "outflow"

    account_name = None
    if "account" in tx.__dict__ and tx.__dict__["account"] is not None:
        account_name = tx.__dict__["account"].name

    dest_account_name = None
    if "destination_account" in tx.__dict__ and tx.__dict__["destination_account"] is not None:
        dest_account_name = tx.__dict__["destination_account"].name

    cat_name = None
    cat_color = None
    if "category" in tx.__dict__ and tx.__dict__["category"] is not None:
        cat_name = tx.__dict__["category"].name
        cat_color = tx.__dict__["category"].color

    return TransactionResponse(
        id=tx.id,
        workspace_id=tx.workspace_id,
        account_id=tx.account_id,
        account_name=account_name,
        destination_account_id=tx.destination_account_id,
        destination_account_name=dest_account_name,
        transfer_direction=transfer_dir,
        paid_by_member_id=tx.paid_by_member_id,
        cost_center_id=tx.cost_center_id,
        category_id=tx.category_id,
        category_name=cat_name,
        category_color=cat_color,
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
    account_id: Optional[UUID] = None,
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
        selectinload(Transaction.tags),
        selectinload(Transaction.account),
        selectinload(Transaction.destination_account),
        selectinload(Transaction.category)
    )

    if start_date:
        stmt = stmt.where(Transaction.transaction_date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.transaction_date <= end_date)
    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
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


@router.post("/{workspace_id}/transfers", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED, summary="Transferência entre Contas Próprias (Neutro)")
async def create_transfer(
    workspace_id: UUID,
    req: TransferCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    member = await get_workspace_membership(workspace_id, current_user.id, db)

    if req.source_account_id == req.destination_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A conta de origem e a conta de destino não podem ser iguais."
        )

    # 1. Carrega conta de origem
    stmt_src = select(Account).where(
        Account.id == req.source_account_id,
        Account.workspace_id == workspace_id,
        Account.is_active == True
    )
    src_acc = (await db.execute(stmt_src)).scalar_one_or_none()
    if not src_acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta de origem não encontrada ou inativa.")

    # 2. Carrega conta de destino
    stmt_dest = select(Account).where(
        Account.id == req.destination_account_id,
        Account.workspace_id == workspace_id,
        Account.is_active == True
    )
    dest_acc = (await db.execute(stmt_dest)).scalar_one_or_none()
    if not dest_acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta de destino não encontrada ou inativa.")

    # 3. Localiza ou cria categoria de Transferência
    stmt_cat = select(Category).where(
        Category.workspace_id == workspace_id,
        or_(Category.name.ilike("Transferência%"), Category.name.ilike("Transferencia%"))
    )
    cat = (await db.execute(stmt_cat)).scalars().first()
    if not cat:
        stmt_any_cat = select(Category).where(Category.workspace_id == workspace_id)
        cat = (await db.execute(stmt_any_cat)).scalars().first()
        if not cat:
            cat = Category(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="Transferência entre Contas",
                icon="arrow-left-right",
                color="#64748B"
            )
            db.add(cat)
            await db.flush()

    # 4. Centro de Custo padrão
    stmt_cc = select(CostCenter).where(CostCenter.workspace_id == workspace_id)
    cost_center = (await db.execute(stmt_cc)).scalars().first()
    if not cost_center:
        cost_center = CostCenter(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name="Geral",
            scope=CostCenterScope.FAMILY
        )
        db.add(cost_center)
        await db.flush()

    paid_by_id = req.paid_by_member_id or member.id
    series_id = uuid.uuid4()
    custom_desc = req.description.strip() if req.description and req.description.strip() else None

    # 5. Transação de Saída (Origem)
    tx_out = Transaction(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        account_id=src_acc.id,
        destination_account_id=dest_acc.id,
        paid_by_member_id=paid_by_id,
        cost_center_id=cost_center.id,
        category_id=cat.id,
        amount=req.amount,
        type=TransactionType.TRANSFER,
        essentiality=EssentialityGrade.ESSENTIAL,
        transaction_date=req.transaction_date,
        status=TransactionStatus.PAID,
        series_id=series_id,
        installment_current=1,
        installment_total=1,
        description=custom_desc or f"Transferência para {dest_acc.name}",
        notes=f"{req.notes or ''} [transfer_direction:outflow]".strip()
    )
    db.add(tx_out)

    # 6. Transação de Entrada Espelho (Destino)
    tx_in = Transaction(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        account_id=dest_acc.id,
        destination_account_id=src_acc.id,
        paid_by_member_id=paid_by_id,
        cost_center_id=cost_center.id,
        category_id=cat.id,
        amount=req.amount,
        type=TransactionType.TRANSFER,
        essentiality=EssentialityGrade.ESSENTIAL,
        transaction_date=req.transaction_date,
        status=TransactionStatus.PAID,
        series_id=series_id,
        installment_current=1,
        installment_total=1,
        description=custom_desc or f"Transferência de {src_acc.name}",
        notes=f"{req.notes or ''} [transfer_direction:inflow]".strip()
    )
    db.add(tx_in)

    await db.commit()
    await db.refresh(tx_out)
    await db.refresh(tx_in)

    return [build_tx_response(tx_out), build_tx_response(tx_in)]


@router.post("/{workspace_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED, summary="Criar Lançamento (com Parcelamento)")
async def create_transaction(
    workspace_id: UUID,
    req: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # Se for transferência simples com destino especificado
    if req.type == TransactionType.TRANSFER and req.destination_account_id:
        # Carrega conta de destino
        stmt_dest = select(Account).where(
            Account.id == req.destination_account_id,
            Account.workspace_id == workspace_id,
            Account.is_active == True
        )
        dest_acc = (await db.execute(stmt_dest)).scalar_one_or_none()
        stmt_src = select(Account).where(
            Account.id == req.account_id,
            Account.workspace_id == workspace_id,
            Account.is_active == True
        )
        src_acc = (await db.execute(stmt_src)).scalar_one_or_none()

        series_id = uuid.uuid4()
        tx_out = Transaction(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            account_id=req.account_id,
            destination_account_id=req.destination_account_id,
            paid_by_member_id=req.paid_by_member_id,
            cost_center_id=req.cost_center_id,
            category_id=req.category_id,
            amount=req.amount,
            type=TransactionType.TRANSFER,
            essentiality=req.essentiality,
            transaction_date=req.transaction_date,
            status=req.status,
            series_id=series_id,
            installment_current=1,
            installment_total=1,
            description=req.description.strip(),
            notes=f"{req.notes or ''} [transfer_direction:outflow]".strip()
        )
        db.add(tx_out)

        tx_in = Transaction(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            account_id=req.destination_account_id,
            destination_account_id=req.account_id,
            paid_by_member_id=req.paid_by_member_id,
            cost_center_id=req.cost_center_id,
            category_id=req.category_id,
            amount=req.amount,
            type=TransactionType.TRANSFER,
            essentiality=req.essentiality,
            transaction_date=req.transaction_date,
            status=req.status,
            series_id=series_id,
            installment_current=1,
            installment_total=1,
            description=f"Transferência de {src_acc.name if src_acc else 'outra conta'}",
            notes=f"{req.notes or ''} [transfer_direction:inflow]".strip()
        )
        db.add(tx_in)
        await db.commit()
        await db.refresh(tx_out)
        await db.refresh(tx_in)
        return [build_tx_response(tx_out), build_tx_response(tx_in)]

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
            destination_account_id=req.destination_account_id,
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
    if req.destination_account_id is not None:
        tx.destination_account_id = req.destination_account_id
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

    if tx.type == TransactionType.TRANSFER and tx.series_id:
        stmt_paired = delete(Transaction).where(
            Transaction.workspace_id == workspace_id,
            Transaction.series_id == tx.series_id
        )
        await db.execute(stmt_paired)
    else:
        await db.delete(tx)

    await db.commit()
    return None


@router.post("/{workspace_id}/transactions/{transaction_id}/confirm", response_model=TransactionResponse, summary="Confirmar Efetivação / Baixa de Lançamento")
async def confirm_transaction(
    workspace_id: UUID,
    transaction_id: UUID,
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

    tx.status = TransactionStatus.PAID
    await db.commit()
    await db.refresh(tx)
    return build_tx_response(tx, tags=tx.tags)


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


# ==================== 6. DESPESAS E RECEITAS FIXAS / RECORRENTES ====================

def build_recurring_response(bill: RecurringBill) -> RecurringBillResponse:
    return RecurringBillResponse(
        id=bill.id,
        workspace_id=bill.workspace_id,
        account_id=bill.account_id,
        account_name=bill.account.name if bill.account else None,
        paid_by_member_id=bill.paid_by_member_id,
        paid_by_member_name=bill.member.display_name if bill.member else None,
        cost_center_id=bill.cost_center_id,
        cost_center_name=bill.cost_center.name if bill.cost_center else None,
        category_id=bill.category_id,
        category_name=bill.category.name if bill.category else None,
        description=bill.description,
        amount=bill.amount,
        type=bill.type,
        essentiality=bill.essentiality,
        frequency=bill.frequency,
        due_day=bill.due_day,
        start_date=bill.start_date,
        end_date=bill.end_date,
        is_active=bill.is_active,
        created_at=bill.created_at
    )


@router.get("/{workspace_id}/recurring", response_model=RecurringSummaryResponse, summary="Listar e Resumir Despesas Fixas")
async def list_recurring_bills(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(RecurringBill).where(
        RecurringBill.workspace_id == workspace_id
    ).options(
        selectinload(RecurringBill.account),
        selectinload(RecurringBill.category),
        selectinload(RecurringBill.cost_center),
        selectinload(RecurringBill.member)
    ).order_by(RecurringBill.due_day.asc())

    bills = (await db.execute(stmt)).scalars().all()

    total_expense = Decimal("0.00")
    total_income = Decimal("0.00")
    active_count = 0

    for b in bills:
        if b.is_active:
            active_count += 1
            if b.type == "income":
                total_income += b.amount
            else:
                total_expense += b.amount

    return RecurringSummaryResponse(
        total_monthly_fixed_expenses=total_expense,
        total_monthly_fixed_income=total_income,
        net_fixed_balance=total_income - total_expense,
        total_active_bills=active_count,
        bills=[build_recurring_response(b) for b in bills]
    )


@router.post("/{workspace_id}/recurring", response_model=RecurringBillResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar Despesa / Conta Fixa")
async def create_recurring_bill(
    workspace_id: UUID,
    req: RecurringBillCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    bill = RecurringBill(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        account_id=req.account_id,
        paid_by_member_id=req.paid_by_member_id,
        cost_center_id=req.cost_center_id,
        category_id=req.category_id,
        description=req.description.strip(),
        amount=req.amount,
        type=req.type,
        essentiality=req.essentiality,
        frequency=req.frequency,
        due_day=req.due_day,
        start_date=req.start_date,
        end_date=req.end_date,
        is_active=req.is_active
    )
    db.add(bill)
    await db.commit()

    stmt = select(RecurringBill).where(RecurringBill.id == bill.id).options(
        selectinload(RecurringBill.account),
        selectinload(RecurringBill.category),
        selectinload(RecurringBill.cost_center),
        selectinload(RecurringBill.member)
    )
    saved = (await db.execute(stmt)).scalar_one()
    return build_recurring_response(saved)


@router.put("/{workspace_id}/recurring/{bill_id}", response_model=RecurringBillResponse, summary="Atualizar Despesa Fixa")
async def update_recurring_bill(
    workspace_id: UUID,
    bill_id: UUID,
    req: RecurringBillUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(RecurringBill).where(
        RecurringBill.id == bill_id,
        RecurringBill.workspace_id == workspace_id
    ).options(
        selectinload(RecurringBill.account),
        selectinload(RecurringBill.category),
        selectinload(RecurringBill.cost_center),
        selectinload(RecurringBill.member)
    )
    bill = (await db.execute(stmt)).scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa fixa não encontrada.")

    if req.description is not None:
        bill.description = req.description.strip()
    if req.amount is not None:
        bill.amount = req.amount
    if req.type is not None:
        bill.type = req.type
    if req.essentiality is not None:
        bill.essentiality = req.essentiality
    if req.frequency is not None:
        bill.frequency = req.frequency
    if req.due_day is not None:
        bill.due_day = req.due_day
    if req.start_date is not None:
        bill.start_date = req.start_date
    if req.end_date is not None:
        bill.end_date = req.end_date
    if req.account_id is not None:
        bill.account_id = req.account_id
    if req.paid_by_member_id is not None:
        bill.paid_by_member_id = req.paid_by_member_id
    if req.cost_center_id is not None:
        bill.cost_center_id = req.cost_center_id
    if req.category_id is not None:
        bill.category_id = req.category_id
    if req.is_active is not None:
        bill.is_active = req.is_active

    await db.commit()
    await db.refresh(bill)
    return build_recurring_response(bill)


@router.delete("/{workspace_id}/recurring/{bill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir Despesa Fixa")
async def delete_recurring_bill(
    workspace_id: UUID,
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(RecurringBill).where(
        RecurringBill.id == bill_id,
        RecurringBill.workspace_id == workspace_id
    )
    bill = (await db.execute(stmt)).scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa fixa não encontrada.")

    await db.delete(bill)
    await db.commit()
    return None

