import asyncio
import httpx
from datetime import date
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

async def test_caixa_pdf_import_flow():
    print("\n" + "=" * 80)
    print("TESTANDO IMPORTACAO E CONCILIACAO INTELIGENTE DE PDF/COMPROVANTE CAIXA")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email = f"anselmo.caixa.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra usuario
        res = await client.post("/auth/register", json={
            "email": email,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Workspace Caixa Test",
        })
        assert res.status_code == 201, f"Erro ao registrar: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        ws_res = await client.get("/workspaces", headers=headers)
        assert ws_res.status_code == 200
        ws_id = ws_res.json()[0]["id"]

        ws_detail = await client.get(f"/workspaces/{ws_id}", headers=headers)
        member_id = ws_detail.json()["members"][0]["id"]

        # 2. Cria contas: Caixa e Sicoob
        res_caixa = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Caixa Economica",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 1000.00
        }, headers=headers)
        assert res_caixa.status_code == 201
        acc_caixa_id = res_caixa.json()["id"]

        res_sicoob = await client.post(f"/workspaces/{ws_id}/accounts", json={
            "name": "Sicoob Credicom",
            "type": "checking",
            "owner_member_id": member_id,
            "initial_balance": 500.00
        }, headers=headers)
        assert res_sicoob.status_code == 201
        acc_sicoob_id = res_sicoob.json()["id"]

        # 3. Upload do PDF real da Caixa para /import/parse
        with open("tests/sample_caixa.pdf", "rb") as f:
            pdf_bytes = f.read()

        files = {"file": ("comprovante2026-09-09_192804.pdf", pdf_bytes, "application/pdf")}
        data = {"account_id": acc_caixa_id}

        parse_res = await client.post(f"/workspaces/{ws_id}/import/parse", files=files, data=data, headers=headers)
        assert parse_res.status_code == 200, f"Erro no parse: {parse_res.text}"
        parse_data = parse_res.json()

        print(f"Formato detectado: {parse_data['format']}")
        print(f"Conta detectada: {parse_data['detected_account']}")
        print(f"Periodo: {parse_data['period_start']} a {parse_data['period_end']}")
        print(f"Saldo anterior: {parse_data['statement_balance']}")
        print(f"Total encontrado: {parse_data['total_found']} transacoes")

        assert parse_data["format"] == "PDF (Caixa Econômica Federal)"
        assert "0113" in parse_data["detected_account"]
        assert parse_data["total_found"] >= 3

        # 4. Validacao de deteccao de transferencias entre contas e categorizacao
        transfers = [c for c in parse_data["candidates"] if c["is_transfer"] is True]
        print(f"Transferencias entre contas auto-detectadas: {len(transfers)}")
        for t in transfers:
            print(f" -> {t['description']} | R$ {t['amount']} | Tipo: {t['type']} ({t['transfer_direction']})")

        assert len(transfers) >= 1
        pix_transfer = next(c for c in parse_data["candidates"] if float(c["amount"]) == 8771.17)
        assert pix_transfer["is_transfer"] is True
        assert pix_transfer["type"] == "transfer"

        # 5. Executa a transferencia via endpoint POST /transfers
        tx_transfer_res = await client.post(f"/workspaces/{ws_id}/transfers", json={
            "source_account_id": acc_caixa_id,
            "destination_account_id": acc_sicoob_id,
            "paid_by_member_id": member_id,
            "amount": 8771.17,
            "transaction_date": pix_transfer["transaction_date"],
            "description": pix_transfer["description"],
            "notes": pix_transfer["notes"]
        }, headers=headers)
        assert tx_transfer_res.status_code == 201, f"Erro ao transferir: {tx_transfer_res.text}"
        print("Transferencia interbancaria executada com sucesso!")

        # 6. Re-executa o parse para testar anti-duplicidade da transferencia
        reparse_res = await client.post(f"/workspaces/{ws_id}/import/parse", files=files, data=data, headers=headers)
        assert reparse_res.status_code == 200
        reparse_data = reparse_res.json()
        matched_tx = next(c for c in reparse_data["candidates"] if float(c["amount"]) == 8771.17)
        print(f"Status de conciliacao apos transferencia: {matched_tx['reconciliation_status']} (is_duplicate={matched_tx['is_duplicate']})")
        assert matched_tx["is_duplicate"] is True
        assert matched_tx["reconciliation_status"] == "matched"

        print("\nSUCESSO TOTAL: Importacao de PDF Caixa + OCR + Auto-Deteccao de Transferencia + Anti-Duplicidade validados 100%!")

if __name__ == "__main__":
    asyncio.run(test_caixa_pdf_import_flow())
