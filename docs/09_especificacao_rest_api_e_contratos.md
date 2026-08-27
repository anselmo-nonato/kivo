# Especificação REST API Full e Contratos — KIVO

**Status:** Aprovado  
**Padrão de API:** RESTful OpenAPI 3.1  
**Formato de Dados:** JSON (`application/json`)  
**Padrão de Erro:** RFC 7807 (Problem Details)  

---

## 1. Princípios do Design RESTful

1. **Paridade Total com a Interface (100% API-First):** Toda e qualquer ação realizada na interface gráfica (botões, filtros, cadastros, simulações, importações) consome um endpoint REST público e documentado.
2. **Versionamento:** Prefixo `/api/v1/` em todas as rotas.
3. **Autenticação:** Header `Authorization: Bearer <access_token>` em rotas protegidas.
4. **Isolamento de Contexto:** Header `X-Workspace-Id: <uuid>` para alternar entre Modo Solo e Modo Família.

---

## 2. Catálogo de Recursos e Endpoints da API

### 2.1. Módulo: Autenticação & 2FA (`/api/v1/auth`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Criação de nova conta de usuário. |
| `POST` | `/api/v1/auth/login` | Login com e-mail e senha (retorna tokens ou desafio 2FA). |
| `POST` | `/api/v1/auth/2fa/setup` | Inicia configuração 2FA (retorna secret, QR Code e backup codes). |
| `POST` | `/api/v1/auth/2fa/enable` | Confirma primeiro código TOTP e ativa 2FA no perfil. |
| `POST` | `/api/v1/auth/2fa/verify` | Valida código TOTP durante o login em 2 etapas. |
| `POST` | `/api/v1/auth/2fa/disable` | Desativa 2FA mediante confirmação de senha + código atual. |
| `POST` | `/api/v1/auth/refresh` | Renovação do Access Token via Refresh Token. |
| `POST` | `/api/v1/auth/logout` | Revogação da sessão atual e invalidação de tokens. |

---

### 2.2. Módulo: Workspaces e Membros (`/api/v1/workspaces` & `/api/v1/members`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/workspaces` | Lista os workspaces aos quais o usuário tem acesso. |
| `POST` | `/api/v1/workspaces` | Cria um novo workspace (Solo ou Família). |
| `GET` | `/api/v1/workspaces/{id}/members` | Lista membros do workspace e seus papéis/rendas. |
| `POST` | `/api/v1/workspaces/{id}/members` | Convida um novo membro (ex: cônjuge/familiar). |
| `GET` | `/api/v1/workspaces/{id}/settlement` | Retorna o balanço de equalização mensal do casal. |

---

### 2.3. Módulo: Centros de Custo, Categorias e Tags (`/api/v1/cost-centers`, `/api/v1/categories`, `/api/v1/tags`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/cost-centers` | Lista centros de custo (Casa, Família, Casal, Pessoais). |
| `POST` | `/api/v1/cost-centers` | Cria centro de custo personalizado. |
| `GET` | `/api/v1/categories` | Lista árvore de categorias e subcategorias. |
| `POST` | `/api/v1/categories` | Cria nova categoria/subcategoria com ícone e cor. |
| `GET` | `/api/v1/tags` | Lista todas as tags ativas do workspace com contagem de uso. |
| `POST` | `/api/v1/tags` | Cria uma nova tag com nome e cor personalizada. |
| `DELETE`| `/api/v1/tags/{id}` | Remove uma tag do workspace. |

---

### 2.4. Módulo: Contas, Cartões e Faturas (`/api/v1/accounts`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/accounts` | Lista contas bancárias, carteiras e cartões de crédito. |
| `POST` | `/api/v1/accounts` | Cadastra nova conta ou cartão com limite e data de fechamento. |
| `GET` | `/api/v1/accounts/{id}/invoices` | Lista faturas do cartão (aberta, fechadas, futuras). |

---

### 2.5. Módulo: Transações Financeiras (`/api/v1/transactions`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/transactions` | Lista lançamentos com filtros avançados, tags, paginação e busca. |
| `POST` | `/api/v1/transactions` | Cria nova transação (suporta lançamentos únicos, parcelados e tags). |
| `GET` | `/api/v1/transactions/{id}` | Detalhes de uma transação específica com suas tags associadas. |
| `PUT` | `/api/v1/transactions/{id}` | Edita transação (ou todas as parcelas futuras da série). |
| `DELETE`| `/api/v1/transactions/{id}` | Remove transação. |

---

### 2.6. Módulo: Dívidas e Desalavancagem (`/api/v1/debts`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/debts` | Lista todas as dívidas ativas, taxas de juros e saldo devedor. |
| `POST` | `/api/v1/debts` | Cadastra novo passivo (empréstimo, financiamento, rotativo). |
| `POST` | `/api/v1/debts/{id}/amortize` | Registra pagamento ou amortização extraordinária. |
| `POST` | `/api/v1/debts/simulate` | Simula quitação por **Método Avalanche** vs. **Bola de Neve**. |

---

### 2.7. Módulo: Cofre da Reserva de Emergência (`/api/v1/emergency-fund`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/emergency-fund` | Retorna meta dinâmica, saldo atual e meses de cobertura essencial. |
| `POST` | `/api/v1/emergency-fund/deposits` | Registra aporte no cofre da reserva. |

---

### 2.8. Módulo: Radar de Desvios & Alertas (`/api/v1/radar`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/radar/limits` | Lista limites e tetos orçamentários parametrizados por categoria. |
| `POST` | `/api/v1/radar/limits` | Configura teto máximo mensal em R$ ou % da receita. |
| `GET` | `/api/v1/radar/alerts` | Retorna alertas ativos de gastos desconexos e ritmo de consumo. |
| `GET` | `/api/v1/radar/waste-report` | Relatório consolidado de itens marcados como `Desperdício`. |

---

### 2.9. Módulo: Relatórios por Tags / Projetos (`/api/v1/reports/tags`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/reports/tags` | Lista custos consolidados por tag (ex: totais de cada viagem/projeto). |
| `GET` | `/api/v1/reports/tags/{id}` | Extrato detalhado de todas as despesas daquela tag específica. |

---

## 3. Padrão de Paginação, Filtros e Tags

Todas as rotas de listagem suportam os seguintes parâmetros padrão via query string:

```
GET /api/v1/transactions?
  page=1
  &limit=25
  &start_date=2026-08-01
  &end_date=2026-08-31
  &cost_center_id=uuid-casa
  &essentiality=essential
  &member_id=uuid-anselmo
  &category_id=uuid-alimentacao
  &tags=viagem-gramado,reforma-cozinha
  &sort=-date,amount
  &search=supermercado
```
