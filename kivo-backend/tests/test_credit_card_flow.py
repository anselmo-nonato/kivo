import asyncio
import httpx
import uuid
import random

BASE_URL = "http://localhost:8000/api/v1"

async def run_credit_card_test_suite():
    print("\n==========================================")
    print("INICIANDO TESTES DO FLUXO DE CARTÃO DE CRÉDITO & FATURA")
    print("==========================================\n")

    unique_id = random.randint(100000, 999999)
    email = f"cartao.teste.{unique_id}@kivo.app"
    password = "Test@Password123!"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Registro e Login
        print(f"1. Registrando usuário {email}...")
        res = await client.post("/auth/register", json={
            "email": email,
            "full_name": "Usuário Teste Cartão",
            "password": password
        })
        assert res.status_code == 201, f"Falha no registro: {res.text}"
        data = res.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        ws_res = await client.get("/workspaces", headers=headers)
        workspace = ws_res.json()[0]
        workspace_id = workspace["id"]
        ws_detail = await client.get(f"/workspaces/{workspace_id}", headers=headers)
        member_id = ws_detail.json()["members"][0]["id"]
        print(f"  ✓ Usuário autenticado. Workspace: {workspace_id}")

        # 2. Criar Conta Corrente e Cartão de Crédito
        print("2. Criando Conta Corrente (R$ 10.000,00) e Cartão Sicoob (Limite R$ 6.200,00)...")
        res_checking = await client.post(f"/workspaces/{workspace_id}/accounts", headers=headers, json={
            "name": "Conta Corrente Sicoob",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 10000.00
        })
        assert res_checking.status_code == 201, res_checking.text
        checking_acc = res_checking.json()
        assert float(checking_acc["current_balance"]) == 10000.00

        res_card = await client.post(f"/workspaces/{workspace_id}/accounts", headers=headers, json={
            "name": "Cartão Sicoob",
            "type": "credit_card",
            "owner_member_id": member_id,
            "initial_balance": 0.00,
            "credit_limit": 6200.00,
            "closing_day": 5,
            "due_day": 12
        })
        assert res_card.status_code == 201, res_card.text
        card_acc = res_card.json()
        assert float(card_acc["credit_limit"]) == 6200.00
        assert float(card_acc["used_limit"]) == 0.00
        assert float(card_acc["available_limit"]) == 6200.00
        print("  ✓ Cartão criado com Limite Total R$ 6.200,00 e Limite Disponível R$ 6.200,00.")

        # 3. Categorias e Centro de Custo
        cat_res = await client.get(f"/workspaces/{workspace_id}/categories", headers=headers)
        categories = cat_res.json()
        cat_id = categories[0]["id"]

        cc_res = await client.get(f"/workspaces/{workspace_id}/cost-centers", headers=headers)
        cost_centers = cc_res.json()
        cc_id = cost_centers[0]["id"]

        # 4. Lançar Compra Avulsa de R$ 1.200,00 no Cartão
        print("3. Lançando compra à vista de R$ 1.200,00 no Cartão...")
        tx1_res = await client.post(f"/workspaces/{workspace_id}/transactions", headers=headers, json={
            "account_id": card_acc["id"],
            "paid_by_member_id": member_id,
            "cost_center_id": cc_id,
            "category_id": cat_id,
            "amount": 1200.00,
            "type": "expense",
            "essentiality": "essential",
            "transaction_date": "2026-09-09",
            "status": "paid",
            "description": "Supermercado Mensal"
        })
        assert tx1_res.status_code == 201, tx1_res.text

        # Verificar limites do cartão
        accs_res = await client.get(f"/workspaces/{workspace_id}/accounts", headers=headers)
        card_now = next(a for a in accs_res.json() if a["id"] == card_acc["id"])
        print(f"  ✓ Após compra de R$ 1.200,00: Usado = R$ {card_now['used_limit']}, Disponível = R$ {card_now['available_limit']}")
        assert float(card_now["used_limit"]) == 1200.00
        assert float(card_now["available_limit"]) == 5000.00

        # 5. Lançar Compra Parcelada de 5x R$ 200,00 (R$ 1.000,00) no Cartão
        print("4. Lançando compra parcelada de 5x R$ 200,00 (R$ 1.000,00) no Cartão...")
        tx2_res = await client.post(f"/workspaces/{workspace_id}/transactions", headers=headers, json={
            "account_id": card_acc["id"],
            "paid_by_member_id": member_id,
            "cost_center_id": cc_id,
            "category_id": cat_id,
            "amount": 200.00,
            "type": "expense",
            "essentiality": "lifestyle",
            "transaction_date": "2026-09-09",
            "total_installments": 5,
            "description": "Monitor Gamer UltraWide"
        })
        assert tx2_res.status_code == 201, tx2_res.text

        # Verificar limites do cartão após parcelamento
        accs_res = await client.get(f"/workspaces/{workspace_id}/accounts", headers=headers)
        card_now = next(a for a in accs_res.json() if a["id"] == card_acc["id"])
        print(f"  ✓ Após parcelamento: Usado = R$ {card_now['used_limit']}, Disponível = R$ {card_now['available_limit']}")
        assert float(card_now["used_limit"]) == 2200.00
        assert float(card_now["available_limit"]) == 4000.00

        # 6. Realizar Pagamento da Fatura do Cartão de R$ 1.500,00 via Conta Corrente
        print("5. Pagando R$ 1.500,00 da fatura do Cartão via Conta Corrente...")
        pay_res = await client.post(f"/workspaces/{workspace_id}/accounts/{card_acc['id']}/pay-invoice", headers=headers, json={
            "source_account_id": checking_acc["id"],
            "amount": 1500.00,
            "payment_date": "2026-09-09",
            "notes": "Pagamento parcial Fatura Setembro"
        })
        assert pay_res.status_code == 201, pay_res.text
        card_post_pay = pay_res.json()
        print(f"  ✓ Pós-pagamento: Cartão Usado = R$ {card_post_pay['used_limit']}, Disponível = R$ {card_post_pay['available_limit']}")
        assert float(card_post_pay["used_limit"]) == 700.00
        assert float(card_post_pay["available_limit"]) == 5500.00

        # Verificar saldo da conta corrente
        accs_res = await client.get(f"/workspaces/{workspace_id}/accounts", headers=headers)
        checking_now = next(a for a in accs_res.json() if a["id"] == checking_acc["id"])
        print(f"  ✓ Saldo Conta Corrente pós débito: R$ {checking_now['current_balance']}")
        assert float(checking_now["current_balance"]) == 8500.00

        # 7. Recalibração / Ajuste direto do Limite Disponível
        print("6. Ajustando o Limite Disponível diretamente para R$ 5.800,00...")
        adj_res = await client.put(f"/workspaces/{workspace_id}/accounts/{card_acc['id']}", headers=headers, json={
            "adjusted_available_limit": 5800.00
        })
        assert adj_res.status_code == 200, adj_res.text
        card_adj = adj_res.json()
        print(f"  ✓ Limite pós ajuste: Usado = R$ {card_adj['used_limit']}, Disponível = R$ {card_adj['available_limit']}")
        assert float(card_adj["available_limit"]) == 5800.00
        assert float(card_adj["used_limit"]) == 400.00

        print("\n==========================================")
        print("✅ TESTES DE CARTÃO DE CRÉDITO E FATURA PASSARAM COM 100% DE SUCESSO!")
        print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_credit_card_test_suite())
