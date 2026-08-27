from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
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
import re
import csv
import io

from app.core.database import get_db
from app.models import (
    User,
    Workspace,
    WorkspaceMember,
    CostCenter,
    Category,
    Account,
    Transaction,
    Debt,
    EmergencyFund,
    BudgetLimit,
    TransactionType,
    EssentialityGrade,
    TransactionStatus
)
from app.schemas.analytics import (
    BudgetLimitCreateRequest,
    BudgetRadarResponse,
    BudgetLimitItemResponse,
    WasteReportResponse,
    WasteItemResponse,
    EmergencyFundConfig,
    EmergencyFundDepositRequest,
    EmergencyFundStatusResponse,
    CashFlow12MonthsResponse,
    CashFlowMonthProjection,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
    ImportParseResponse,
    ImportedTransactionCandidate
)
from app.api.deps import get_current_user
from app.api.v1.endpoints.workspaces import get_workspace_membership

router = APIRouter()

# ==================== 1. RADAR DE TETOS & SEMÁFORO DE CONSUMO (ISSUE #12) ====================

@router.get("/{workspace_id}/radar", response_model=BudgetRadarResponse, summary="Radar de Tetos e Semáforo de Consumo")
async def get_budget_radar(
    workspace_id: UUID,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="Formato YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    year, m = map(int, month.split("-"))
    start_dt = date(year, m, 1)
    end_dt = start_dt + relativedelta(months=1, days=-1)
    days_in_month = end_dt.day

    # Calcula % do mês decorrido
    today = date.today()
    if today < start_dt:
        month_progress_pct = Decimal("0.00")
    elif today > end_dt:
        month_progress_pct = Decimal("100.00")
    else:
        month_progress_pct = round((Decimal(str(today.day)) / Decimal(str(days_in_month))) * 100, 2)

    # Carrega limites configurados
    stmt_limits = select(BudgetLimit).where(BudgetLimit.workspace_id == workspace_id).options(
        selectinload(BudgetLimit.category),
        selectinload(BudgetLimit.cost_center)
    )
    limits = (await db.execute(stmt_limits)).scalars().all()

    # Renda total
    stmt_inc = select(WorkspaceMember.declared_income).where(WorkspaceMember.workspace_id == workspace_id)
    total_income = sum((await db.execute(stmt_inc)).scalars().all(), Decimal("0.00"))

    budgets_list = []
    total_budget_limit = Decimal("0.00")
    total_spent = Decimal("0.00")

    for bl in limits:
        effective_limit = bl.limit_amount or Decimal("0.00")
        if bl.limit_percentage_income and total_income > 0:
            effective_limit = round(total_income * (bl.limit_percentage_income / Decimal("100.00")), 2)

        # Soma gastos do mês para este limite
        stmt_spent = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.workspace_id == workspace_id,
            Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
            Transaction.transaction_date >= start_dt,
            Transaction.transaction_date <= end_dt
        )
        if bl.category_id:
            stmt_spent = stmt_spent.where(Transaction.category_id == bl.category_id)
        if bl.cost_center_id:
            stmt_spent = stmt_spent.where(Transaction.cost_center_id == bl.cost_center_id)

        spent = Decimal(str(await db.scalar(stmt_spent)))
        pct_consumed = round((spent / effective_limit) * 100, 2) if effective_limit > 0 else Decimal("0.00")

        # Semáforo de Ritmo
        if pct_consumed > 100:
            pace = "Estourado"
            color = "#EF4444" # Vermelho
        elif pct_consumed > (month_progress_pct + 15):
            pace = "Acelerado"
            color = "#F59E0B" # Amarelo
        else:
            pace = "Normal"
            color = "#10B981" # Verde

        total_budget_limit += effective_limit
        total_spent += spent

        budgets_list.append(
            BudgetLimitItemResponse(
                id=bl.id,
                category_id=bl.category_id,
                category_name=bl.category.name if bl.category else None,
                cost_center_id=bl.cost_center_id,
                cost_center_name=bl.cost_center.name if bl.cost_center else None,
                limit_amount=effective_limit,
                spent_amount=spent,
                percentage_consumed=pct_consumed,
                month_progress_percentage=month_progress_pct,
                consumption_pace_status=pace,
                status_color=color
            )
        )

    overall_pct = round((total_spent / total_budget_limit) * 100, 2) if total_budget_limit > 0 else Decimal("0.00")

    return BudgetRadarResponse(
        workspace_id=workspace_id,
        month=month,
        total_budget_limit=total_budget_limit,
        total_spent=total_spent,
        overall_percentage=overall_pct,
        month_progress_percentage=month_progress_pct,
        budgets=budgets_list
    )


