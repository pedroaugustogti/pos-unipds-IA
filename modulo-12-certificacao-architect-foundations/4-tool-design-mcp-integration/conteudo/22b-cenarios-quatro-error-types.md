# 2.2 (extra) — Transient, Validation, Business, Permission

> Cruza com [22-erros-estruturados.md](./22-erros-estruturados.md).

Empty 200 ≠ outage 503. Nunca mapear falha → `hits=[]` → “no results”.

## Payload padrão

```json
{
  "is_error": true,
  "errorCategory": "transient|validation|business|permission",
  "isRetryable": true,
  "description": "acionável",
  "attempted_action": "lookup_order"
}
```

---

## 1) Transient

`lookup_order` timeout/503.

| Motivo classificar | Solução |
|--------------------|---------|
| Infra; pedido pode existir | Retry backoff; se persistir avisar/HITL — **não** “pedido inexistente” |

## 2) Validation

`order_id: "88210-ABC"` formato inválido.

| Motivo | Solução |
|--------|---------|
| Input malformado | Corrigir args / perguntar user; retry **só com input novo** |

## 3) Business

Return window 45 dias; entregue há 60.

| Motivo | Solução |
|--------|---------|
| Regra de negócio | Explicar policy / HITL exception — **não** retry cego |

## 4) Permission

Agent sem scope `refunds:write`.

| Motivo | Solução |
|--------|---------|
| AuthZ | Escalate/HITL — **não** retry |

### Como configurar scope

Não é `settings.json` allow/deny do Code.

```text
roles.yaml / JWT scopes
  → PreToolUse compara required_scope(tool) ⊆ granted(agent)
  → ou API 403 mapeado para errorCategory=permission
```

Claude Code `permissions` = Bash/Edit etc.  
Scope de negócio = RBAC do host/API.

---

## Cenário clássico: Search falhou → “no results”

503 virando `hits=[]` → user acha que não há policy.

**Fix:** `is_error` + category + retryable; prompt: falha ≠ vazio.

---

## Checkpoint

- [ ] 4 categorias + retry policy
- [ ] Permission scope ≠ settings allow

← [2.2](./22-erros-estruturados.md) · [ESTUDO](./ESTUDO.md)
