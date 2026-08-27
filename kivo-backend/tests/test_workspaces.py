import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def run_workspaces_test_suite():
    print("\n==========================================")
    print("INICIANDO TESTES DE WORKSPACES & MEMBROS")
    print("==========================================\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        ts = int(asyncio.get_event_loop().time() * 1000)
        email1 = f"anselmo.ws.{ts}@kivo.app"
        email2 = f"nathalia.ws.{ts}@kivo.app"
        pwd = "SenhaForte123#Kivo"

        # 1. Registra 2 usuarios
        print("1. Registrando usuarios Anselmo e Nathalia...")
        res1 = await client.post("/auth/register", json={
            "email": email1,
            "password": pwd,
            "full_name": "Anselmo Nonato",
            "initial_workspace_name": "Financas Anselmo (Solo)"
        })
        assert res1.status_code == 201
        token1 = res1.json()["access_token"]

        res2 = await client.post("/auth/register", json={
            "email": email2,
            "password": pwd,
            "full_name": "Nathalia Nonato",
            "initial_workspace_name": "Financas Nathalia (Solo)"
        })
        assert res2.status_code == 201
        token2 = res2.json()["access_token"]
        print("  OK: Ambos os usuarios registrados com sucesso.")

        # 2. Listar Workspaces do Anselmo
        print("2. Listando workspaces do Anselmo...")
        res = await client.get("/workspaces", headers={"Authorization": f"Bearer {token1}"})
        assert res.status_code == 200
        ws_list = res.json()
        assert len(ws_list) == 1
        assert ws_list[0]["type"] == "solo"
        print("  OK: Workspace Solo padrao listado com sucesso.")

        # 3. Criar Workspace Familia
        print("3. Criando Workspace Familia (Anselmo & Nathalia)...")
        res = await client.post("/workspaces", json={
            "name": "Familia Nonato",
            "type": "family",
            "currency": "BRL"
        }, headers={"Authorization": f"Bearer {token1}"})
        assert res.status_code == 201
        family_ws = res.json()
        family_ws_id = family_ws["id"]
        assert family_ws["type"] == "family"
        assert len(family_ws["members"]) == 1
        member1_id = family_ws["members"][0]["id"]
        print(f"  OK: Workspace Familia criado com ID: {family_ws_id}")

        # 4. Atualizar Renda do Anselmo no Workspace Familia (R$ 13.000,00)
        print("4. Atualizando renda declarada do Anselmo (R$ 13.000,00)...")
        res = await client.put(f"/workspaces/{family_ws_id}/members/{member1_id}", json={
            "declared_income": 13000.00
        }, headers={"Authorization": f"Bearer {token1}"})
        assert res.status_code == 200
        assert float(res.json()["declared_income"]) == 13000.00
        print("  OK: Renda do Anselmo atualizada com sucesso.")

        # 5. Adicionar Nathalia ao Workspace Familia (R$ 7.000,00)
        print("5. Adicionando Nathalia ao Workspace Familia (R$ 7.000,00)...")
        res = await client.post(f"/workspaces/{family_ws_id}/members", json={
            "email": email2,
            "display_name": "Nathalia Nonato",
            "role": "admin",
            "declared_income": 7000.00
        }, headers={"Authorization": f"Bearer {token1}"})
        assert res.status_code == 201
        member2_data = res.json()
        assert float(member2_data["declared_income"]) == 7000.00
        print("  OK: Nathalia adicionada como Admin ao Workspace Familia.")

        # 6. Consultar Detalhes do Workspace Familia
        print("6. Consultando detalhes completos do Workspace Familia...")
        res = await client.get(f"/workspaces/{family_ws_id}", headers={"Authorization": f"Bearer {token2}"})
        assert res.status_code == 200
        detail = res.json()
        assert len(detail["members"]) == 2
        print(f"  OK: Workspace Familia contem {len(detail['members'])} membros.")

    print("\n==========================================")
    print("TODOS OS TESTES DE WORKSPACE & MEMBROS PASSARAM COM SUCESSO!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_workspaces_test_suite())