@router.post("/{workspace_id}/radar/limits", status_code=status.HTTP_201_CREATED, summary="Cadastrar Teto Orçamentário")
async def create_budget_limit(
    workspace_id: UUID,
    req: BudgetLimitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)
    bl = BudgetLimit(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        category_id=req.category_id,
        cost_center_id=req.cost_center_id,
        limit_amount=req.limit_amount,
        limit_percentage_income=req.limit_percentage_income,
        alert_threshold_percentage=req.alert_threshold_percentage
    )
    db.add(bl)
    await db.commit()
    return {"message": "Teto orçamentário configurado com sucesso!", "id": bl.id}


# ==================== 2. RELATÓRIO DE DESPERDÍCIOS / RALOS (ISSUE #13) ====================

@router.get("/{workspace_id}/waste", response_model=WasteReportResponse, summary="Relatório de Ralos e Gastos Desconexos")
async def get_waste_report(
    workspace_id: UUID,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="Formato YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    year, m = map(int, month.split("-"))
    start_dt = date(year, m, 1)
    end_dt = start_dt + relativedelta(months=1, days=-1)

    # 1. Busca transações com essencialidade 'waste'
    stmt_waste = select(Transaction).where(
        Transaction.workspace_id == workspace_id,
        Transaction.essentiality == EssentialityGrade.WASTE,
        Transaction.transaction_date >= start_dt,
        Transaction.transaction_date <= end_dt
    ).options(selectinload(Transaction.category))
    waste_txs = (await db.execute(stmt_waste)).scalars().all()

    # 2. Total de despesas gerais do mês
    stmt_total_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.workspace_id == workspace_id,
        Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]),
        Transaction.transaction_date >= start_dt,
        Transaction.transaction_date <= end_dt
    )
    total_expense = Decimal(str(await db.scalar(stmt_total_exp)))

    total_waste = sum((tx.amount for tx in waste_txs), Decimal("0.00"))
    waste_annualized = total_waste * Decimal("12.00")
    waste_pct = round((total_waste / total_expense) * 100, 2) if total_expense > 0 else Decimal("0.00")

    # Simulação do montante em 5 anos a 10% a.a. (CDI/Tesouro) aportando o valor mensal do ralo
    # FV = PMT * [((1 + i)^n - 1) / i]
    i_monthly = 0.10 / 12.0
    n_months = 60
    if float(total_waste) > 0:
        fv_5_years = float(total_waste) * (((1 + i_monthly) ** n_months - 1) / i_monthly)
    else:
        fv_5_years = 0.0

    items = []
    for tx in waste_txs:
        ann = tx.amount * Decimal("12.00")
        # 3 anos a 10% a.a.
        opp_3_yrs = float(tx.amount) * (((1 + i_monthly) ** 36 - 1) / i_monthly)
        items.append(
            WasteItemResponse(
                transaction_id=tx.id,
                description=tx.description,
                amount=tx.amount,
                transaction_date=tx.transaction_date,
                category_name=tx.category.name if tx.category else "Geral",
                annualized_impact=ann,
                opportunity_cost_3_years=Decimal(f"{opp_3_yrs:.2f}")
            )
        )

    return WasteReportResponse(
        workspace_id=workspace_id,
        month=month,
        total_waste_month=total_waste,
        total_waste_annualized=waste_annualized,
        waste_percentage_of_expenses=waste_pct,
        potential_patrimony_in_5_years=Decimal(f"{fv_5_years:.2f}"),
        waste_transactions=items
    )


# ==================== 3. COFRE DA RESERVA DE EMERGÊNCIA (ISSUE #14) ====================

