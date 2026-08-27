import asyncio
import httpx
from datetime import date
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

async def run_analytics_test_suite():
    print("\n==========================================")
    print("INICIANDO TESTES DE ANALYTICS & AUTOMAÇÕES (RADAR, RALOS, RESERVA, PROJEÇÕES E OFX)")
    print("==========================================\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email = f"anselmo.analytics.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra Usuário e pega IDs
        print("1. Registrando usuário para o fluxo de Analytics...")
        res = await client.post("/auth/register", json={
            "email": email,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Kivo Analytics Space"
        })
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        ws_res = await client.get("/workspaces", headers=headers)
        ws_id = ws_res.json()[0]["id"]
        
        ws_detail = await client.get(f"/workspaces/{ws_id}", headers=headers)
        member_id = ws_detail.json()["members"][0]["id"]

        # Atualiza renda declarada (R$ 15.000,00)
        await client.put(f"/workspaces/{ws_id}/members/{member_id}", json={"declared_income": 15000.00}, headers=headers)

        # Cria conta corrente
        res_acc = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Conta Itaú Personalité",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 8000.00
        }, headers=headers)
        acc_id = res_acc.json()["id"]

        ccs = (await client.get(f"/workspaces/{ws_id}/cost-centers", headers=headers)).json()
        cats = (await client.get(f"/workspaces/{ws_id}/categories", headers=headers)).json()
        cc_casa = [c for c in ccs if c["scope"] == "home"][0]["id"]
        cat_alim = [c for c in cats if c["name"] == "Alimentação"][0]["id"]
        cat_moradia = [c for c in cats if c["name"] == "Moradia"][0]["id"]
        cat_lazer = [c for c in cats if c["name"] == "Lazer & Conforto"][0]["id"]

        # 2. Configurar Teto Orçamentário e Testar Radar (Issue #12)
        print("2. Configurando Teto Orçamentário para Alimentação (R$ 2.000,00)...")
        res_limit = await client.post(f"/workspaces/{ws_id}/radar/limits", json={
            "category_id": cat_alim,
            "limit_amount": 2000.00,
            "alert_threshold_percentage": 75.00
        }, headers=headers)
        assert res_limit.status_code == 201

        # Lança gasto de R$ 1.600 em Alimentação
        await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_id,
            "paid_by_member_id": member_id,
            "cost_center_id": cc_casa,
            "category_id": cat_alim,
            "amount": 1600.00,
            "type": "expense",
            "essentiality": "essential",
            "transaction_date": str(date.today()),
            "description": "Supermercado Mensal",
            "status": "paid"
        }, headers=headers)

        month_str = date.today().strftime("%Y-%m")
        res_radar = await client.get(f"/workspaces/{ws_id}/radar?month={month_str}", headers=headers)
        assert res_radar.status_code == 200
        radar = res_radar.json()
        assert float(radar["total_spent"]) == 1600.00
        assert float(radar["overall_percentage"]) == 80.00
        print(f"  OK: Radar de consumo: {radar['overall_percentage']}% consumido (Status: {radar['budgets'][0]['consumption_pace_status']})")

        # 3. Lançar Gasto Desconexo e Testar Relatório de Ralos (Issue #13)
        print("3. Testando Relatório de Desperdícios / Ralos Financeiros...")
        await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_id,
            "paid_by_member_id": member_id,
            "cost_center_id": cc_casa,
            "category_id": cat_lazer,
            "amount": 450.00,
            "type": "expense",
            "essentiality": "waste", # Classificação de Ralo
            "transaction_date": str(date.today()),
            "description": "Compra por Impulso Black Friday",
            "status": "paid"
        }, headers=headers)

        res_waste = await client.get(f"/workspaces/{ws_id}/waste?month={month_str}", headers=headers)
        assert res_waste.status_code == 200
        waste_rep = res_waste.json()
        assert float(waste_rep["total_waste_month"]) == 450.00
        assert float(waste_rep["total_waste_annualized"]) == 5400.00
        print(f"  OK: Ralo identificado: R$ {waste_rep['total_waste_month']} no mês (Impacto Anualizado: R$ {waste_rep['total_waste_annualized']}, Potencial 5 Anos: R$ {waste_rep['potential_patrimony_in_5_years']})")

        # 4. Testar Cofre da Reserva de Emergência (Issue #14)
        print("4. Testando Cofre da Reserva de Emergência...")
        res_fund_status = await client.get(f"/workspaces/{ws_id}/emergency-fund", headers=headers)
        assert res_fund_status.status_code == 200
        print(f"  Meta calculada dinamicamente: R$ {res_fund_status.json()['calculated_target_amount']} ({res_fund_status.json()['target_months']} meses de gastos essenciais)")

        # Realiza aporte de R$ 6.000 na reserva
        res_dep = await client.post(f"/workspaces/{ws_id}/emergency-fund/deposit", json={
            "amount": 6000.00,
            "account_id": acc_id
        }, headers=headers)
        assert res_dep.status_code == 200
        assert float(res_dep.json()["current_balance"]) == 6000.00
        print(f"  OK: Depósito realizado. Saldo da Reserva: R$ {res_dep.json()['current_balance']} (Cobertura: {res_dep.json()['months_covered']} meses - {res_dep.json()['status_classification']})")

        # 5. Testar Projeção de Fluxo de Caixa 12 Meses e Simulador de Stress (Issue #15)
        print("5. Testando Projeção de Fluxo de Caixa 12 Meses e Simulador de Cenários...")
        res_cf = await client.get(f"/workspaces/{ws_id}/cash-flow/12-months", headers=headers)
        assert res_cf.status_code == 200
        cf_data = res_cf.json()
        assert len(cf_data["projections"]) == 12
        print(f"  OK: 12 meses projetados. Saldo final estimado: R$ {float(cf_data['projections'][-1]['accumulated_cash_reserve']):,.2f}")

        # Simulação de Cenário de Stress (Queda de 20% na renda + Despesa extra de R$ 4.000)
        res_sim_scen = await client.post(f"/workspaces/{ws_id}/cash-flow/simulate-scenario", json={
            "income_variation_percentage": -20.00,
            "one_off_extra_expense": 4000.00,
            "one_off_expense_month": month_str
        }, headers=headers)
        assert res_sim_scen.status_code == 200
        sim_res = res_sim_scen.json()
        print(f"  OK: Cenário de Stress simulado: {sim_res['diagnosis']}")

        # 6. Testar Parser OFX com Categorização Inteligente (Issue #16)
        print("6. Testando Parser de Arquivo OFX de Extrato Bancário...")
        ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILENAME:NONE
