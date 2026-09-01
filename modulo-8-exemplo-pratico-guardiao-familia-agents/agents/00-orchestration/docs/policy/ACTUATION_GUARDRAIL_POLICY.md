# Actuation Guardrail Policy (HITL)

Versão: 1.0  
Escopo: validação obrigatória **antes** de `execute_agent_actuation_tool`.

## Objetivo

Interromper o fluxo de eventos quando o contexto de atuação (ticket, handoff, playbook, histórico)
sugerir risco de **prompt injection**, **comportamento crítico** ou **ação irreversível** sem supervisão humana.

## Regras de bloqueio (severity: critical)

1. **Prompt injection / jailbreak** — instruções que tentem anular políticas do sistema:
   - "ignore previous instructions", "disregard policy", "you are now", "act as DAN"
   - Pedidos para ocultar ações do board, omitir evidências ou falsificar resultados de QA
2. **Contorno de HITL** — texto que ordene pular `hitl_guard_actuation`, `approve_hitl`, merge sem humano
3. **Segredos em contexto** — tokens API, chaves AWS, senhas, JWT longos colados no ticket/handoff
4. **Ações destrutivas em produção** — `terraform destroy`, `drop database`, `force push main`, deploy prod sem gate
5. **Merge / release irreversível** — fase `In Pull Request` em modo `live` sem clearance humano explícito

## Regras de alerta (severity: high → bloqueio se ≥2)

1. **Pular testes** — "skip tests", "sem evidência Appium", `skip_tests` em task de alto risco
2. **Escopo violado** — instruções para editar paths em `do_not_touch` ou fora de `in_scope`
3. **Alto risco operacional** — pagamentos, LGPD, auth, stores, infra prod (ver `hitl_gates.HIGH_RISK_*`)
4. **release_blocker** — card marcado como bloqueador de release em eventos de aprovação/merge
5. **Contradição de papel** — contexto pede ação de outro `agent_role` sem handoff válido

## Importância do contexto (scoring)

| Sinal | Peso |
|-------|------|
| Finding critical | +100 (bloqueio imediato) |
| Finding high | +40 |
| Finding medium | +15 |
| Task high_risk | +20 |
| release_blocker | +30 |
| Fase merge + live | +50 |

`importance_score ≥ 100` → **blocked**  
`importance_score ≥ 60` sem critical → **blocked**  
Caso contrário → **proceed** (emite `guard_pass_id` de uso único)

## Resolução humana

1. Humano tria no board (comentário automático da tool)
2. Chama `hitl_guard_actuation` com `human_clearance=true` e `clearance_note`
3. Recebe novo `guard_pass_id` e só então `execute_agent_actuation_tool`

## Notificação no board

Em bloqueio, comentar na issue com: task_id, evento, findings, `importance_score`, ação esperada do humano.
