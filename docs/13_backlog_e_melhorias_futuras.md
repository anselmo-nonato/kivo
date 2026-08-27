# KIVO — Backlog de Ideias e Melhorias Futuras 💡

Este documento centraliza as discussões de produto, RFCs (Request for Comments) e ideias aprovadas para análise e implementação em versões posteriores ao MVP (v1.x em diante).

---

## 📌 1. Automação Avançada de Faturas e Crédito Rotativo
* **GitHub Issue:** [#26](https://github.com/anselmo-nonato/kivo/issues/26)
* **Status:** Registrado para análise futura.
* **Decisão Pragmática do MVP:**
  * O sistema permite registrar pagamentos totais ou parciais de faturas.
  * O saldo não pago permanece em aberto com badge visual de alerta de atraso após o vencimento.
  * Os juros, multas e IOF cobrados pela operadora do cartão entram na fatura seguinte via importação de OFX/extrato ou lançamento manual, classificados na categoria `debt` (Essencialidade: Dívidas/Juros).
* **Melhorias Futuras Planejadas:**
  1. **Conversão Opcional em Passivo:** Botão de 1 clique para transformar o saldo não pago da fatura em uma dívida rastreável no simulador Avalanche.
  2. **Simulador de Parcelamento de Fatura:** Comparador de custo entre pagar o mínimo (rotativo) vs parcelar a fatura em até 24x vs empréstimo consignado/pessoal.
  3. **Alerta Preditivo:** Notificação de aproximação de vencimento com projeção de juros caso o pagamento não seja efetuado.

---

## 📌 2. Open Finance Brasil (Sincronização Bancária Automática)
* **Ideia:** Integração direta com APIs bancárias autorizadas pelo Banco Central via Open Finance (Pluggy / Belvo) para sincronização de saldo e transações sem necessidade de exportar OFX/CSV manualmente.

---

## 📌 3. Relatórios Exportáveis em PDF / Excel Executivo
* **Ideia:** Geração de relatórios mensais e anuais formatados para prestação de contas, declaração de imposto de renda e reuniões de alinhamento financeiro do casal/família.
