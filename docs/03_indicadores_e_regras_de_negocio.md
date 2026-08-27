# Indicadores, Métricas e Regras de Negócio

Para garantir que o sistema atue como um **consultor financeiro proativo** e não apenas como um diário de contas, definimos os indicadores analíticos e as regras de detecção de desvios.

---

## 1. Indicadores Chave de Saúde Financeira (KPIs)

| Indicador | Fórmula de Cálculo | Faixa Ideal | Faixa de Alerta | Faixa Crítica |
| :--- | :--- | :--- | :--- | :--- |
| **Índice de Comprometimento com Dívidas (DTI)** | `(Parcelas de Dívidas / Renda Líquida Total) * 100` | `< 10%` | `10% a 30%` | `> 30%` |
| **Taxa de Desperdício (Waste Ratio)** | `(Gastos Marcados como Desperdício / Renda Líquida) * 100` | `0%` | `1% a 3%` | `> 3%` |
| **Índice de Essencialidade** | `(Gastos Essenciais / Renda Líquida Total) * 100` | `45% a 55%` | `55% a 70%` | `> 70%` |
| **Índice de Estilo de Vida / Lazer** | `(Gastos Estilo de Vida / Renda Líquida Total) * 100` | `15% a 25%` | `25% a 35%` | `> 35% (Desconexo)` |
| **Taxa de Poupança & Aporte** | `(Aportes em Reserva + Amortizações Extras / Renda) * 100` | `> 20%` | `10% a 20%` | `< 10% ou Negativa` |
| **Cobertura da Reserva de Emergência** | `Saldo da Reserva / Gasto Mensal Essencial Total` | `6 a 12 meses` | `3 a 6 meses` | `< 3 meses` |

---

## 2. Motor de Detecção de "Gastos Desconexos da Realidade"

O sistema implementa alertas automáticos baseados em **tetos parametrizáveis** (por valor fixo ou por percentual da renda familiar).

### Exemplos de Regras de Detecção:

1. **Alerta de Desproporção Alimentar (Restaurantes vs. Casa):**
   - *Gatilho:* Se `(Restaurantes + Delivery) > 40% do Total Gasto em Alimentação` ou ultrapassar o teto estipulado de R$ X.
   - *Ação do Sistema:* Disparar notificação: *"Atenção: Os gastos com refeições fora/delivery já somam R$ Y e representam Z% do orçamento alimentar deste mês."*
2. **Alerta de Assinaturas e Recorrências Ociosas:**
   - *Gatilho:* Identificação de pagamentos recorrentes não essenciais repetidos há mais de 3 meses sem benefício registrado.
3. **Alerta de Ritmo de Gastos (Burn Rate Semanal):**
   - *Gatilho:* Se na 2ª semana do mês já tiver sido consumido mais de 60% do orçamento de despesas variáveis.
4. **Alerta de Compra com Juros Ocultos:**
   - *Gatilho:* Qualquer lançamento contendo encargos de rotativo, cheque especial ou parcelamento com taxa de juros maior que 0%.

---

## 3. Divisão de Contas e Balanço do Casal

Para manter a saúde e transparência no relacionamento financeiro:

### Modelo de Rateio Proporcional às Receitas:
1. **Receita Líquida Anselmo:** \( R_A \)
2. **Receita Líquida Nathália:** \( R_N \)
3. **Receita Familiar Total:** \( R_T = R_A + R_N \)
4. **Percentual Anselmo:** \( P_A = \frac{R_A}{R_T} \)
5. **Percentual Nathália:** \( P_N = \frac{R_N}{R_T} \)

### Regra de Equalização Mensal:
- Todas as despesas com Centro de Custo **🏠 Casa** e **👨‍👩‍👧 Família** são somadas no fechamento mensal (\( D_{comum} \)).
- O valor devido por Anselmo é \( P_A \times D_{comum} \).
- O valor devido por Nathália é \( P_N \times D_{comum} \).
- O sistema calcula quem pagou mais despesas comuns em seus cartões/contas e exibe o saldo de acerto sem necessidade de contas manuais.
- Despesas com Centro de Custo **👤 Individual** pertencem 100% ao respectivo membro.

---

## 4. Projeções Futuras e Fluxo de Caixa Preditivo

O sistema projetará os próximos 12 meses considerando:
1. **Compromissos Recorrentes Fixos:** Aluguel, contas de consumo médias, mensalidades.
2. **Faturas de Cartão Futuras:** Parcelas já contratadas a vencer nos meses M+1, M+2, etc.
3. **Cronograma de Dívidas:** Projeção da data exata de quitação de cada passivo sob amortização normal vs. amortização acelerada.
4. **Acúmulo da Reserva:** Previsão de quando a reserva atingirá a meta de 3 meses e 6 meses de segurança.
