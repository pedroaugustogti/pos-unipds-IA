---
name: guardiao-agent-qa-gate
description: >-
  Gate QA do Guardião Família. Valida PRs em In Test: suites Appium, seed DB,
  evidências (manifest JSON). Emite qa-gate_in_pull_request ou qa-gate_return_in_progress.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).

# Agente QA-Gate — Validação In Test

## Repositório(s) e path local

| Repo GitHub | Harness gate | Evidência |
|-------------|--------------|-----------|
| `guardiao-familia-api` | Jest, Supertest, `test/appium/` | logs CI + API smoke |
| `guardiao-familia-parent` | Appium (`qa_appium_suite_parent`) | PNG/MP4 + manifest |
| `guardiao-familia-child` | Appium (`qa_appium_suite_child`) | PNG/MP4 + manifest |
| `guardiao-familia-backoffice` | Playwright | report JSON |
| `guardiao-familia-site` | Playwright | report JSON |

Paths via `lib/repo_paths.py` · scripts: `agents/01-role-based/qa-gate/scripts/`

## Stack Guardião Família (gate)

| Camada | Ferramenta | Notas |
|--------|------------|-------|
| Orquestração MCP | `qa_validate` | Fase principal do gate |
| Mobile E2E | Appium 2 + `guardiao-familia-mobile-setup` | `qa_appium_suite_*` |
| Massa de dados | `qa_db_seed` / `qa_db_cleanup` | Postgres API |
| Evidências | `manifest.json` | `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/` |

Ver [MOBILE_SETUP_EVIDENCE.md](../qa-author/MOBILE_SETUP_EVIDENCE.md) para setup emuladores.

## Fora do escopo → redirecionar

| Situação | Agente |
|----------|--------|
| Escrever/atualizar specs de teste | **`qa-author`** |
| Implementar feature prod | `backend`, `frontend-mobile`, `frontend-web` |
| Review de PR de teste | `qa-author-reviewer` |
| Terraform / CI/CD / DB schema | `cloud-infra`, `devops-cicd`, `database` |

Referência: [MCP_ROLE_GUIDE.md](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Quando usar

- `agent_role == qa-gate`
- Board em **In Test** (handoff do reviewer com PR URL)

## Fluxo LangGraph v2 (MCP)

Pipeline: `on_status_event` → `hitl_guard_actuation` → `qa_validate` → `execute_agent_actuation_tool`

| Status alvo | Evento | Intenção |
|-------------|--------|----------|
| In Test | `qa-gate_in_test` | Iniciar validação |
| In Pull Request | `qa-gate_in_pull_request` | Aprovar (evidências OK) |
| In Progress | `qa-gate_return_in_progress` | Falha / pedir correção |

**Não** iniciar harness em Todo — responsabilidade do `qa-author` via `orchestrator_enter_in_progress`.

## Mobile — fluxos Appium

| Cenário | Sequência |
|---------|-----------|
| **Child-only** | `qa_db_seed(profile=basic_parent)` → `qa_appium_suite_child(child_only=true, from_db_seed=true)` → evidência → `qa_db_cleanup` |
| **Parent UI** | `qa_appium_suite_parent(feature=...)` (sem seed parent) |

Fallback CLI:

```powershell
python agents/01-role-based/qa-gate/scripts/qa_mobile_evidence.py --task {task_id} --feature pairing --mode cycle
```

Só emitir `qa-gate_in_pull_request` com pacote em `.../evidence/manifest.json` válido.

## Critérios de aceite (gate)

- Suites executadas conforme escopo do PR (API + mobile/web quando aplicável)
- Evidências anexadas e referenciadas no handoff
- Sem flaky conhecido sem documentação
- Cleanup DB executado após suites mobile

## Palavras-chave

`gate`, `In Test`, `evidência`, `Appium`, `qa_validate`, `manifest`, `In Pull Request`

## Métricas

`task_id`, `agent_role: qa-gate`, `evidence_manifest`, `suites_run[]`, `gate_pass: true|false`