@router.get("/{workspace_id}/emergency-fund", response_model=EmergencyFundStatusResponse, summary="Status do Cofre da Reserva de Emergência")
async def get_emergency_fund_status(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # 1. Carrega ou cria registro do Cofre
    stmt = select(EmergencyFund).where(EmergencyFund.workspace_id == workspace_id)
    fund = (await db.execute(stmt)).scalar_one_or_none()
    if not fund:
        fund = EmergencyFund(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            target_months=Decimal("6.0"),
            current_balance=Decimal("0.00")
        )
        db.add(fund)
        await db.commit()
        await db.refresh(fund)

    # 2. Calcula Média dos Custos Essenciais dos últimos 3 meses
    today = date.today()
    three_months_ago = today - relativedelta(months=3)
    stmt_ess = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.workspace_id == workspace_id,
        Transaction.essentiality == EssentialityGrade.ESSENTIAL,
        Transaction.transaction_date >= three_months_ago,
        Transaction.transaction_date <= today
    )
    total_essential_last_3m = Decimal(str(await db.scalar(stmt_ess)))
    avg_monthly_essential = round(total_essential_last_3m / Decimal("3.00"), 2)

    # Se não tiver histórico suficiente, usa média de R$ 3.000 como base padrão
    if avg_monthly_essential == 0:
        avg_monthly_essential = Decimal("3000.00")

    target_amount = round(avg_monthly_essential * fund.target_months, 2)
    progress_pct = round((fund.current_balance / target_amount) * 100, 2) if target_amount > 0 else Decimal("0.00")
    months_covered = round(fund.current_balance / avg_monthly_essential, 1) if avg_monthly_essential > 0 else Decimal("0.0")

    if months_covered < Decimal("3.0"):
        classification = "Iniciando (< 3 meses)"
    elif months_covered <= Decimal("6.0"):
        classification = "Sólida (3 a 6 meses)"
    else:
        classification = "Blindada (> 6 meses)"

    return EmergencyFundStatusResponse(
        workspace_id=workspace_id,
        target_months=fund.target_months,
        average_monthly_essential_cost=avg_monthly_essential,
        calculated_target_amount=target_amount,
        current_balance=fund.current_balance,
        progress_percentage=progress_pct,
        months_covered=months_covered,
        status_classification=classification
    )


@router.post("/{workspace_id}/emergency-fund/deposit", response_model=EmergencyFundStatusResponse, summary="Depositar no Cofre da Reserva")
async def deposit_emergency_fund(
    workspace_id: UUID,
    req: EmergencyFundDepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    stmt = select(EmergencyFund).where(EmergencyFund.workspace_id == workspace_id)
    fund = (await db.execute(stmt)).scalar_one_or_none()
    if not fund:
        fund = EmergencyFund(id=uuid.uuid4(), workspace_id=workspace_id, target_months=Decimal("6.0"), current_balance=Decimal("0.00"))
        db.add(fund)

    fund.current_balance += req.amount
    await db.commit()

    return await get_emergency_fund_status(workspace_id, current_user, db)


# ==================== 4. FLUXO DE CAIXA 12 MESES & SIMULADOR DE CENÁRIOS (ISSUE #15) ====================

@router.get("/{workspace_id}/cash-flow/12-months", response_model=CashFlow12MonthsResponse, summary="Projeção de Fluxo de Caixa para 12 Meses")
async def get_cash_flow_projection(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # 1. Saldo atual somado de todas as contas ativas
    stmt_accounts = select(Account).where(Account.workspace_id == workspace_id, Account.is_active == True)
    accounts = (await db.execute(stmt_accounts)).scalars().all()
    
    current_starting_cash = Decimal("0.00")
    for acc in accounts:
        stmt_inc = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id, Transaction.type == TransactionType.INCOME, Transaction.status == TransactionStatus.PAID
        )
        stmt_exp = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == acc.id, Transaction.type.in_([TransactionType.EXPENSE, TransactionType.DEBT_PAYMENT]), Transaction.status == TransactionStatus.PAID
        )
        current_starting_cash += (acc.initial_balance + Decimal(str(await db.scalar(stmt_inc))) - Decimal(str(await db.scalar(stmt_exp))))

    # 2. Renda mensal recorrente
    stmt_members = select(WorkspaceMember.declared_income).where(WorkspaceMember.workspace_id == workspace_id)
    monthly_income = sum((await db.execute(stmt_members)).scalars().all(), Decimal("0.00"))

    # 3. Dívidas mensais
    stmt_debts = select(Debt).where(Debt.workspace_id == workspace_id, Debt.current_balance > 0)
    debts = (await db.execute(stmt_debts)).scalars().all()

    today = date.today()
    projections = []
    running_reserve = current_starting_cash

    for m_idx in range(1, 13):
        target_month_date = today + relativedelta(months=m_idx - 1)
        month_key = target_month_date.strftime("%Y-%m")
        m_start = date(target_month_date.year, target_month_date.month, 1)
        m_end = m_start + relativedelta(months=1, days=-1)

        # Parcelas já lançadas e agendadas para o mês
        stmt_inst = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.workspace_id == workspace_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= m_start,
            Transaction.transaction_date <= m_end
        )
        monthly_installments = Decimal(str(await db.scalar(stmt_inst)))

        # Dívidas ativas no mês
        debt_payment_month = sum((d.installment_amount for d in debts if d.remaining_installments >= m_idx), Decimal("0.00"))
        
        # Despesas fixas estimadas
        fixed_expenses = Decimal("2500.00")

        total_outflow = fixed_expenses + monthly_installments + debt_payment_month
        net_balance = monthly_income - total_outflow
        running_reserve += net_balance

        projections.append(
            CashFlowMonthProjection(
                month=month_key,
                projected_income=monthly_income,
                projected_fixed_expenses=fixed_expenses,
                projected_installments=monthly_installments,
                projected_debt_payments=debt_payment_month,
                total_projected_outflow=total_outflow,
                projected_net_balance=net_balance,
                accumulated_cash_reserve=running_reserve
            )
        )

    return CashFlow12MonthsResponse(
        workspace_id=workspace_id,
        current_starting_cash=current_starting_cash,
        projections=projections
    )


