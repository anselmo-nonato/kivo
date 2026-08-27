# Padrões de Desenvolvimento, Validações e Qualidade — KIVO

**Status:** Aprovado  
**Padrão de Qualidade:** Clean Architecture, 100% Type-Safe, Test-Driven para Regras Financeiras  

---

## 1. Padrões de Validação e DTOs (Pydantic V2)

Todas as entradas da API passam obrigatoriamente por esquemas estritos do Pydantic antes de atingir os serviços de negócio.

### 1.1. Regras de Ouro de Validação:
1. **Valores Monetários:** Sempre validados como `Decimal` com 2 casas decimais e restrição de sinal (`gt=0` para montantes de transação).
2. **Datas:** `date` no formato ISO 8601 (`YYYY-MM-DD`). Transações não podem ter datas com mais de 5 anos no passado ou 2 anos no futuro.
3. **Strings Sanitizadas:** Strings como descrição e notas passam por `strip_whitespace` e remoção de scripts maliciosos.

---

## 2. Estrutura e Organização do Código (Clean Architecture)

```
kivo-backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # Rotas de Login, Registro e 2FA
│   │   │   │   ├── transactions.py  # CRUD e filtros de transações
│   │   │   │   ├── debts.py         # Módulo Sair do Vermelho
│   │   │   │   ├── radar.py         # Tetos e alertas de gastos
│   │   │   │   └── projections.py   # Fluxo de caixa preditivo
│   │   │   └── api_router.py
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (.env)
│   │   ├── security.py              # JWT, Argon2id, TOTP RFC 6238
│   │   └── database.py              # Async SQLAlchemy Engine & Session
│   ├── models/                      # SQLAlchemy Declarative Models
│   ├── schemas/                     # Pydantic DTOs (Request / Response)
│   ├── services/                    # Regras de Negócio Puras (Math / Finance)
│   │   ├── settlement_service.py    # Algoritmo de Equalização do Casal
│   │   ├── debt_payoff_service.py   # Algoritmo Avalanche vs. Bola de Neve
│   │   └── radar_service.py         # Detector de Desperdício e Ritmo
│   └── tests/                       # Pytest (Unitários & Integração)
```

---

## 3. Ambiente Docker Compose para Desenvolvimento

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: kivo_postgres
    environment:
      POSTGRES_DB: kivo_db
      POSTGRES_USER: kivo_admin
      POSTGRES_PASSWORD: kivo_secret_local
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: kivo_redis
    ports:
      - "6379:6379"

  api:
    build: ./kivo-backend
    container_name: kivo_api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./kivo-backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://kivo_admin:kivo_secret_local@postgres:5432/kivo_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev_jwt_secret_key_kivo
    depends_on:
      - postgres
      - redis

  web:
    build: ./kivo-frontend
    container_name: kivo_web
    command: npm run dev
    volumes:
      - ./kivo-frontend:/app
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 4. Estratégia de Testes Automatizados

1. **Testes Unitários:** Foco total nos cálculos financeiros matemáticos (`Decimal`, juros compostos, quitação de dívidas, equalização proporcional de renda).
2. **Testes de Integração de API:** Validação de ponta a ponta dos fluxos de login com 2FA, isolamento entre Workspaces e consistência do extrato bancário.
