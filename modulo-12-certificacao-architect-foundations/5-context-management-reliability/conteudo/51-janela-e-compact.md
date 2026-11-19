# 5.1 — Janela de contexto e compactacao

## Objetivo
Nao encher a janela "porque cabe"; proteger fatos com CASE FACTS; trim de tool output; mitigar lost-in-the-middle.

## Analogia
Mochila de viagem: cabem 30kg, mas carregar 30kg todo dia cansa — e voce perde o passaporte no fundo.

## CASE FACTS
```text
CASE FACTS (do not summarize):
- Customer ID: #12345
- Order: #67890
- Total: $149.99
- Auto-refund limit: $100
```

Compact perde: valores exatos, IDs, stack traces, nuances.

Trim tool results para campos uteis.

## Mini-lab
Escreva CASE FACTS para um incidente de pagamento + liste 5 campos a remover do payload da tool.

## Checkpoint
- [ ] CASE FACTS
- [ ] Lost-in-the-middle: bookend / headers

← [ESTUDO](./ESTUDO.md) · → [5.2](./52-escalation-patterns.md)
