# Módulos Funcionais e Especificação de Requisitos

Mapeamento dos módulos que compõem o sistema de gestão financeira familiar.

---

## 1. Módulo: Central de Lançamentos e Conciliação
- **Registro Rápido:** Formulário ágil para lançamentos avulsos com preenchimento das 4 dimensões (Membro, Centro de Custo, Essencialidade, Categoria).
- **Importação e Extratos:** Capacidade de importar faturas de cartão e extratos bancários (OFX / CSV) com auto-sugestão de categorização por histórico.
- **Gestão de Parcelamentos:** Controle automático de parcelas (ex: 3/10) com impacto nas faturas e fluxo futuro.

---

## 2. Módulo: Balanço do Casal e Centros de Custo
- **Dashboard Individual vs. Conjunto:**
  - Visão exclusiva de Anselmo (Rendimento, Gastos Pessoais, Cota-parte da Casa).
  - Visão exclusiva de Nathália (Rendimento, Gastos Pessoais, Cota-parte da Casa).
  - Visão Consolidada da Família.
- **Equalizador Automático:** Cálculo do acerto mensal entre o casal para equilibrar os pagamentos das despesas comuns da casa.

---

## 3. Módulo: Plano Tático de Eliminação de Dívidas (Sair do Vermelho)
- **Inventário Completo de Passivos:** Cadastro de credor, saldo devedor atual, taxa de juros real, Custo Efetivo Total (CET) e valor da parcela.
- **Estratégias de Amortização:**
  - **Método Avalanche (Mais econômico):** Foco prioritário na dívida com maior taxa de juros.
  - **Método Bola de Neve (Mais motivador):** Foco na menor dívida para rápida eliminação e liberação de fluxo de caixa.
- **Simulador de Antecipação:** Permite simular: *"Se eu colocar R$ 500 extras este mês nesta dívida, quantos meses e quantos reais de juros economizo?"*

---

## 4. Módulo: Cofre e Metas de Reserva de Emergência
- **Cálculo Dinâmico do Custo Essencial:** O sistema calcula a média mensal real de despesas classificadas como `🟢 Essencial` nos últimos 3 a 6 meses.
- **Termômetro da Reserva:**
  - Nível 1: Mini-reserva de segurança (R$ 2.000 a R$ 5.000) durante a fase de pagamento de dívidas.
  - Nível 2: 3 meses de custo essencial da casa.
  - Nível 3: 6 meses de custo essencial da casa.
- **Histórico de Rendimentos:** Acompanhamento do rendimento dos aportes (ex: 100% CDI / Tesouro Selic).

---

## 5. Módulo: Radar de Desvios e Parametrização de Gastos
- **Configuração de Tetos por Categoria:**
  - Definição de limites em R$ ou % da receita líquida (Ex: Restaurantes não podem passar de R$ 800/mês ou 8% da renda).
- **Semáforo de Gastos:**
  - 🟢 Verde: Até 75% do teto consumido.
  - 🟡 Amarelo: Entre 75% e 99% consumido.
  - 🔴 Vermelho: Teto estourado (Alerta de gasto desconexo).
- **Relatório de Desperdícios:** Sumário de tudo que foi marcado como `🔴 Desperdício` no mês para revisão em conjunto pelo casal.

---

## 6. Módulo: Projeção Futura e Cenários
- **Fluxo de Caixa Preditivo (12 Meses):** Gráfico de linha demonstrando a curva prevista de receitas, despesas fixas, parcelas a vencer e saldo remanescente mês a mês.
- **Simulador de Decisão:** *"Podemos fazer essa viagem no mês X?"* ou *"Podemos comprar este bem parcelado?"* — o sistema simula o impacto no orçamento dos meses seguintes e no tempo de conclusão da reserva de emergência.
