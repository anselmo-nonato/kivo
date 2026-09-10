import asyncio
import httpx
from datetime import date
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

async def test_sicoob_pdf_import_flow():
    print("\n" + "=" * 80)
    print("TESTANDO IMPORTACAO E CONCILIACAO INTELIGENTE DE PDF SICOOB")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email = f"anselmo.sicoob.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra usuario
        res = await client.post("/auth/register", json={
            "email": email,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Workspace Sicoob Test",
        })
        assert res.status_code == 201, f"Erro ao registrar: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        ws_res = await client.get("/workspaces", headers=headers)
        assert ws_res.status_code == 200
        ws_id = ws_res.json()[0]["id"]

        ws_detail = await client.get(f"/workspaces/{ws_id}", headers=headers)
        member_id = ws_detail.json()["members"][0]["id"]

        # 2. Cria conta bancaria Sicoob
        res_acc = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Sicoob Credicom",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 0.00
        }, headers=headers)
        assert res_acc.status_code == 201
        acc_id = res_acc.json()["id"]

        cc_res = await client.get(f"/workspaces/{ws_id}/cost-centers", headers=headers)
        cc_id = cc_res.json()[0]["id"]

        cat_res = await client.get(f"/workspaces/{ws_id}/categories", headers=headers)
        cat_id = cat_res.json()[0]["id"]

        # 3. Cria uma transacao previa para testar anti-duplicidade: 5483.16 em 2026-09-04
        prev_tx = await client.post(f"/workspaces/{ws_id}/transactions", json={
            "account_id": acc_id,
            "paid_by_member_id": member_id,
            "cost_center_id": cc_id,
            "category_id": cat_id,
            "amount": 5483.16,
            "type": "expense",
            "essentiality": "essential",
            "transaction_date": "2026-09-04",
            "description": "Pagamento Fatura Previa Manual",
            "status": "paid"
        }, headers=headers)
        assert prev_tx.status_code == 201

        # 4. Upload do PDF real para /import/parse
        with open("tests/sample_sicoob.pdf", "rb") as f:
            pdf_bytes = f.read()

        files = {"file": ("sicoob_2026_09_09_12_36_55.pdf", pdf_bytes, "application/pdf")}
        data = {"account_id": acc_id}

        parse_res = await client.post(f"/workspaces/{ws_id}/import/parse", files=files, data=data, headers=headers)
        assert parse_res.status_code == 200, f"Erro no parse: {parse_res.text}"
        parse_data = parse_res.json()

        print(f"Formato detectado: {parse_data['format']}")
        print(f"Conta detectada: {parse_data['detected_account']}")
        print(f"Periodo: {parse_data['period_start']} a {parse_data['period_end']}")
        print(f"Saldo em conta: {parse_data['statement_balance']}")
        print(f"Total encontrado: {parse_data['total_found']} transacoes")

        assert parse_data["format"] == "PDF (Sicoob SISBR)"
        assert "90.627.574-1" in parse_data["detected_account"]
        assert parse_data["period_start"] == "2026-09-01"
        assert parse_data["period_end"] == "2026-09-09"
        assert parse_data["total_found"] > 0

        # 5. Validacao do Anti-Duplicacao
        matched_candidates = [c for c in parse_data["candidates"] if c["is_duplicate"] is True]
        print(f"Transacoes ja existentes detectadas (Anti-Duplicidade): {len(matched_candidates)}")
        assert len(matched_candidates) >= 1
        assert matched_candidates[0]["reconciliation_status"] == "matched"

        future_candidates = [c for c in parse_data["candidates"] if c["is_future"] is True]
        print(f"Lancamentos futuros identificados: {len(future_candidates)}")
        assert len(future_candidates) >= 2

        # 6. Importacao das transacoes selecionadas (apenas novas)
        to_import = [c for c in parse_data["candidates"] if not c["is_duplicate"] and not c["is_future"]]
        for c in to_import:
            tx_res = await client.post(f"/workspaces/{ws_id}/transactions", json={
                "account_id": acc_id,
                "paid_by_member_id": member_id,
                "cost_center_id": cc_id,
                "category_id": c["suggested_category_id"] or cat_id,
                "amount": c["amount"],
                "type": c["type"],
                "essentiality": c["suggested_essentiality"],
                "transaction_date": c["transaction_date"],
                "description": c["description"],
                "notes": c["notes"],
                "status": "paid",
            }, headers=headers)
            assert tx_res.status_code == 201

        print(f"SUCESSO TOTAL: {len(to_import)} novas transacoes importadas com conciliacao 100% precisa.")

if __name__ == "__main__":
    asyncio.run(test_sicoob_pdf_import_flow())

