---
name: guardiao-agent-qa
description: >-
  Agente QA do Guardião Família. Testes unitários, integração, E2E (Detox/Maestro),
  push SOS, geofence E2E. Tasks com teste/e2e/spec no título ou label qa.
---

# Agente QA — Testes & Qualidade

## Quando usar

- `agent_role == qa`
- Título contém: teste, test, e2e, spec, qa, coverage
- Secondary em tasks produto que exigem validação E2E

## Stack de testes

| Camada | Ferramenta | Repo |
|--------|------------|------|
| API unit/integration | Jest, Supertest | api |
| Mobile E2E | Detox ou Maestro | parent, child |
| Web | Playwright/Cypress | backoffice, site |
| Push/SOS E2E | device farm ou simulador + mock FCM | parent |

## Workflow board → PR

1. Claim task de teste; In Progress.
2. Branch `test/T-XXX-NNN-<slug>`.
3. Adicionar/atualizar specs; não alterar lógica prod sem necessidade.
4. PR: cenários cobertos, gaps, flaky risks, como rodar localmente.
5. Se bug encontrado: issue separada + link no PR.

## Critérios de aceite

- Testes reproduzíveis em CI
- Cenários críticos: SOS <30s, geofence entry/exit, push som emergência
- Screenshots/logs anexados em tasks E2E mobile quando útil
- Coverage não regredir no módulo afetado

## Palavras-chave

`teste`, `test`, `e2e`, `spec`, `QA`, `coverage`, `Detox`, `Maestro`, `push SOS`

## Coordenação

- Implementação faltante → devolver para agent dev primário com comentário
- Release blocker tests → prioridade máxima no claim

## Métricas PR

`task_id`, `agent_role: qa`, `test_files[]`, `scenarios_count`, `ci_job`.
