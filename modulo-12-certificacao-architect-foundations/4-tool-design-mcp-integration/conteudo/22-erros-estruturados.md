# 2.2 — Erros estruturados de tools

## Objetivo
Nunca esconder falha como `[]` de sucesso; classificar transient / validation / business / permission.

## Analogia
Medico: "exame nao realizado (lab fechado)" ≠ "exame normal sem achados".

## Payload
```json
{
  "is_error": true,
  "errorCategory": "transient",
  "isRetryable": true,
  "description": "Timeout 30s lookup order #67890",
  "partial_results": null,
  "attempted_action": "GET /orders/67890"
}
```

| Categoria | Retry? | Acao |
|-----------|--------|------|
| Transient | Sim | Backoff |
| Validation | Com input novo | Corrigir args |
| Business | Nao | Explicar / HITL |
| Permission | Nao | Escalate |

Empty 200 ≠ outage 503.

## Mini-lab
Escreva 4 respostas de tool (uma por categoria) para `process_refund`.

## Checkpoint
- [ ] Distingo empty vs fail
- [ ] Erro com contexto acionavel

← [2.1](./21-tool-interface.md) · [ESTUDO](./ESTUDO.md) · → [2.3](./23-distribuicao-tool-choice.md)
