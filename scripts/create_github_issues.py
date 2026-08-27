import subprocess

issues = [
    # v0.1 - Fundação
    {
        "title": "[Core] Setup do Monorepo, Docker Compose, FastAPI e Next.js",
        "milestone": "v0.1 - Fundação e Core Multi-Tenant",
        "labels": "epic,backend,frontend",
        "body": """### Descrição
Configuração da infraestrutura base do monorepo KIVO com Docker Compose.

### Requisitos Técnicos
- Configurar `docker-compose.yml` com serviços: `postgres:16-alpine`, `redis:7-alpine`, `api` (FastAPI) e `web` (Next.js 15).
- Setup do FastAPI com Pydantic V2 e CORS configurado.
- Setup do Next.js com Tailwind CSS v4, TypeScript e Shadcn UI.

### Critérios de Aceitação
- [ ] `docker compose up` sobe todos os 4 containers saudáveis.
- [ ] Rota `/api/v1/health` responde status 200 com conexão válida ao Postgres e Redis."""
    },
    {
        "title": "[Auth] Sistema de Autenticação JWT com 2FA (RFC 6238 TOTP) e Backup Codes",
        "milestone": "v0.1 - Fundação e Core Multi-Tenant",
        "labels": "security,backend,frontend",
        "body": """### Descrição
Implementação do fluxo de autenticação seguro em 2 etapas com suporte a Google Authenticator.

### Requisitos Técnicos
- Hash de senhas com Argon2id.
- Geração de segredo TOTP (RFC 6238) e QR Code em base64.
- Geração de 8 códigos de backup alfanuméricos hasheados no banco.
- Fluxo de login em 2 etapas (desafio efêmero de 5 min $\\rightarrow$ validação de 6 dígitos $\\rightarrow$ JWT + Refresh Token em cookie HttpOnly).

### Critérios de Aceitação
- [ ] Usuário consegue registrar conta e ativar 2FA escaneando QR Code no celular.
- [ ] Login exige código TOTP quando 2FA estiver ativado.
- [ ] Códigos de backup permitem login de emergência de uso único."""
    },
    {
        "title": "[Database] Migrações Iniciais PostgreSQL (Esquema Multi-Tenant, RLS e Enums)",
        "milestone": "v0.1 - Fundação e Core Multi-Tenant",
        "labels": "backend,security",
        "body": """### Descrição
Criação do esquema relacional completo no PostgreSQL com suporte a multi-tenancy e RLS.

### Requisitos Técnicos
- Configuração do SQLAlchemy 2.0 Async e Alembic.
- Criação das tabelas e enums conforme documento `docs/10_modelo_de_banco_de_dados_sql.md`.
- Uso estrito de `NUMERIC(15, 2)` para valores monetários e `UUIDv7` para chaves primárias.

### Critérios de Aceitação
- [ ] `alembic upgrade head` roda sem erros gerando todas as tabelas.
- [ ] Índices compostos criados para performance de consultas."""
    },
    {
        "title": "[Workspace] Gestão de Workspaces (Modo Solo e Modo Família) e Convite de Membros",
        "milestone": "v0.1 - Fundação e Core Multi-Tenant",
        "labels": "backend,frontend",
        "body": """### Descrição
Módulo de alternância e gestão de workspaces e membros.

### Requisitos Técnicos
- CRUD de Workspaces (Solo / Família).
- Convite de membros por e-mail e atribuição de papéis (Owner, Member, Viewer).
- Cadastro de renda mensal declarada de cada membro para cálculos de rateio.

### Critérios de Aceitação
- [ ] Usuário pode alternar facilmente entre o Modo Solo e o Modo Família na interface.
- [ ] Dados financeiros ficam 100% isolados entre workspaces distintos."""
    },

    # v0.2 - MVP Fluxo de Caixa
    {
        "title": "[Contas] Cadastro de Contas Bancárias, Carteiras e Cartões de Crédito com Faturas",
        "milestone": "v0.2 - Gestão de Contas e Lançamentos 4D (MVP)",
        "labels": "backend,frontend",
        "body": """### Descrição
Gerenciamento de contas correntes, investimentos, carteiras físicas e cartões de crédito.

### Requisitos Técnicos
- Cadastro de cartões com limite, data de fechamento e data de vencimento.
- Agrupamento automático de lançamentos em faturas mensais (abertas, fechadas e futuras).

### Critérios de Aceitação
- [ ] Saldo bancário atualizado automaticamente a cada lançamento de despesa/receita.
- [ ] Despesas no cartão são alocadas na fatura correta de acordo com a data de fechamento."""
    },
    {
        "title": "[Categorização] Estrutura de Centros de Custo e Árvore de Categorias",
        "milestone": "v0.2 - Gestão de Contas e Lançamentos 4D (MVP)",
        "labels": "backend,frontend",
        "body": """### Descrição
Configuração da taxonomia financeira do usuário.

### Requisitos Técnicos
- Centros de Custo padrões: Casa, Família, Casal, Pessoal Anselmo, Pessoal Nathália.
- Árvore hierárquica de Categorias e Subcategorias com ícone Lucide e cor hexadecimal.

### Critérios de Aceitação
- [ ] Usuário pode criar categorias e subcategorias personalizadas.
- [ ] Associação padrão de essencialidade recomendada por categoria."""
    },
    {
        "title": "[Transações] CRUD de Lançamentos com Suporte a Parcelamento e Taxonomia 4D",
        "milestone": "v0.2 - Gestão de Contas e Lançamentos 4D (MVP)",
        "labels": "epic,backend,frontend",
        "body": """### Descrição
Mecanismo central de registro de transações financeiras.

### Requisitos Técnicos
- Formulário de lançamento com classificação nas 4 dimensões (Dono, Centro de Custo, Essencialidade, Categoria).
- Suporte a despesas parceladas (ex: 1/10 a 10/10) gerando parcelas futuras vinculadas por `series_id`.
- Filtros avançados na listagem de extrato (por mês, dono, centro de custo, essencialidade e busca textual).

### Critérios de Aceitação
- [ ] Criar compra parcelada gera corretamente os registros para os meses subsequentes.
- [ ] Edição em lote de parcelas futuras disponível."""
    },
    {
        "title": "[Equalização] Módulo de Rateio Proporcional de Despesas do Casal e Acerto de Contas",
        "milestone": "v0.2 - Gestão de Contas e Lançamentos 4D (MVP)",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Algoritmo de divisão justa de despesas compartilhadas com base na renda proporcional de cada parceiro.

### Requisitos Técnicos
- Cálculo automático da proporção: $\\text{Fatia}_A = \\frac{R_A}{R_A + R_B} \\times 100$.
- Extrato de acerto de contas (*settlement*): quem pagou mais que a sua cota e quanto deve ser reembolsado.
- Botão "Quitar Acerto do Mês" gerando a transação de transferência de compensação.

### Critérios de Aceitação
- [ ] Relatório mensal exibe com clareza o saldo de equalização do casal."""
    },

    # v0.3 - Sair do Vermelho
    {
        "title": "[Dívidas] Cadastro de Passivos, Taxas de Juros e Amortização Extraordinária",
        "milestone": "v0.3 - Módulo Sair do Vermelho e Diagnóstico",
        "labels": "backend,frontend",
        "body": """### Descrição
Painel de controle de dívidas e financiamentos.

### Requisitos Técnicos
- Cadastro de dívida com saldo devedor, taxa de juros ao mês (% a.m.), valor da parcela e quantidade restante.
- Registro de amortizações extraordinárias abatendo diretamente do saldo devedor.

### Critérios de Aceitação
- [ ] Visualização do total consolidado de dívidas e custo financeiro mensal em juros."""
    },
    {
        "title": "[Simulador] Motor de Quitação Inteligente: Método Avalanche vs. Bola de Neve",
        "milestone": "v0.3 - Módulo Sair do Vermelho e Diagnóstico",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Algoritmo matemático de estratégia de eliminação acelerada de dívidas.

### Requisitos Técnicos
- Comparativo entre Método Avalanche (maior taxa de juros primeiro) e Bola de Neve (menor saldo devedor primeiro).
- Cálculo exato de quantos meses e quantos reais de juros o usuário economiza aplicando um aporte extra mensal.

### Critérios de Aceitação
- [ ] Gráfico comparativo de tempo e juros pagos entre as duas estratégias."""
    },
    {
        "title": "[Diagnóstico] Cálculo Automatizado do DTI (Debt-to-Income) e Termômetro de Endividamento",
        "milestone": "v0.3 - Módulo Sair do Vermelho e Diagnóstico",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Cálculo do indicador de comprometimento de renda com dívidas.

### Requisitos Técnicos
- $\\text{DTI} = \\frac{\\sum \\text{Parcelas de Dívidas}}{\\text{Renda Líquida Total}} \\times 100$.
- Semáforo de saúde: Verde ($<30\\%$), Amarelo ($30-50\\%$) e Vermelho ($>50\\%$).

### Critérios de Aceitação
- [ ] Termômetro exibido no topo do dashboard com diagnóstico e recomendações táticas."""
    },

    # v0.4 - Radar e Reserva
    {
        "title": "[Radar] Parametrização de Tetos Orçamentários e Semáforo de Ritmo de Consumo",
        "milestone": "v0.4 - Radar de Gastos e Reserva de Emergência",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Sistema de alertas preditivos para evitar estouro de orçamento durante o mês.

### Requisitos Técnicos
- Configuração de tetos máximos por categoria em R$ ou % da renda.
- Cálculo do ritmo de consumo proporcional ao dia do mês (alerta se $70\\%$ do teto foi gasto no dia 10).

### Critérios de Aceitação
- [ ] Cartões de categoria exibem barra de progresso colorida (Verde, Amarelo em 75%, Vermelho em 100%+)."""
    },
    {
        "title": "[Desperdício] Tag de Classificação de Gastos Desconexos e Relatório de Ralos",
        "milestone": "v0.4 - Radar de Gastos e Reserva de Emergência",
        "labels": "backend,frontend",
        "body": """### Descrição
Módulo de identificação e corte de gastos supérfluos e desperdícios.

### Requisitos Técnicos
- Tag `Desperdício` com preenchimento opcional do campo "Motivo do Desperdício" (ex: comida que estragou, assinatura esquecida).
- Relatório mensal somando o valor total desperdiçado e quanto isso renderia na reserva de emergência.

### Critérios de Aceitação
- [ ] Relatório visual com ranking dos maiores ralos financeiros do mês."""
    },
    {
        "title": "[Reserva] Cofre da Reserva de Emergência com Meta Dinâmica de Custos Essenciais",
        "milestone": "v0.4 - Radar de Gastos e Reserva de Emergência",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Cofre financeiro com recálculo dinâmico baseado na média real de custos essenciais.

### Requisitos Técnicos
- $\\text{Meta Reserva} = \\text{Meses Desejados (ex: 6)} \\times \\text{Média Gastos Essenciais últimos 6 meses}$.
- Termômetro visual de progresso e simulação de data estimada para conclusão da meta.

### Critérios de Aceitação
- [ ] Aporte na reserva registra transação especial que não impacta como despesa de consumo."""
    },

    # v0.5 - Projeções e Importação
    {
        "title": "[Projeções] Projeção de Fluxo de Caixa para 12 Meses e Simulador de Cenários",
        "milestone": "v0.5 - Projeções e Importação de Dados",
        "labels": "finance-engine,backend,frontend",
        "body": """### Descrição
Visualização preditiva da saúde financeira nos próximos 12 meses.

### Requisitos Técnicos
- Projeção de receitas recorrentes, despesas fixas e parcelas futuras já contratadas.
- Ferramenta "Posso Comprar?": simula o impacto de uma nova compra no saldo futuro.

### Critérios de Aceitação
- [ ] Gráfico de linha interativo exibindo a curva de saldo projetada mês a mês."""
    },
    {
        "title": "[Importação] Parser de Faturas e Extratos (OFX e CSV) com Sugestão Automática",
        "milestone": "v0.5 - Projeções e Importação de Dados",
        "labels": "backend,frontend",
        "body": """### Descrição
Leitor de extratos e faturas para cadastro ágil em lote.

### Requisitos Técnicos
- Upload e parse de arquivos `.ofx` e `.csv` dos principais bancos brasileiros (Nubank, Itaú, Inter, Bradesco, C6).
- Detecção inteligente de transações duplicadas e auto-sugestão de categoria por histórico de descrições.

### Critérios de Aceitação
- [ ] Tela de conciliação permitindo revisar e confirmar os lançamentos antes de salvar no banco de dados."""
    }
]

for item in issues:
    cmd = [
        "gh", "issue", "create",
        "--repo", "anselmo-nonato/kivo",
        "--title", item["title"],
        "--body", item["body"],
        "--milestone", item["milestone"],
        "--label", item["labels"]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Criada: {item['title']} -> {res.stdout.strip()}")

print("Todas as 16 Issues foram criadas no repositório GitHub com sucesso!")
