---
name: guardiao-agent-qa
description: >-
  Agente QA Author do Guardião Família. Testes unitários, integração, E2E Appium/Playwright,
  push SOS, geofence E2E. Gera casos de teste e evidências (report JSON, screenshots).
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Agente QA Author — Testes & Qualidade

## Repositório(s) e path local

| Repo GitHub | Path local | Env var | Harness |
|-------------|------------|---------|---------|
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` | Jest, Supertest, `test/appium/` |
| `guardiao-familia-parent` | `...\guardiao-familia-parent` | `GUARDAO_PARENT_PATH` | specs mobile |
| `guardiao-familia-child` | `...\guardiao-familia-child` | `GUARDAO_CHILD_PATH` | specs mobile |
| `guardiao-familia-backoffice` | `...\guardiao-familia-backoffice` | `GUARDAO_BACKOFFICE_PATH` | Playwright |
| `guardiao-familia-site` | `...\guardiao-familia-site` | `GUARDAO_SITE_PATH` | Playwright |

Paths via `lib/repo_paths.py`. **Não usar Detox/Maestro** — padronizado Appium em **mobile-setup**.

## Evidências mobile (frontend-mobile) — obrigatório

Skill dedicada: **[MOBILE_SETUP_EVIDENCE.md](MOBILE_SETUP_EVIDENCE.md)**

```powershell
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-XXX --feature pairing --mode cycle
```

Engine: `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-mobile-setup` (`GUARDAO_MOBILE_SETUP_PATH`).

## Stack Guardião Família

| Camada | Ferramenta | Repo / path |
|--------|------------|-------------|
| API unit/integration | Jest, Supertest | `guardiao-familia-api` |
| Mobile E2E Android | Appium 2 + fast-stack | **`guardiao-familia-mobile-setup`** (`appium/`, `scripts/fast-stack.ps1`) |
| Evidências PNG/MP4 mobile | `qa_mobile_evidence.py` | Ver [MOBILE_SETUP_EVIDENCE.md](MOBILE_SETUP_EVIDENCE.md) |
| API pairing smoke | `task36-pairing-v2.e2e.mjs` | api (smoke rápido, não substitui UI) |
| Web | Playwright | backoffice, site |
| Push/SOS E2E | emulador + mock FCM | parent |

Bibliotecas orquestrador: `lib/mobile/qa_mobile_mcp.py`, `lib/mobile/mobile_task.py`, `lib/mobile/qa_mobile_setup_evidence.py`, `lib/mobile/local_e2e.py`, `lib/mobile/mobile_flow_discovery.py`

### Discovery mobile (seed fluxos 0→N)

```powershell
python agents/qa-gate/scripts/qa_discover_mobile_flows.py --app both
```

Registra telas, labels e fluxos em `data/mobile_user_flows.db`. Tickets mobile consomem este banco para sec. 2.1.

**RAG (Postgres pgvector):** após discovery, rodar `python agents/qa-gate/scripts/ingest_mobile_flows_rag.py` — agentes consultam via MCP `query_mobile_flow_rag`.

## Fora do escopo → redirecionar

| Situação | Agente |
|----------|--------|
| Implementar feature prod (não teste) | `backend`, `frontend-mobile`, `frontend-web` |
| Terraform, VPC, ECS, ECR | `cloud-infra` |
| GitHub Actions, deploy pipeline | `devops-cicd` |
| Migration/schema PostgreSQL ou Redis | `database` |
| Validar PR em In Test (gate) | `qa-gate` |
| Submit App Store / Play | `stores-release` |

**Anti-pattern:** comentar issue e redirecionar, não implementar feature fora do harness.

Referência completa: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md). LangGraph reclassifica via `lib/agent_registry.resolve_agent_for_task` antes de `implement`.

## Quando usar

- `agent_role == qa`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`qa` / qa-author) |
|--------------|-----|---------------------------|
| In Progress | `implement` | **Owner** — specs, harness, `open_pr` |
| In Code Review | `review` | Via `qa-reviewer` |
| Ready for Test / In Test | `wait_ci` / `qa` | Gate executado por **`qa-gate`** (evidências) |

Ciclo creator: `route → load_context → implement → apply → route`

## Ambiente local mobile

Ver `docs/operacao/LOCAL_E2E_MOBILE.md` e [MOBILE_SETUP_EVIDENCE.md](MOBILE_SETUP_EVIDENCE.md).

```bash
python agents/qa-gate/scripts/local_e2e_smoke.py check
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-XXX --mode check
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-XXX --feature pairing --mode cycle
```

## Casos de teste — pareamento (referência)

| ID | Nome | Automatizado |
|----|------|--------------|
| S0 | Login parent | API + Appium |
| S0.1 | Provisionar família/filho | API + Appium |
| 1 | Código válido (happy path) | API + Appium |
| 2 | Código inválido + rate limit | Appium |
| 4 | Persistência sessão após restart | Appium |
| 8 | Offline + retry | Appium |

## Workflow board → PR

1. Claim task de teste; In Progress.
2. Branch `test/T-XXX-NNN-<slug>`.
3. Adicionar/atualizar specs; não alterar lógica prod sem necessidade.
4. Executar suite local; anexar evidências na issue.
5. PR: cenários cobertos, gaps, flaky risks, como rodar localmente.
6. Se bug encontrado: issue separada + link no PR.

## Critérios de aceite

- Testes reproduzíveis localmente (`local_e2e_stack.ps1`)
- Cenários críticos: SOS <30s, geofence entry/exit, push som emergência, pareamento 0→1
- Screenshots/logs anexados em tasks E2E mobile
- Coverage não regredir no módulo afetado

## Palavras-chave

`teste`, `test`, `e2e`, `spec`, `QA`, `coverage`, `Appium`, `pairing`, `pareamento`, `push SOS`

## Métricas PR

`task_id`, `agent_role: qa`, `test_files[]`, `scenarios_count`, `ci_job`, `evidence`.
