import asyncio
import httpx
from datetime import date
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

async def run_financial_test_suite():
    print("\n==========================================")
    print("INICIANDO TESTES DO MOTOR FINANCEIRO (CONTAS, CATEGORIAS, TAGS E LANÇAMENTOS)")
    print("==========================================\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email = f"anselmo.fin.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra Usuário e pega Workspace
        print("1. Registrando usuário para o fluxo financeiro...")
        res = await client.post("/auth/register", json={
            "email": email,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Finanças Kivo Dev"
        })
        assert res.status_code == 201
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Pega workspace e membro
        ws_res = await client.get("/workspaces", headers=headers)
        ws_id = ws_res.json()[0]["id"]
        
        ws_detail = await client.get(f"/workspaces/{ws_id}", headers=headers)
        member_id = ws_detail.json()["members"][0]["id"]
        print(f"  OK: Workspace ID {ws_id} e Member ID {member_id}")

        # 2. Criar Contas Bancárias e Cartão (Issue #5)
        print("2. Criando Conta Corrente (Nubank) e Cartão de Crédito...")
        res_acc1 = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Nubank Conta Principal",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 5000.00
        }, headers=headers)
        assert res_acc1.status_code == 201
        acc_checking_id = res_acc1.json()["id"]

        res_acc2 = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Cartão XP Visa Infinite",
            "type": "credit_card",
            "owner_member_id": member_id,
            "initial_balance": 0.00,
            "credit_limit": 25000.00,
            "closing_day": 5,
            "due_day": 12
        }, headers=headers)
        assert res_acc2.status_code == 201
        acc_card_id = res_acc2.json()["id"]
        print("  OK: Contas bancárias e cartões criados.")

        # 3. Listar Centros de Custo e Categorias Padrão (Issue #6)
        print("3. Obtendo Centros de Custo e Categorias...")
        ccs = (await client.get(f"/workspaces/{ws_id}/cost-centers", headers=headers)).json()
        cats = (await client.get(f"/workspaces/{ws_id}/categories", headers=headers)).json()
        assert len(ccs) >= 2
        assert len(cats) >= 6
        cc_casa_id = ccs[0]["id"]
        cat_moradia_id = [c for c in cats if c["name"] == "Moradia"][0]["id"]
        cat_receita_id = [c for c in cats if c["name"] == "Receitas"][0]["id"]
        print("  OK: Centros de custo e categorias obtidos.")

        # 4. Criar Tags Transversais de Projeto/Evento (Issue #17)
        print("4. Criando Tags (#Reforma2026 e #ViagemGramado)...")
        res_t1 = await client.post(f"/workspaces/{ws_id}/tags", json={"name": "Reforma2026", "color": "#F59E0B"}, headers=headers)
        res_t2 = await client.post(f"/workspaces/{ws_id}/tags", json={"name": "ViagemGramado", "color": "#10B981"}, headers=headers)
        assert res_t1.status_code == 201
        assert res_t2.status_code == 201
        tag_reforma_id = res_t1.json()["id"]
        tag_viagem_id = res_t2.json()["id"]
        print("  OK: Tags criadas.")

        # 5. Criar Transação de Receita (Issue #7)
        print("5. Lançando Receita (Salário: R$ 13.000,00)...")
        res_inc = await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_checking_id,
            "paid_by_member_id": member_id,
            "cost_center_id": cc_casa_id,
            "category_id": cat_receita_id,
            "amount": 13000.00,
            "type": "income",
            "essentiality": "essential",
            "transaction_date": str(date.today()),
            "description": "Salário Mensal",
            "status": "paid"
        }, headers=headers)
        assert res_inc.status_code == 201
        print("  OK: Receita registrada.")

        # 6. Criar Lançamento Parcelado com TAG (10 parcelas de R$ 1.200,00 com tag #Reforma2026)
        print("6. Lançando Despesa Parcelada (Móveis: 10x de R$ 1.200,00 com Tag #Reforma2026)...")
        res_inst = await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_card_id,
            "paid_by_member_id": member_id,
            "cost_center_id": cc_casa_id,
            "category_id": cat_moradia_id,
            "amount": 1200.00,
            "type": "expense",
            "essentiality": "essential",
            "transaction_date": str(date.today()),
            "description": "Móveis Planejados Cozinha",
            "status": "paid",
            "total_installments": 10,
            "tag_ids": [tag_reforma_id]
        }, headers=headers)
        assert res_inst.status_code == 201
        created_installments = res_inst.json()
        assert len(created_installments) == 10
        assert created_installments[0]["installment_current"] == 1
        assert created_installments[9]["installment_current"] == 10
        assert len(created_installments[0]["tags"]) == 1
        print(f"  OK: 10 parcelas geradas com sucesso vinculadas à Tag #{created_installments[0]['tags'][0]['name']}")

        # 7. Validar Relatório Consolidado por Tag (Issue #17)
        print("7. Consultando Relatório Consolidado de Projetos por Tag...")
        res_tag_rep = await client.get(f"/workspaces/{ws_id}/tags/report", headers=headers)
        assert res_tag_rep.status_code == 200
        tag_items = res_tag_rep.json()
        reforma_item = [t for t in tag_items if t["tag_name"] == "Reforma2026"][0]
        # Total acumulado de despesas na tag (10 x 1.200 = 12.000)
        assert float(reforma_item["total_expense"]) == 12000.00
        assert reforma_item["transaction_count"] == 10
        print(f"  OK: Relatório da Tag #Reforma2026 calculou acumulado total exato: R$ {reforma_item['total_expense']}")

        # 8. Validar Saldo da Conta Bancária (Issue #5)
        print("8. Verificando cálculo de Saldo da Conta Corrente...")
        accs = (await client.get(f"/workspaces/{ws_id}/accounts", headers=headers)).json()
        checking_acc = [a for a in accs if a["id"] == acc_checking_id][0]
        # Saldo inicial (5000) + Receita (13000) = 18000
        assert float(checking_acc["current_balance"]) == 18000.00
        print(f"  OK: Saldo atualizado com precisão: R$ {checking_acc['current_balance']}")

        # 9. Validar Resumo Mensal por Essencialidade (Issue #7)
        print("9. Consultando Resumo Mensal de Essencialidade...")
        month_str = date.today().strftime("%Y-%m")
        res_sum = await client.get(f"/workspaces/{ws_id}/summary?month={month_str}", headers=headers)
        assert res_sum.status_code == 200
        summary = res_sum.json()
        assert float(summary["total_income"]) == 13000.00
        print(f"  OK: Resumo mensal: Receita R$ {summary['total_income']}, Despesas R$ {summary['total_expense']}, Economia Líquida R$ {summary['net_savings']} ({summary['savings_rate_percentage']}%)")

    print("\n==========================================")
    print("✅ TODOS OS TESTES FINANCEIROS (CONTAS, CATEGORIAS, TAGS E LANÇAMENTOS) PASSARAM COM 100% DE SUCESSO!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_financial_test_suite())
