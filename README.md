# KIVO — A Chave da sua Virada Financeira 🚀

Plataforma inteligente de gestão financeira pessoal e familiar, construída com arquitetura REST API First, Clean Architecture, suporte a Multi-Tenancy (Modo Solo e Modo Família), 2FA nativo (Google Authenticator TOTP RFC 6238), Taxonomia 4D + Tags, Equalização Justa de Despesas do Casal e Motor de Quitação de Dívidas (Avalanche vs. Bola de Neve).

---

## 🏗️ Arquitetura e Stack Tecnológica

* **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 (Async) + Pydantic V2 + Alembic
* **Banco de Dados:** PostgreSQL 16 (Alpine) com tipos `NUMERIC(15,2)`, UUIDv7 e Row Level Security (RLS)
* **Cache & Sessões:** Redis 7 (Alpine)
* **Frontend:** Next.js 14 + React 18 + TypeScript + Tailwind CSS
* **Segurança:** Argon2id, JWT (Access + Refresh), TOTP RFC 6238 e Códigos de Recuperação de Uso Único
* **Infraestrutura:** Docker Compose com Healthchecks automatizados

---

## 🚀 Status das Entregas (Milestones v0.1 a v0.5 — 100% Concluídas)

| Milestone | Escopo | Issues Entregues | Status |
| :--- | :--- | :--- | :---: |
| **v0.1** | **Fundação & Multi-Tenant** | #1, #2, #3, #4 | 🟢 **100% Concluído** |
| **v0.2** | **Taxonomia 4D, Contas & Tags** | #5, #6, #7, #17 | 🟢 **100% Concluído** |
| **v0.3** | **Equalização & Dívidas** | #8, #9, #10, #11 | 🟢 **100% Concluído** |
| **v0.4** | **Radar, Desperdício & Reserva** | #12, #13, #14 | 🟢 **100% Concluído** |
| **v0.5** | **Projeções 12M & Parser OFX** | #15, #16 | 🟢 **100% Concluído** |

---

## 💻 Como Rodar o Projeto com Docker

```powershell
# 1. Iniciar todos os serviços
docker compose up -d --build

# 2. Executar a suíte de testes de ponta a ponta
docker exec kivo_api python tests/test_auth_2fa.py
docker exec kivo_api python tests/test_workspaces.py
docker exec kivo_api python tests/test_financial_flow.py
docker exec kivo_api python tests/test_intelligence_flow.py
docker exec kivo_api python tests/test_analytics_flow.py
```

### 🌐 Endpoints Locais:
* **Web App (Frontend):** [http://localhost:3000](http://localhost:3000)
* **API Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 📄 Documentação Técnica Completa

Consulte o diretório [`docs/`](./docs/) para manuais de produto, regras de negócio, contratos de API e modelos matemáticos:
* `docs/01_visao_e_objetivos.md` — Visão geral e proposta de valor
* `docs/02_modelo_de_dados_e_categorizacao.md` — Modelo 4D e Multi-Tenant
* `docs/03_indicadores_e_regras_de_negocio.md` — Algoritmos de Equalização e Quitação
* `docs/07_arquitetura_de_software_e_stack.md` — Clean Architecture & Docker
* `docs/08_autenticacao_e_seguranca_2fa.md` — RFC 6238 TOTP e Argon2id
* `docs/13_backlog_e_melhorias_futuras.md` — RFC Cartões de Crédito Avançados (#26)
* `docs/14_trusted_device_2fa_e_persistencia.md` — Especificação Dispositivos Confiáveis 30D (#27)

