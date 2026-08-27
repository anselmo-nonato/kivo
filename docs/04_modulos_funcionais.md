# Módulos Funcionais e Regras de Negócio — KIVO

**Status:** Aprovado  
**Escopo:** Funcionalidades do Sistema (Frontend e Backend)  

---

## 1. Módulo: Autenticação, Usuários e Workspaces
* **Cadastro e Login:** Suporte a e-mail, senha com Argon2id e 2FA via Google Authenticator (TOTP RFC 6238).
* **Modo Solo vs. Modo Família:** Alternância instantânea de Workspace no topo da aplicação.
* **Gestão de Membros:** Convite de parceiros(as) e familiares com definição de renda mensal declarada.

---

## 2. Módulo: Contas Bancárias, Carteiras e Cartões
* **Contas Correntes e Investimentos:** Saldo em tempo real com conciliação.
* **Cartões de Crédito:** Controle de limites, datas de fechamento e faturas (aberta, fechada, futuras).

---

## 3. Módulo: Lançamentos, Parcelamentos e Tags
* **Lançamento Rápido:** Entrada de dados com classificação em 4 dimensões (Dono, Centro de Custo, Essencialidade, Categoria).
* **Compras Parceladas:** Criação automática de parcelas futuras vinculadas (`1/12`, `2/12`...).
* **🏷️ Sistema de Tags / Projetos:**
  * Inclusão rápida de tags pelo símbolo `#` no campo de descrição ou seletor múltiplo.
  * Filtro por uma ou mais tags na listagem de extrato.
  * Painel de Projetos/Eventos: consolidação de custos totais por tag (ex: custo total da `#ViagemGramado`).

---

## 4. Módulo: Equalização e Rateio Justo do Casal
* **Divisão Proporcional:** Cálculo da participação justa baseada na renda líquida declarada ($R_A / (R_A + R_B)$).
* **Extrato de Acerto de Contas:** Cálculo em tempo real de quem pagou mais despesas da Casa/Casal e quanto deve receber de reembolso.

---

## 5. Módulo: Sair do Vermelho (Desalavancagem)
* **Cadastro de Dívidas:** Saldo devedor, taxa de juros a.m. e parcelas restantes.
* **Simulador de Quitação:** Comparador entre Método Avalanche (maior juro primeiro) e Bola de Neve (menor saldo primeiro).
* **Termômetro DTI:** Indicador visual de comprometimento de renda com dívidas.

---

## 6. Módulo: Radar de Gastos e Ralos Financeiros
* **Tetos por Categoria:** Limites orçamentários com semáforo de ritmo de consumo.
* **Detector de Desperdício:** Relatório exclusivo de gastos supérfluos e impacto financeiro anual.

---

## 7. Módulo: Cofre da Reserva de Emergência
* **Meta Dinâmica:** Recalculada com base na média real dos gastos essenciais dos últimos 6 meses.
* **Termômetro da Reserva:** Cobertura em meses e progresso percentual.

---

## 8. Módulo: Projeção de Fluxo de Caixa
* **Visão 12 Meses:** Projeção preditiva do saldo futuro considerando receitas, despesas fixas e parcelas.
* **Simulador "Posso Comprar?":** Avaliação de impacto de novas compras no orçamento futuro.