@router.post("/{workspace_id}/cash-flow/simulate-scenario", response_model=ScenarioSimulationResponse, summary="Simulador de Cenários de Stress")
async def simulate_stress_scenario(
    workspace_id: UUID,
    req: ScenarioSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_flow = await get_cash_flow_projection(workspace_id, current_user, db)
    orig_12m = base_flow.projections[-1].accumulated_cash_reserve

    sim_cash = base_flow.current_starting_cash
    for p in base_flow.projections:
        # Aplica variação de renda
        sim_income = p.projected_income * (Decimal("1.00") + (req.income_variation_percentage / Decimal("100.00")))
        sim_outflow = p.total_projected_outflow
        
        if req.one_off_expense_month == p.month:
            sim_outflow += req.one_off_extra_expense

        sim_cash += (sim_income - sim_outflow)

    impact = sim_cash - orig_12m
    resilient = sim_cash >= 0
    diag = "Seu caixa permanece positivo durante todo o período mesmo com o cenário adverso." if resilient else "ALERTA: Este cenário deixará o saldo negativo. Recomenda-se aumentar a reserva de emergência antes de assumir novos compromissos."

    return ScenarioSimulationResponse(
        scenario_description=f"Variação de Renda: {req.income_variation_percentage}% | Gasto Extra: R$ {req.one_off_extra_expense:,.2f}",
        original_cash_12_months=orig_12m,
        simulated_cash_12_months=sim_cash,
        impact_difference=impact,
        is_resilient=resilient,
        diagnosis=diag
    )


# ==================== 5. PARSER OFX & CSV COM CATEGORIZAÇÃO INTELIGENTE (ISSUE #16) ====================

CATEGORY_RULES = [
    (r"(?i)(ifood|rappi|restaurante|mcdonalds|burger|padaria|supermercado|carrefour|pao de acucar|assai)", "Alimentação", "essential"),
    (r"(?i)(uber|99app|posto|ipiranga|combustivel|gasolina|estacionamento|pedagio|sem parar)", "Transporte", "essential"),
    (r"(?i)(aluguel|condominio|enel|sabesp|cpfl|claro|vivo|internet|energia|copel)", "Moradia", "essential"),
    (r"(?i)(farmacia|drogaria|hospital|consulta|laboratorio|unimed|fleury|raia|drogasil)", "Saúde", "essential"),
    (r"(?i)(netflix|spotify|cinema|steam|playstation|amazon prime|disney|bar|churrascaria)", "Lazer & Conforto", "lifestyle"),
    (r"(?i)(salario|pro-labore|pix recebido|ted recebida|dividendos|rendimento)", "Receitas", "essential"),
]

@router.post("/{workspace_id}/import/parse", response_model=ImportParseResponse, summary="Parser de Extratos OFX e CSV com Sugestão")
async def parse_import_file(
    workspace_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_workspace_membership(workspace_id, current_user.id, db)

    # Carrega categorias do workspace
    stmt_cats = select(Category).where(Category.workspace_id == workspace_id)
    workspace_cats = {c.name.lower(): c for c in (await db.execute(stmt_cats)).scalars().all()}

    content = await file.read()
    filename = file.filename or "extrato"
    ext = filename.split(".")[-1].lower()

    candidates: List[ImportedTransactionCandidate] = []
    total_inc = Decimal("0.00")
    total_exp = Decimal("0.00")

    if ext == "ofx":
        text = content.decode("utf-8", errors="ignore")
        # Extrai blocos <STMTTRN>
        trn_blocks = re.findall(r"<STMTTRN>([\s\S]*?)</STMTTRN>", text)
        for block in trn_blocks:
            trntype = re.search(r"<TRNTYPE>(.*)", block)
            dtposted = re.search(r"<DTPOSTED>(\d{8})", block)
            trnamt = re.search(r"<TRNAMT>([-\d\.]+)", block)
            memo = re.search(r"<MEMO>(.*)", block)
            fitid = re.search(r"<FITID>(.*)", block)

            if dtposted and trnamt:
                d_str = dtposted.group(1)
                tx_date = date(int(d_str[0:4]), int(d_str[4:6]), int(d_str[6:8]))
                amt_val = Decimal(trnamt.group(1).strip())
                desc = memo.group(1).strip() if memo else "Transação OFX"
                fit = fitid.group(1).strip() if fitid else None

                tx_type = "income" if amt_val > 0 else "expense"
                abs_amt = abs(amt_val)

                if tx_type == "income":
                    total_inc += abs_amt
                else:
                    total_exp += abs_amt

                # Sugestão por regex
                sugg_cat_name = "Outros"
                sugg_ess = "lifestyle"
                conf = 0.5
                for pattern, cat_name, ess in CATEGORY_RULES:
                    if re.search(pattern, desc):
                        sugg_cat_name = cat_name
                        sugg_ess = ess
                        conf = 0.95
                        break

                cat_obj = workspace_cats.get(sugg_cat_name.lower())

                candidates.append(
                    ImportedTransactionCandidate(
                        external_id=fit,
                        transaction_date=tx_date,
                        amount=abs_amt,
                        type=tx_type,
                        description=desc,
                        suggested_category_id=cat_obj.id if cat_obj else None,
                        suggested_category_name=sugg_cat_name,
                        suggested_essentiality=sugg_ess,
                        confidence_score=conf
                    )
                )

    else: # CSV
        text = content.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(text), delimiter="," if "," in text else ";")
        for row in reader:
            if len(row) >= 3 and any(char.isdigit() for char in row[0]):
                # Assume: Data, Descrição, Valor
                try:
                    # Tenta formatar data YYYY-MM-DD ou DD/MM/YYYY
                    raw_dt = row[0].strip()
                    if "/" in raw_dt:
                        d, m, y = map(int, raw_dt.split("/"))
                        tx_date = date(y, m, d)
                    else:
                        y, m, d = map(int, raw_dt.split("-"))
                        tx_date = date(y, m, d)

                    desc = row[1].strip()
                    amt_str = row[2].replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                    amt_val = Decimal(amt_str)
                    tx_type = "income" if amt_val > 0 else "expense"
                    abs_amt = abs(amt_val)

                    if tx_type == "income":
                        total_inc += abs_amt
                    else:
                        total_exp += abs_amt

                    sugg_cat_name = "Outros"
                    sugg_ess = "lifestyle"
                    conf = 0.5
                    for pattern, cat_name, ess in CATEGORY_RULES:
                        if re.search(pattern, desc):
                            sugg_cat_name = cat_name
                            sugg_ess = ess
                            conf = 0.95
                            break

                    cat_obj = workspace_cats.get(sugg_cat_name.lower())

                    candidates.append(
                        ImportedTransactionCandidate(
                            external_id=None,
                            transaction_date=tx_date,
                            amount=abs_amt,
                            type=tx_type,
                            description=desc,
                            suggested_category_id=cat_obj.id if cat_obj else None,
                            suggested_category_name=sugg_cat_name,
                            suggested_essentiality=sugg_ess,
                            confidence_score=conf
                        )
                    )
                except Exception:
                    continue

    return ImportParseResponse(
        filename=filename,
        format=ext.upper(),
        total_found=len(candidates),
        total_amount_income=total_inc,
        total_amount_expense=total_exp,
        candidates=candidates
    )
