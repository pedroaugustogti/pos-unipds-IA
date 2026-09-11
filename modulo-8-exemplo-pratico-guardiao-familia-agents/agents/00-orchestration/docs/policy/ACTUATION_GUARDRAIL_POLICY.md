# Actuation Guardrail Policy (HITL)

Versão: 2.0  
Escopo: `emit_status_event` e `hitl_guard_actuation` / `execute_agent_actuation_tool`.

## Objetivo

**HITL somente quando o texto do contexto viola policy** (prompt injection, ação destrutiva, segredos, escopo).
Metadados da task (`high_risk`, `release_blocker`, tipo de evento, bug count) **não** disparam HITL.

## Regras de bloqueio (severity: critical)

1. **Prompt injection / jailbreak**
2. **Contorno de HITL** — pular `hitl_guard_actuation`, merge sem humano
3. **Segredos em contexto** — tokens, chaves AWS, JWT
4. **Ações destrutivas** — `terraform destroy`, `delete terraform`, `drop database`, `truncate`, DELETE em massa
5. **Privilégios** — remover/revogar admin, permissões, roles; desabilitar MFA; elevar para superuser

## Regras de alerta (severity: high → bloqueio)

1. Pular testes / evidência QA
2. Merge sem review
3. Editar `do_not_touch` / ignorar `out_of_scope`

## Resolução humana

1. Triagem no board (comentário automático em bloqueio)
2. `hitl_guard_actuation(human_clearance=true, clearance_note=...)`
3. `execute_agent_actuation_tool` com `guard_pass_id`

Implementação: `lib/gateway/policy_violations.py` · `lib/gateway/hitl_gates.py`
