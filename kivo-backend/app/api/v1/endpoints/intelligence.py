from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import uuid
import math

from app.core.database import get_db
from app.models import (
    User,
    Workspace,
    WorkspaceMember,
    CostCenter,
    CostCenterScope,
    Category,
    Transaction,
    Debt,
    TransactionType,
    EssentialityGrade,
    TransactionStatus
)
from app.schemas.intelligence import (
    EqualizationReportResponse,
    MemberEqualizationDetail,
    EqualizationSettleRequest,
    DebtCreateRequest,
    DebtUpdateRequest,
    DebtAmortizationRequest,
    DebtResponse,
    DebtSimulationResponse,
    DebtSimulationPlan,
    DTIAnalysisResponse
)
from app.api.deps import get_current_user
from app.api.v1.endpoints.workspaces import get_workspace_membership

router = APIRouter()

# ==================== 1. EQUALIZAÇÃO DE CASAL (ISSUE #8) ====================

@router.get("/{workspace_id}/equalization", response_model=EqualizationReportResponse, summary="Cálculo de Rateio Proporcional do Casal")
async def calculate_couple_equalization(
    workspace_id: UUID,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="Mês de competência (YYYY-MM)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    year, m = map(int, month.split("-"))
    start_dt = date(year, m, 1)
    end_dt = start_dt + relativedelta(months=1, days=-1)

    # 1. Carrega Membros do Workspace
    stmt_members = select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
    members = (await db.execute(stmt_members)).scalars().all()
    if not members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum membro encontrado no workspace.")

    total_income = sum((m.declared_income for m in members), Decimal("0.00"))
    
    # 2. Carrega Centros de Custo Compartilhados (HOME, FAMILY, COUPLE)
    stmt_shared_cc = select(CostCenter.id).where(
        CostCenter.workspace_id == workspace_id,
        CostCenter.scope.in_([CostCenterScope.HOME, CostCenterScope.FAMILY, CostCenterScope.COUPLE])
    )
    shared_cc_ids = (await db.execute(stmt_shared_cc)).scalars().all()

    # 3. Carrega Despesas Compartilhadas do Mês agrupadas por quem pagou
    stmt_txs = select(
        Transaction.paid_by_member_id,
        func.coalesce(func.sum(Transaction.amount), 0)
    ).where(
        Transaction.workspace_id == workspace_id,
        Transaction.cost_center_id.in_(shared_cc_ids),
        Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
        Transaction.transaction_date >= start_dt,
        Transaction.transaction_date <= end_dt
    ).group_by(Transaction.paid_by_member_id)

    paid_map = {row[0]: Decimal(str(row[1])) for row in (await db.execute(stmt_txs)).all()}
    total_shared_expenses = sum(paid_map.values(), Decimal("0.00"))

    member_details = []
    for m in members:
        # Proporção de renda
        if total_income > 0:
            income_pct = round((m.declared_income / total_income) * 100, 2)
        else:
            income_pct = round(Decimal("100.00") / Decimal(str(len(members))), 2)

        if m.custom_split_percentage is not None:
            income_pct = m.custom_split_percentage

        fair_share = round(total_shared_expenses * (income_pct / Decimal("100.00")), 2)
        paid_amount = paid_map.get(m.id, Decimal("0.00"))
        bal = paid_amount - fair_share

        member_details.append(
            MemberEqualizationDetail(
                member_id=m.id,
                display_name=m.display_name,
                declared_income=m.declared_income,
                income_percentage=income_pct,
                total_shared_paid=paid_amount,
                fair_share_amount=fair_share,
                balance=bal
            )
        )

    # Identifica pagador e recebedor principal
    settlement_text = "Contas 100% equilibradas neste mês."
    amount_transfer = Decimal("0.00")
    payer_id = None
    payer_name = None
    receiver_id = None
    receiver_name = None

    debtors = [m for m in member_details if m.balance < 0]
    creditors = [m for m in member_details if m.balance > 0]

    if debtors and creditors:
        debtors.sort(key=lambda x: x.balance)
        creditors.sort(key=lambda x: x.balance, reverse=True)
        primary_debtor = debtors[0]
        primary_creditor = creditors[0]
        amount_transfer = abs(primary_debtor.balance)
        payer_id = primary_debtor.member_id
        payer_name = primary_debtor.display_name
        receiver_id = primary_creditor.member_id
        receiver_name = primary_creditor.display_name
        settlement_text = f"{primary_debtor.display_name} deve transferir R$ {amount_transfer:,.2f} para {primary_creditor.display_name} para equalizar o rateio justo."

    return EqualizationReportResponse(
        workspace_id=workspace_id,
        period_month=month,
        total_shared_expenses=total_shared_expenses,
        total_combined_income=total_income,
        members=member_details,
        settlement_suggestion=settlement_text,
        amount_to_transfer=amount_transfer,
        payer_member_id=payer_id,
        payer_name=payer_name,
        receiver_member_id=receiver_id,
        receiver_name=receiver_name
    )


# ==================== 2. DÍVIDAS & AMORTIZAÇÃO (ISSUE #9) ====================

def build_debt_response(d: Debt) -> DebtResponse:
    return DebtResponse(
        id=d.id,
        workspace_id=d.workspace_id,
        member_id=d.member_id,
        creditor_name=d.creditor_name,
        original_amount=d.original_amount,
        current_balance=d.current_balance,
        monthly_interest_rate=d.monthly_interest_rate,
        monthly_interest_rate_percentage=round(d.monthly_interest_rate * 100, 2),
        installment_amount=d.installment_amount,
        remaining_installments=d.remaining_installments,
        due_day=d.due_day,
        created_at=d.created_at,
        updated_at=d.updated_at
    )


@router.get("/{workspace_id}/debts", response_model=List[DebtResponse], summary="Listar Dívidas / Passivos")
async def list_debts(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    stmt = select(Debt).where(Debt.workspace_id == workspace_id).order_by(Debt.monthly_interest_rate.desc())
    debts = (await db.execute(stmt)).scalars().all()
    return [build_debt_response(d) for d in debts]


@router.post("/{workspace_id}/debts", response_model=DebtResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar Dívida")
async def create_debt(
    workspace_id: UUID,
    req: DebtCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    debt = Debt(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        member_id=req.member_id,
        creditor_name=req.creditor_name.strip(),
        original_amount=req.original_amount,
        current_balance=req.current_balance,
        monthly_interest_rate=req.monthly_interest_rate,
        installment_amount=req.installment_amount,
        remaining_installments=req.remaining_installments,
        due_day=req.due_day
    )
    db.add(debt)
    await db.commit()
    await db.refresh(debt)
    return build_debt_response(debt)


@router.post("/{workspace_id}/debts/{debt_id}/amortize", response_model=DebtResponse, summary="Amortização Extraordinária de Dívida")
async def amortize_debt(
    workspace_id: UUID,
    debt_id: UUID,
    req: DebtAmortizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Debt).where(Debt.id == debt_id, Debt.workspace_id == workspace_id)
    debt = (await db.execute(stmt)).scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dívida não encontrada.")

    # Abate direto do saldo devedor
    new_balance = max(Decimal("0.00"), debt.current_balance - req.extra_amount)
    debt.current_balance = new_balance

    if req.strategy == "reduce_term":
        # Recalcula prazo com base na parcela atual
        if debt.installment_amount > 0 and new_balance > 0:
            debt.remaining_installments = max(1, math.ceil(float(new_balance / debt.installment_amount)))
        elif new_balance == 0:
            debt.remaining_installments = 0
    else:
        # Reduz parcela mantendo prazo
        if debt.remaining_installments > 0 and new_balance > 0:
            debt.installment_amount = round(new_balance / Decimal(str(debt.remaining_installments)), 2)

    await db.commit()
    await db.refresh(debt)
    return build_debt_response(debt)


# ==================== 3. SIMULADOR AVALANCHE VS. BOLA DE NEVE (ISSUE #10) ====================

@router.get("/{workspace_id}/debts/simulate", response_model=DebtSimulationResponse, summary="Simulação: Método Avalanche vs. Bola de Neve")
async def simulate_debt_payoff(
    workspace_id: UUID,
    extra_monthly_budget: Decimal = Query(Decimal("500.00"), ge=0, description="Valor extra mensal dedicado à quitação"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(Debt).where(Debt.workspace_id == workspace_id, Debt.current_balance > 0)
    debts = (await db.execute(stmt)).scalars().all()

    if not debts:
        return DebtSimulationResponse(
            monthly_extra_budget=extra_monthly_budget,
            current_monthly_installments_total=Decimal("0.00"),
            avalanche=DebtSimulationPlan(
                strategy_name="Avalanche (Maior Taxa de Juros Primeiro)",
                description="Sem dívidas ativas.",
                months_to_payoff=0,
                total_interest_paid=Decimal("0.00"),
                total_amount_paid=Decimal("0.00"),
                payoff_order=[]
            ),
            snowball=DebtSimulationPlan(
                strategy_name="Bola de Neve (Menor Saldo Primeiro)",
                description="Sem dívidas ativas.",
                months_to_payoff=0,
                total_interest_paid=Decimal("0.00"),
                total_amount_paid=Decimal("0.00"),
                payoff_order=[]
            ),
            recommendation="Parabéns! Nenhuma dívida ativa no momento."
        )

    current_installments = sum((d.installment_amount for d in debts), Decimal("0.00"))

    # 1. Simulação Avalanche (Maior taxa de juros a.m.)
    avalanche_order = sorted(debts, key=lambda d: d.monthly_interest_rate, reverse=True)
    # 2. Simulação Bola de Neve (Menor saldo devedor)
    snowball_order = sorted(debts, key=lambda d: d.current_balance)

    def run_simulation(ordered_list: List[Debt], extra_budget: Decimal):
        # Clona saldos
        balances = {d.id: float(d.current_balance) for d in ordered_list}
        rates = {d.id: float(d.monthly_interest_rate) for d in ordered_list}
        min_payments = {d.id: float(d.installment_amount) for d in ordered_list}
        
        total_interest = 0.0
        total_paid = 0.0
        months = 0
        max_months = 360 # Limite 30 anos

        while any(b > 0 for b in balances.values()) and months < max_months:
            months += 1
            available_extra = float(extra_budget)

            # Aplica juros do mês
            for d_id in balances:
                if balances[d_id] > 0:
                    interest = balances[d_id] * rates[d_id]
                    total_interest += interest
                    balances[d_id] += interest

            # Paga parcela mínima
            for d_id in balances:
                if balances[d_id] > 0:
                    payment = min(balances[d_id], min_payments[d_id])
                    balances[d_id] -= payment
                    total_paid += payment
                else:
                    # Libera a parcela da dívida quitada para o pote extra (Efeito Bola de Neve)
                    available_extra += min_payments[d_id]

            # Aplica todo o extra no foco prioritário da fila
            for d in ordered_list:
                if balances[d.id] > 0 and available_extra > 0:
                    extra_pay = min(balances[d.id], available_extra)
                    balances[d.id] -= extra_pay
                    total_paid += extra_pay
                    available_extra -= extra_pay
                    if balances[d.id] == 0:
                        continue

        return months, Decimal(f"{total_interest:.2f}"), Decimal(f"{total_paid:.2f}")

    m_av, int_av, paid_av = run_simulation(avalanche_order, extra_monthly_budget)
    m_sb, int_sb, paid_sb = run_simulation(snowball_order, extra_monthly_budget)

    diff_economy = paid_sb - paid_av
    rec = f"Recomendamos o Método Avalanche: você economiza R$ {diff_economy:,.2f} em juros bancários e quita tudo em {m_av} meses." if diff_economy > 0 else f"O Método Bola de Neve quita sua primeira dívida mais rapidamente proporcionando alívio emocional imediato."

    return DebtSimulationResponse(
        monthly_extra_budget=extra_monthly_budget,
        current_monthly_installments_total=current_installments,
        avalanche=DebtSimulationPlan(
            strategy_name="Avalanche (Foco em Juros Altos)",
            description="Prioriza a dívida com maior taxa de juros mensal para minimizar o custo efetivo total.",
            months_to_payoff=m_av,
            total_interest_paid=int_av,
            total_amount_paid=paid_av,
            payoff_order=[f"{d.creditor_name} ({d.monthly_interest_rate*100:.1f}% a.m.)" for d in avalanche_order]
        ),
        snowball=DebtSimulationPlan(
            strategy_name="Bola de Neve (Foco em Vitórias Rápidas)",
            description="Prioriza a dívida de menor saldo devedor para quitá-la no menor tempo possível e liberar fluxo de caixa.",
            months_to_payoff=m_sb,
            total_interest_paid=int_sb,
            total_amount_paid=paid_sb,
            payoff_order=[f"{d.creditor_name} (R$ {d.current_balance:,.2f})" for d in snowball_order]
        ),
        recommendation=rec
    )


# ==================== 4. DIAGNÓSTICO DTI (ISSUE #11) ====================

@router.get("/{workspace_id}/debts/dti", response_model=DTIAnalysisResponse, summary="Termômetro DTI (Debt-to-Income)")
async def calculate_dti_thermometer(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # 1. Renda total declarada
    stmt_members = select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
    members = (await db.execute(stmt_members)).scalars().all()
    total_income = sum((m.declared_income for m in members), Decimal("0.00"))

    # 2. Compromisso mensal com dívidas
    stmt_debts = select(Debt).where(Debt.workspace_id == workspace_id, Debt.current_balance > 0)
    debts = (await db.execute(stmt_debts)).scalars().all()
    monthly_debt_total = sum((d.installment_amount for d in debts), Decimal("0.00"))

    dti = Decimal("0.00")
    if total_income > 0:
        dti = round((monthly_debt_total / total_income) * 100, 2)

    if dti < Decimal("20.00"):
        classification = "Saudável (< 20%)"
        status_color = "#10B981" # Emerald
        advice = "Excelente controle! Suas dívidas consomem uma parcela segura da sua renda, permitindo poupar e investir com tranquilidade."
    elif dti <= Decimal("35.00"):
        classification = "Alerta (20% a 35%)"
        status_color = "#F59E0B" # Amber
        advice = "Atenção redobrada: o endividamento está na faixa de alerta. Evite novos parcelamentos e direcione o excedente para amortização."
    else:
        classification = "Crítico (> 35%)"
        status_color = "#EF4444" # Red
        advice = "Nível de endividamento crítico! Mais de um terço da sua renda está comprometida com dívidas. Utilize o simulador Avalanche para reestruturar suas contas imediatamente."

    return DTIAnalysisResponse(
        workspace_id=workspace_id,
        total_monthly_income=total_income,
        total_monthly_debt_commitments=monthly_debt_total,
        dti_percentage=dti,
        classification=classification,
        status_color=status_color,
        actionable_advice=advice
    )