NEWFILENAME:NONE
<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20260827
<TRNAMT>-84.90
<FITID>20260827001
<MEMO>IFOOD *RESTAURANTE
</STMTTRN>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20260827
<TRNAMT>-32.50
<FITID>20260827002
<MEMO>UBER *TRIP SAO PAULO
</STMTTRN>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20260827
<TRNAMT>-55.90
<FITID>20260827003
<MEMO>NETFLIX.COM MENSALIDADE
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT
<DTPOSTED>20260827
<TRNAMT>5000.00
<FITID>20260827004
<MEMO>PIX RECEBIDO PRO-LABORE
</STMTTRN>
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""

        files = {"file": ("extrato_nubank.ofx", ofx_content.encode("utf-8"), "application/octet-stream")}
        res_parse = await client.post(f"/workspaces/{ws_id}/import/parse", files=files, headers=headers)
        assert res_parse.status_code == 200
        parse_data = res_parse.json()
        assert parse_data["total_found"] == 4
        cands = parse_data["candidates"]
        
        # Valida categorização inteligente
        assert cands[0]["suggested_category_name"] == "Alimentação"
        assert cands[1]["suggested_category_name"] == "Transporte"
        assert cands[2]["suggested_category_name"] == "Lazer & Conforto"
        assert cands[3]["suggested_category_name"] == "Receitas"
        print(f"  OK: Parser OFX extraiu 4 lançamentos com classificação 100% precisa (iFood -> Alimentação, Uber -> Transporte, Netflix -> Lazer, Pix -> Receitas).")

    print("\n==========================================")
    print("✅ TODOS OS TESTES DE ANALYTICS & AUTOMAÇÕES PASSARAM COM 100% DE SUCESSO!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_analytics_test_suite())
