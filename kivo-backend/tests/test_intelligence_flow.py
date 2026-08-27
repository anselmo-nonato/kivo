import asyncio
import httpx
from datetime import date
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

async def run_intelligence_test_suite():
    print("\n==========================================")
    print("INICIANDO TESTES DE INTELIGÊNCIA (EQUALIZAÇÃO CASAL, DÍVIDAS, SIMULADOR E DTI)")
    print("==========================================\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email1 = f"anselmo.intel.{ts}@kivo.app"
        email2 = f"nathalia.intel.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra Usuários Anselmo (R$ 13k) e Nathália (R$ 7k)
        print("1. Criando Workspace Família com Anselmo (R$ 13.000) e Nathália (R$ 7.000)...")
        res1 = await client.post("/auth/register", json={
            "email": email1,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Solo"
        })
        token1 = res1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        res2 = await client.post("/auth/register", json={
            "email": email2,
            "password": pwd,
            "full_name": "Nathália Nonato",
            "initial_workspace_name": "Solo"
        })
        token2 = res2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Cria Workspace Família
        ws_res = await client.post("/workspaces", json={
            "name": "Família Inteligente",
            "type": "family",
            "currency": "BRL"
        }, headers=headers1)
        ws_id = ws_res.json()["id"]
        member1_id = ws_res.json()["members"][0]["id"]

        # Atualiza renda Anselmo
        await client.put(f"/workspaces/{ws_id}/members/{member1_id}", json={"declared_income": 13000.00}, headers=headers1)
        # Adiciona Nathália
        res_m2 = await client.post(f"/workspaces/{ws_id}/members", json={
            "email": email2,
            "display_name": "Nathália Nonato",
            "role": "admin",
            "declared_income": 7000.00
        }, headers=headers1)
        member2_id = res_m2.json()["id"]
        print("  OK: Workspace Família configurado (Total R$ 20.000,00: Anselmo 65%, Nathália 35%).")

        # 2. Configura Conta Corrente e Centros de Custo
        res_acc = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Conta Conjunta",
            "type": "checking",
            "owner_member_id": member1_id,
            "initial_balance": 10000.00
        }, headers=headers1)
        acc_id = res_acc.json()["id"]

        ccs = (await client.get(f"/workspaces/{ws_id}/cost-centers", headers=headers1)).json()
        cats = (await client.get(f"/workspaces/{ws_id}/categories", headers=headers1)).json()
        cc_casa = [c for c in ccs if c["scope"] == "home"][0]["id"]
        cat_moradia = [c for c in cats if c["name"] == "Moradia"][0]["id"]

        # 3. Lança Despesa Compartilhada da Casa (R$ 4.000,00 paga 100% pelo Anselmo)
        print("2. Lançando R$ 4.000,00 de despesa compartilhada da Casa paga por Anselmo...")
        await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_id,
            "paid_by_member_id": member1_id,
            "cost_center_id": cc_casa,
            "category_id": cat_moradia,
            "amount": 4000.00,
            "type": "expense",
            "essentiality": "essential",
            "transaction_date": str(date.today()),
            "description": "Aluguel + Condomínio Casa",
            "status": "paid"
        }, headers=headers1)

        # 4. Validar Relatório de Equalização (Issue #8)
        print("3. Validando cálculo de rateio proporcional (Equalização do Casal)...")
        month_str = date.today().strftime("%Y-%m")
        res_eq = await client.get(f"/workspaces/{ws_id}/equalization?month={month_str}", headers=headers1)
        assert res_eq.status_code == 200
        eq_data = res_eq.json()
        
        assert float(eq_data["total_shared_expenses"]) == 4000.00
        assert float(eq_data["total_combined_income"]) == 20000.00
        # Anselmo: Cota 65% = 2600. Pagou 4000. Saldo = +1400
        # Nathalia: Cota 35% = 1400. Pagou 0. Saldo = -1400
        assert float(eq_data["amount_to_transfer"]) == 1400.00
        assert eq_data["payer_name"] == "Nathália Nonato"
        assert eq_data["receiver_name"] == "Anselmo Nonato"
        print(f"  OK: Rateio justo validado! Sugestão gerada: {eq_data['settlement_suggestion']}")

        # 5. Cadastrar Dívidas (Issue #9)
        print("4. Cadastrando dívidas do casal (Rotativo de Cartão e Empréstimo Bancário)...")
        res_d1 = await client.post(f"/workspaces/{ws_id}/debts", json={
            "member_id": member1_id,
            "creditor_name": "Cartão de Crédito Rotativo",
            "original_amount": 8000.00,
            "current_balance": 8000.00,
            "monthly_interest_rate": 0.1200, # 12% a.m.
            "installment_amount": 1200.00,
            "remaining_installments": 10,
            "due_day": 10
        }, headers=headers1)
        assert res_d1.status_code == 201
        debt1_id = res_d1.json()["id"]

        res_d2 = await client.post(f"/workspaces/{ws_id}/debts", json={
            "member_id": member1_id,
            "creditor_name": "Empréstimo Pessoal Caixa",
            "original_amount": 15000.00,
            "current_balance": 15000.00,
            "monthly_interest_rate": 0.0350, # 3.5% a.m.
            "installment_amount": 850.00,
            "remaining_installments": 24,
            "due_day": 20
        }, headers=headers1)
        assert res_d2.status_code == 201
        print("  OK: Dívidas cadastradas com sucesso.")

        # 6. Testar Amortização Extraordinária (Issue #9)
        print("5. Testando amortização extraordinária de R$ 2.000 no Cartão Rotativo...")
        res_amort = await client.post(f"/workspaces/{ws_id}/debts/{debt1_id}/amortize", json={
            "extra_amount": 2000.00,
            "account_id": acc_id,
            "strategy": "reduce_term"
        }, headers=headers1)
        assert res_amort.status_code == 200
        assert float(res_amort.json()["current_balance"]) == 6000.00
        assert res_amort.json()["remaining_installments"] == 5
        print(f"  OK: Saldo devedor abatido para R$ {res_amort.json()['current_balance']} e prazo reduzido para {res_amort.json()['remaining_installments']} meses.")

        # 7. Testar Simulador Avalanche vs Bola de Neve (Issue #10)
        print("6. Executando simulação de quitação (Método Avalanche vs Bola de Neve)...")
        res_sim = await client.get(f"/workspaces/{ws_id}/debts/simulate?extra_monthly_budget=1000", headers=headers1)
        assert res_sim.status_code == 200
        sim = res_sim.json()
        assert "Avalanche" in sim["avalanche"]["strategy_name"]
        assert "Bola de Neve" in sim["snowball"]["strategy_name"]
        assert sim["avalanche"]["months_to_payoff"] > 0
        print(f"  OK: Simulação concluída! Recomendação: {sim['recommendation']}")

        # 8. Testar Termômetro DTI (Debt-to-Income) (Issue #11)
        print("7. Calculando indicador DTI (Debt-to-Income)...")
        res_dti = await client.get(f"/workspaces/{ws_id}/debts/dti", headers=headers1)
        assert res_dti.status_code == 200
        dti = res_dti.json()
        # Renda: 20.000. Parcelas: 1200 + 850 = 2050 -> DTI = 10.25% (Saudável < 20%)
        assert float(dti["dti_percentage"]) == 10.25
        assert "Saudável" in dti["classification"]
        print(f"  OK: Termômetro DTI = {dti['dti_percentage']}% [{dti['classification']}] - Cor: {dti['status_color']}")

    print("\n==========================================")
    print("✅ TODOS OS TESTES DE INTELIGÊNCIA FINANCEIRA PASSARAM COM 100% DE SUCESSO!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_intelligence_test_suite())
