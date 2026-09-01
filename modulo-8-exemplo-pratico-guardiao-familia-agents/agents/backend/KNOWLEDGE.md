# Base de conhecimento — módulo 8

Digest gerado de todos os `README.md` (exceto `output/`, `skills/` legado).
Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`

## agents/

### `agents/00-orchestration/docs/`
- **Papel:** Documentação técnica do grafo e integrações.
- README: [`agents/00-orchestration/docs/README.md`](../00-orchestration/docs/README.md)

### `agents/00-orchestration/evals/datasets/`
- **Papel:** JSON/CSV com tasks piloto e sequência esperada de eventos.
- README: [`agents/00-orchestration/evals/datasets/README.md`](../00-orchestration/evals/datasets/README.md)

### `agents/00-orchestration/evals/`
- **Papel:** Datasets e runners de regressão do pipeline Kanban.
- Decisão: Falha de eval → não promover mudança de policy sem revisão
- Decisão: Traces em LangSmith (`LANGCHAIN_PROJECT`)
- README: [`agents/00-orchestration/evals/README.md`](../00-orchestration/evals/README.md)

### `agents/00-orchestration/guardiao_mcp/`
- **Papel:** Fachada MCP sobre `lib/*`. Status **só** via `emit_status_event` (gateway).
- README: [`agents/00-orchestration/guardiao_mcp/README.md`](../00-orchestration/guardiao_mcp/README.md)

### `agents/00-orchestration/langgraph_app/`
- **Papel:** Orquestração Kanban: claim → context → decide → implement → review → QA → CI → HITL → apply.
- README: [`agents/00-orchestration/langgraph_app/README.md`](../00-orchestration/langgraph_app/README.md)

### `agents/00-orchestration/`
- **Papel:** Pipeline LangGraph, MCP, evals e CLIs do módulo 8.
- README: [`agents/00-orchestration/README.md`](../00-orchestration/README.md)

### `agents/00-orchestration/schemas/`
- **Papel:** Cópia espelhada em `board_automation/schemas/` quando aplicável.
- README: [`agents/00-orchestration/schemas/README.md`](../00-orchestration/schemas/README.md)

### `agents/00-orchestration/scripts/board/`
- **Papel:** Wrappers antigos de CLIs de board.
- README: [`agents/00-orchestration/scripts/board/README.md`](../00-orchestration/scripts/board/README.md)

### `agents/00-orchestration/scripts/cli/`
- **Papel:** Porta única de Status: sempre `gateway_cli` ou MCP `emit_status_event`.
- README: [`agents/00-orchestration/scripts/cli/README.md`](../00-orchestration/scripts/cli/README.md)

### `agents/00-orchestration/scripts/demo/`
- **Papel:** Usar em apresentações; não confundir com operação 24/7.
- README: [`agents/00-orchestration/scripts/demo/README.md`](../00-orchestration/scripts/demo/README.md)

### `agents/00-orchestration/scripts/langgraph/`
- **Papel:** Decisão: `dry_run` para banca; `live` só com tokens e HITL configurados.
- README: [`agents/00-orchestration/scripts/langgraph/README.md`](../00-orchestration/scripts/langgraph/README.md)

### `agents/00-orchestration/scripts/ops/`
- **Papel:** Scripts de manutenção do repositório (migração de paths, reorganização).
- README: [`agents/00-orchestration/scripts/ops/README.md`](../00-orchestration/scripts/ops/README.md)

### `agents/00-orchestration/scripts/`
- **Papel:** Paths: `lib.paths.orch_script("langgraph/langgraph_run.py")`
- README: [`agents/00-orchestration/scripts/README.md`](../00-orchestration/scripts/README.md)

### `agents/00-orchestration/scripts/worker/`
- **Papel:** Artefatos: `agents/00-runtime/system/dispatch/`
- README: [`agents/00-orchestration/scripts/worker/README.md`](../00-orchestration/scripts/worker/README.md)

### `agents/00-runtime/`
- **Papel:** Ambiente Python e artefatos gerados em execução.
- Decisão: Instalar deps: `pip install -r agents/00-runtime/requirements.txt`
- Decisão: Env: `.env` na raiz do módulo (`lib/env_load.py`)
- README: [`agents/00-runtime/README.md`](../00-runtime/README.md)

### `agents/00-runtime/system/`
- **Papel:** Pasta **efêmera** (`.gitignore`). Estado compartilhado entre tickets — **não** coloque aqui pastas `T-P*`.
- README: [`agents/00-runtime/system/README.md`](../00-runtime/system/README.md)

### `agents/_shared/`
- **Papel:** Documentos lidos por **todos** os papéis antes de agir.
- Decisão: Nunca alterar Status fora de `emit_status_event`
- Decisão: Roteamento de task: `board_automation.board.task_router` + CSV
- README: [`agents/_shared/README.md`](../_shared/README.md)

### `agents/backend/`
- **Papel:** Creator — implementa features, corrige bugs e abre PRs no repositório **guardiao-familia-api** (NestJS).
- Acionar: Task no board com `agent_role=backend` (ver `TASK_AGENT_MAP.csv`)
- Acionar: Endpoints REST/GraphQL, módulos NestJS, DTOs, guards, integrações de serviço
- Acionar: Correções de API consumidas por mobile ou web
- Decisão: **Gateway:** alterar Status somente via `emit_status_event` (MCP) — nunca editar coluna do board manualmente
- Decisão: **Handoff:** gravar PR, branch e dúvidas em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/backend/README.md`](README.md)

### `agents/backend-reviewer/`
- **Papel:** Reviewer — revisa PRs de backend (NestJS) e emite veredito via gateway; em alto risco, `approved` é proposta sujeita a HITL.
- Acionar: Task em `Ready for Code Review` / `In Code Review` com handoff do `backend`
- Acionar: Validação de contratos API, segurança (auth, LGPD), SOS e pagamentos
- Acionar: Disputa creator/reviewer registrada no handoff
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler obrigatoriamente `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- README: [`agents/backend-reviewer/README.md`](../backend-reviewer/README.md)

### `agents/cloud-infra/`
- **Papel:** Creator — provisiona e altera infraestrutura AWS via **Terraform** (VPC, ECS/Fargate, RDS, etc.).
- Acionar: Task com `agent_role=cloud-infra`
- Acionar: Módulos Terraform, variáveis de ambiente, recursos AWS novos ou ajustes
- Acionar: Alinhamento de infra com requisitos de backend/mobile/web
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** plan/PR, ambientes afetados em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/cloud-infra/README.md`](../cloud-infra/README.md)

### `agents/cloud-infra-reviewer/`
- **Papel:** Reviewer — revisa PRs de infraestrutura Terraform/AWS e emite veredito via gateway.
- Acionar: Task em code review com handoff do `cloud-infra`
- Acionar: Validação de segurança (IAM, SG), custo, drift e impacto em ambientes
- Acionar: Disputas de mudanças de infra
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (plan, ambientes)
- README: [`agents/cloud-infra-reviewer/README.md`](../cloud-infra-reviewer/README.md)

### `agents/database/`
- **Papel:** Creator — modela schema, escreve migrations e abre PRs de banco de dados do Guardião Família.
- Acionar: Task com `agent_role=database`
- Acionar: Migrations, índices, constraints, seeds e ajustes de performance SQL
- Acionar: Alinhamento de modelo de dados com requisitos de backend
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** migrations, ordem de deploy em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/database/README.md`](../database/README.md)

### `agents/database-reviewer/`
- **Papel:** Reviewer — revisa PRs de banco (migrations, schema) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `database`
- Acionar: Validação de integridade, rollback, impacto em dados e compatibilidade com API
- Acionar: Disputas de modelagem
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/database-reviewer/README.md`](../database-reviewer/README.md)

### `agents/devops-cicd/`
- **Papel:** Creator — configura e mantém pipelines **CI/CD** (GitHub Actions, build, test, deploy hooks).
- Acionar: Task com `agent_role=devops-cicd`
- Acionar: Workflows YAML, secrets de CI, gates de qualidade no pipeline
- Acionar: Integração de testes automatizados no fluxo de PR/merge
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** workflows alterados, impacto em repos em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/devops-cicd/README.md`](../devops-cicd/README.md)

### `agents/devops-cicd-reviewer/`
- **Papel:** Reviewer — revisa PRs de CI/CD e emite veredito via gateway.
- Acionar: Task em code review com handoff do `devops-cicd`
- Acionar: Validação de segurança de workflows, permissões, caches e impacto em builds
- Acionar: Disputas de pipeline
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/devops-cicd-reviewer/README.md`](../devops-cicd-reviewer/README.md)

### `agents/frontend-mobile/`
- **Papel:** Creator — implementa e abre PRs nos apps **React Native** Guardião Família (parent e child).
- Acionar: Task com `agent_role=frontend-mobile`
- Acionar: Telas, navegação, pairing, fluxos parent/child, integração com API
- Acionar: Correções de UX mobile ou bugs específicos de emulador/dispositivo
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** PR, branch, screenshots ou dúvidas em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/frontend-mobile/README.md`](../frontend-mobile/README.md)

### `agents/frontend-mobile-reviewer/`
- **Papel:** Reviewer — revisa PRs dos apps React Native (parent/child) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `frontend-mobile`
- Acionar: Validação de navegação, acessibilidade, contratos com API e padrões RN
- Acionar: Disputas de implementação mobile
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- README: [`agents/frontend-mobile-reviewer/README.md`](../frontend-mobile-reviewer/README.md)

### `agents/frontend-web/`
- **Papel:** Creator — implementa e abre PRs no site **guardiao-familia-site** (frontend web).
- Acionar: Task com `agent_role=frontend-web`
- Acionar: Páginas, componentes, rotas, integração com API no browser
- Acionar: Ajustes de layout, SEO ou fluxos web do produto
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** PR e contexto em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/frontend-web/README.md`](../frontend-web/README.md)

### `agents/frontend-web-reviewer/`
- **Papel:** Reviewer — revisa PRs do site web (guardiao-familia-site) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `frontend-web`
- Acionar: Validação de UX, acessibilidade, performance e contratos com API
- Acionar: Disputas de implementação web
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- README: [`agents/frontend-web-reviewer/README.md`](../frontend-web-reviewer/README.md)

### `agents/qa/`
- **Papel:** Creator — executa e documenta testes **E2E cross-stack** (API + web + mobile) do Guardião Família.
- Acionar: Task com `agent_role=qa`
- Acionar: Cenários E2E integrados, regressão entre stacks, evidências de fluxo completo
- Acionar: Validação pós-implementação antes ou após gate formal
- Decisão: **Gateway:** `start_test`, `test_passed`, `test_failed_bug` via `emit_status_event`
- Decisão: **Handoff:** cenários, logs e artefatos em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/qa/README.md`](../qa/README.md)

### `agents/qa-author/`
- **Papel:** Creator — authora e mantém o **harness de testes** (fixtures, helpers, dados seed, estrutura de suites).
- Acionar: Task com `agent_role=qa-author`
- Acionar: Novos helpers de teste, seeds de DB para QA, utilitários Appium/E2E
- Acionar: Refatoração do harness compartilhado entre `qa` e `qa-gate`
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** arquivos alterados, contratos de seed em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/qa-author/README.md`](../qa-author/README.md)

### `agents/qa-author-reviewer/`
- **Papel:** Reviewer — revisa PRs de harness de testes e emite veredito via gateway.
- Acionar: Task em code review com handoff do `qa-author`
- Acionar: Validação de seeds, idempotência, isolamento de ambientes e reuso pelo gate
- Acionar: Disputas sobre estrutura do harness
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/qa-author-reviewer/README.md`](../qa-author-reviewer/README.md)

### `agents/qa-gate/`
- **Título:** qa-gate
- Decisão: Não claimar harness em Todo (`qa-author`)
- Decisão: Mobile child: **seed parent** (`basic_parent`/`parent_home`) → `qa_appium_suite_child(child_only=true)` → evidência → cleanup
- README: [`agents/qa-gate/README.md`](../qa-gate/README.md)

### `agents/qa-gate/scripts/`
- **Papel:** Path helper: `lib.paths.qa_script("qa_mobile_evidence.py")`
- README: [`agents/qa-gate/scripts/README.md`](../qa-gate/scripts/README.md)

### `agents/qa-reviewer/`
- **Papel:** Reviewer — revisa planos, evidências e resultados E2E do `qa` e emite veredito via gateway.
- Acionar: Task em review com handoff do `qa`
- Acionar: Validação de cobertura de cenários, qualidade de evidências e classificação de bugs
- Acionar: Disputas sobre pass/fail de testes cross-stack
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (evidências anexas)
- README: [`agents/qa-reviewer/README.md`](../qa-reviewer/README.md)

### `agents/`
- **Papel:** ﻿# Agentes — Guardião Família
- Decisão: **Canônico:** `agents/{role}/SKILL.md` (não `skills/`)
- Decisão: **Base de conhecimento:** `agents/{role}/KNOWLEDGE.md` ou `agents/_shared/REPO_KNOWLEDGE.md`
- README: [`agents/README.md`](../README.md)

### `agents/skills/`
- **Papel:** Cópias antigas de skills por papel. **Canônico:** `agents/{role}/SKILL.md`.
- README: [`agents/skills/README.md`](../skills/README.md)

### `agents/stores-release/`
- **Papel:** Creator — prepara e executa releases nas **app stores** (Google Play, App Store) do Guardião Família.
- Acionar: Task com `agent_role=stores-release`
- Acionar: Versionamento, changelogs, metadados de loja, tracks de release
- Acionar: Coordenação de build assinado e submissão
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** versão, track, links de release em `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/stores-release/README.md`](../stores-release/README.md)

### `agents/stores-release-reviewer/`
- **Papel:** Reviewer — revisa releases e configurações de app stores e emite veredito via gateway.
- Acionar: Task em review com handoff do `stores-release`
- Acionar: Validação de versão, metadados, compliance de loja e rollback plan
- Acionar: Disputas de submissão
- Decisão: **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- README: [`agents/stores-release-reviewer/README.md`](../stores-release-reviewer/README.md)

## board_automation/

### `board_automation/board/`
- **Papel:** API de domínio do GitHub Project e roteamento de tasks.
- README: [`board_automation/board/README.md`](../../board_automation/board/README.md)

### `board_automation/data/backlogs/`
- **Papel:** Backlogs de seed (Project 3, infra Fargate) usados por scripts em `scripts/seeds/`.
- README: [`board_automation/data/backlogs/README.md`](../../board_automation/data/backlogs/README.md)

### `board_automation/data/imports/`
- **Papel:** Snapshots para import/sync do Project #2 (módulo 7).
- README: [`board_automation/data/imports/README.md`](../../board_automation/data/imports/README.md)

### `board_automation/data/maps/`
- **Papel:** Env: `GUARDAO_TASK_MAP_CSV` (default `TASK_AGENT_MAP.csv`).
- README: [`board_automation/data/maps/README.md`](../../board_automation/data/maps/README.md)

### `board_automation/data/`
- **Papel:** Decisão: alterar roteamento → editar CSV + `classify_tasks.py` / reconcile.
- README: [`board_automation/data/README.md`](../../board_automation/data/README.md)

### `board_automation/docs/`
- **Papel:** Templates de issue: [`../templates/`](../templates/)
- README: [`board_automation/docs/README.md`](../../board_automation/docs/README.md)

### `board_automation/`
- **Papel:** GitHub Project, roteamento de tasks, templates de issue e sincronização de status.
- README: [`board_automation/README.md`](../../board_automation/README.md)

### `board_automation/schemas/`
- **Papel:** Espelho de `agents/00-orchestration/schemas/board_events.json`.
- README: [`board_automation/schemas/README.md`](../../board_automation/schemas/README.md)

### `board_automation/scripts/cli/`
- **Papel:** Sempre `--dry-run` primeiro em produção.
- README: [`board_automation/scripts/cli/README.md`](../../board_automation/scripts/cli/README.md)

### `board_automation/scripts/ops/`
- **Papel:** Manutenção estrutural de `board_automation/` (moves, reorganização).
- README: [`board_automation/scripts/ops/README.md`](../../board_automation/scripts/ops/README.md)

### `board_automation/scripts/`
- **Papel:** Helper: `lib.paths.board_script("cli/reconcile_board.py")`
- README: [`board_automation/scripts/README.md`](../../board_automation/scripts/README.md)

### `board_automation/scripts/seeds/`
- **Papel:** Logs: `agents/00-runtime/system/board/`
- README: [`board_automation/scripts/seeds/README.md`](../../board_automation/scripts/seeds/README.md)

### `board_automation/templates/.github/ISSUE_TEMPLATE/`
- **Papel:** Copiar para `.github/ISSUE_TEMPLATE/` de cada repo produto.
- README: [`board_automation/templates/.github/ISSUE_TEMPLATE/README.md`](../../board_automation/templates/.github/ISSUE_TEMPLATE/README.md)

### `board_automation/templates/.github/`
- **Papel:** Copiar `ISSUE_TEMPLATE/agent-task.yml` para cada repo `guardiao-familia-*`.
- README: [`board_automation/templates/.github/README.md`](../../board_automation/templates/.github/README.md)

### `board_automation/templates/github-workflows/`
- **Papel:** Workflow YAML para copiar em **repos produto** (sinais CI → orquestrador).
- README: [`board_automation/templates/github-workflows/README.md`](../../board_automation/templates/github-workflows/README.md)

### `board_automation/templates/`
- **Papel:** Copiar para repos produto conforme necessário.
- README: [`board_automation/templates/README.md`](../../board_automation/templates/README.md)

## certs/

### `certs/`
- **Papel:** CA bundle para `lib/env_load.py` e SDK Android em ambientes com proxy SSL.
- README: [`certs/README.md`](../../certs/README.md)

## docs/

### `docs/apresentacao/`
- **Papel:** Material para banca e demonstrações paced.
- README: [`docs/apresentacao/README.md`](../../docs/apresentacao/README.md)

### `docs/autonomia/fases/`
- **Papel:** Registros das fases do [`GUIA_LANGGRAPH_MCP_LLM.md`](../GUIA_LANGGRAPH_MCP_LLM.md).
- README: [`docs/autonomia/fases/README.md`](../../docs/autonomia/fases/README.md)

### `docs/autonomia/orquestracao/`
- **Papel:** Visão completa do fluxo Guardião Família (módulo 8): **onde cada tecnologia entra**, papéis de agentes, modelos LLM, MCP, nós LangGraph e porta única do gateway.
- README: [`docs/autonomia/orquestracao/README.md`](../../docs/autonomia/orquestracao/README.md)

### `docs/autonomia/`
- **Papel:** Documentação as-is: fluxo, processo, tecnologia e execução.
- README: [`docs/autonomia/README.md`](../../docs/autonomia/README.md)

### `docs/comportamento/`
- **Papel:** Aponta para `agents/{role}/agent.md` e `SKILL.md` de cada papel.
- README: [`docs/comportamento/README.md`](../../docs/comportamento/README.md)

### `docs/live/`
- **Papel:** Espelho publicado em GitHub Pages (`dashboard.html`, `snapshot.json`).
- README: [`docs/live/README.md`](../../docs/live/README.md)

### `docs/operacao/`
- **Papel:** Procedimentos HITL, operação diária e E2E mobile local.
- README: [`docs/operacao/README.md`](../../docs/operacao/README.md)

### `docs/`
- **Papel:** Índice para **agentes e operadores**: comportamento, operação, autonomia.
- README: [`docs/README.md`](../../docs/README.md)

### `docs/templates/`
- **Papel:** Templates de **issues e board**: [board_automation/templates/](../../board_automation/templates/)
- README: [`docs/templates/README.md`](../../docs/templates/README.md)

## lib/

### `lib/ci/`
- **Papel:** Integração: nós `ci_nodes` no LangGraph.
- README: [`lib/ci/README.md`](../../lib/ci/README.md)

### `lib/core/`
- **Papel:** Usado por LangGraph, gateway e dispatch.
- README: [`lib/core/README.md`](../../lib/core/README.md)

### `lib/gateway/`
- **Papel:** Regra: LangGraph, MCP e CLIs **devem** passar por aqui.
- README: [`lib/gateway/README.md`](../../lib/gateway/README.md)

### `lib/mobile/`
- **Papel:** Scripts CLI: `agents/qa-gate/scripts/`
- README: [`lib/mobile/README.md`](../../lib/mobile/README.md)

### `lib/observability/`
- **Papel:** Saída: `agents/00-runtime/system/observability/` (`snapshot.json`, `tasks/*.json`)
- README: [`lib/observability/README.md`](../../lib/observability/README.md)

### `lib/orchestrator/`
- **Papel:** Estado: `agents/00-runtime/system/orchestrator/`
- README: [`lib/orchestrator/README.md`](../../lib/orchestrator/README.md)

### `lib/`
- **Papel:** Código de domínio usado por LangGraph, MCP, CLIs e worker. **Não** contém prompts de agente.
- Decisão: Não duplicar lógica de board em `lib/` — usar `board_automation.board`
- Decisão: Shims na raiz de `lib/*.py` podem existir; preferir subpacotes
- README: [`lib/README.md`](../../lib/README.md)

### `lib/site/`
- **Papel:** Automação do site `guardiao-familia-site` (hero, smoke).
- README: [`lib/site/README.md`](../../lib/site/README.md)

## ./

### `./`
- **Papel:** Base de conhecimento para **agentes autônomos**: orquestração LangGraph, board GitHub, gateway único de Status, MCP e QA mobile.
- README: [`./README.md`](../../README.md)
