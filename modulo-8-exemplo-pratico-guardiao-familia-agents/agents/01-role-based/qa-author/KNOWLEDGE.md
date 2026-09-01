# Base de conhecimento — módulo 8

Digest gerado de todos os `README.md` (exceto `output/`).
Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`

## MCP Guardião Família (v2)

Servidor: `guardiao_mcp` · [`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

**Classificação:** creator · **Papel:** `qa-author` · Revisor: `qa-author-reviewer`

| Tool | Quando |
|------|--------|
| `list_status_events` | Filtrar `agent_role=qa-author` |
| `on_status_event` | Antes de atuar — ticket, handoff, playbook |
| `hitl_guard_actuation` | Obrigatório antes de `execute_agent_actuation_tool` |
| `developer_implement` | Fase implement (`In Progress`) |
| `execute_agent_actuation_tool` | Fecha fase + emite próximo evento |
| `emit_status_event` | Única porta de status |

**Sequência:** `on_status_event` → `hitl_guard_actuation` → `developer_implement` → `execute` (use `phase_work`).

| Status | Evento |
|--------|--------|
| In Progress | `qa-author_in_progress` |
| Ready for Code Review | `qa-author_ready_for_code_review` (+ `pr_url`) |
| In Code Review | `qa-author_in_code_review` |

Handoff: `agents/00-runtime/output/{task_id}/handoff.json`

---

## agents/

### `agents/`
- **Papel:** Índice dos agentes — LangGraph v2, MCP role-based e papéis creator/reviewer/qa-gate/ops.
- Decisão: **Paths:** `lib/core/agent_paths.py` → `agents/01-role-based/{role}/`
- Decisão: **Status:** só via `emit_status_event`
- Decisão: **Handoff:** `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **Skill canônica:** `01-role-based/{role}/SKILL.md`
- README: [`agents/README.md`](../README.md)

### `agents/00-orchestration/`
- **Papel:** Pipeline LangGraph v2 (55 nós `evt_*`), MCP (14 tools), evals e CLIs.
- README: [`agents/00-orchestration/README.md`](../00-orchestration/README.md)

### `agents/00-orchestration/docs/`
- **Papel:** Documentação **canônica** consultada pelos agentes antes de agir. Referenciada em cada `agents/01-role-based/{role}/agent.md`.
- README: [`agents/00-orchestration/docs/README.md`](../00-orchestration/docs/README.md)

### `agents/00-orchestration/evals/`
- **Papel:** Datasets e runners de regressão do pipeline Kanban.
- Decisão: Falha de eval → não promover mudança de policy sem revisão
- Decisão: Traces em LangSmith (`LANGCHAIN_PROJECT`)
- README: [`agents/00-orchestration/evals/README.md`](../00-orchestration/evals/README.md)

### `agents/00-orchestration/evals/datasets/`
- **Papel:** JSON com tasks piloto e sequência esperada de eventos **role-based** (LangGraph v2).
- README: [`agents/00-orchestration/evals/datasets/README.md`](../00-orchestration/evals/datasets/README.md)

### `agents/00-orchestration/guardiao_mcp/`
- **Papel:** Fachada MCP sobre `lib/*` — **14 tools**. Status **só** via `emit_status_event` (eventos role-based).
- README: [`agents/00-orchestration/guardiao_mcp/README.md`](../00-orchestration/guardiao_mcp/README.md)

### `agents/00-orchestration/langgraph_app/`
- **Papel:** Grafo v2 — `sync_board` → `orchestrator_decide` → 55 nós `evt_*` → pipeline MCP → loop até Done.
- README: [`agents/00-orchestration/langgraph_app/README.md`](../00-orchestration/langgraph_app/README.md)

### `agents/00-orchestration/langgraph_app/nodes/evt/`
- **Papel:** Os 55 nós de evento são **gerados em runtime** por `nodes/factory.py` a partir de `registry/catalog.py`.
- README: [`agents/00-orchestration/langgraph_app/nodes/evt/README.md`](../00-orchestration/langgraph_app/nodes/evt/README.md)

### `agents/00-orchestration/schemas/`
- **Papel:** Cópia espelhada em `board_automation/schemas/` quando aplicável.
- README: [`agents/00-orchestration/schemas/README.md`](../00-orchestration/schemas/README.md)

### `agents/00-orchestration/scripts/`
- **Papel:** Paths: `lib.paths.orch_script("langgraph/langgraph_run.py")`
- README: [`agents/00-orchestration/scripts/README.md`](../00-orchestration/scripts/README.md)

### `agents/00-orchestration/scripts/cli/`
- **Papel:** Scripts operacionais — eventos **role-based v2** (`{agent_role}_{status_slug}`).
- README: [`agents/00-orchestration/scripts/cli/README.md`](../00-orchestration/scripts/cli/README.md)

### `agents/00-orchestration/scripts/langgraph/`
- **Papel:** Scripts **v2** — invocam `langgraph_app.run_once`.
- README: [`agents/00-orchestration/scripts/langgraph/README.md`](../00-orchestration/scripts/langgraph/README.md)

### `agents/00-runtime/`
- **Papel:** Ambiente Python e artefatos gerados em execução.
- Decisão: Instalar deps: `pip install -r agents/00-runtime/requirements.txt`
- Decisão: Env: `.env` na raiz do módulo (`lib/env_load.py`)
- Decisão: Paths: `lib/paths.py` — **nunca** hardcodar `output/` ou `system/` em código novo
- Decisão: Orquestração vive em `agents/00-orchestration/`, não aqui
- README: [`agents/00-runtime/README.md`](../00-runtime/README.md)

### `agents/00-runtime/system/`
- **Papel:** Pasta **efêmera** (`.gitignore`). Estado compartilhado entre tickets — **não** coloque aqui pastas `T-P*`.
- README: [`agents/00-runtime/system/README.md`](../00-runtime/system/README.md)

### `agents/01-role-based/`
- **Papel:** Pastas **creator**, **reviewer**, **qa-gate** e **ops** — prompts, skills e KNOWLEDGE de cada `agent_role`.
- README: [`agents/01-role-based/README.md`](../README.md)

### `agents/01-role-based/backend/`
- **Papel:** Creator — implementa features, corrige bugs e abre PRs no repositório **guardiao-familia-api** (NestJS).
- Acionar: Task no board com `agent_role=backend` (ver `TASK_AGENT_MAP.csv`)
- Acionar: Endpoints REST/GraphQL, módulos NestJS, DTOs, guards, integrações de serviço
- Acionar: Correções de API consumidas por mobile ou web
- Decisão: **Gateway:** alterar Status somente via `emit_status_event` (MCP) — nunca editar coluna do board manualmente
- Decisão: **Handoff:** gravar PR, branch e dúvidas em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `backend_*`; ver `agent.md`)
- Decisão: Nunca mergear PR; nunca alterar Terraform ou apps mobile
- README: [`agents/01-role-based/backend/README.md`](../backend/README.md)

### `agents/01-role-based/backend-reviewer/`
- **Papel:** Reviewer — revisa PRs de backend (NestJS) e emite veredito via gateway; em alto risco, `approved` é proposta sujeita a HITL.
- Acionar: Task em `Ready for Code Review` / `In Code Review` com handoff do `backend`
- Acionar: Validação de contratos API, segurança (auth, LGPD), SOS e pagamentos
- Acionar: Disputa creator/reviewer registrada no handoff
- Decisão: **Gateway:** eventos role-based `backend-reviewer_in_code_review`, `backend-reviewer_ready_for_test`, `backend-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler obrigatoriamente `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Decisão: Em alto risco, não avançar autonomia plena sem HITL humano
- README: [`agents/01-role-based/backend-reviewer/README.md`](../backend-reviewer/README.md)

### `agents/01-role-based/cloud-infra/`
- **Papel:** Creator — provisiona e altera infraestrutura AWS via **Terraform** (VPC, ECS/Fargate, RDS, etc.).
- Acionar: Task com `agent_role=cloud-infra`
- Acionar: Módulos Terraform, variáveis de ambiente, recursos AWS novos ou ajustes
- Acionar: Alinhamento de infra com requisitos de backend/mobile/web
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** plan/PR, ambientes afetados em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `cloud-infra_*`; ver `agent.md`)
- Decisão: Nunca aplicar destroy em produção sem HITL; nunca alterar código de app
- README: [`agents/01-role-based/cloud-infra/README.md`](../cloud-infra/README.md)

### `agents/01-role-based/cloud-infra-reviewer/`
- **Papel:** Reviewer — revisa PRs de infraestrutura Terraform/AWS e emite veredito via gateway.
- Acionar: Task em code review com handoff do `cloud-infra`
- Acionar: Validação de segurança (IAM, SG), custo, drift e impacto em ambientes
- Acionar: Disputas de mudanças de infra
- Decisão: **Gateway:** eventos role-based `cloud-infra-reviewer_in_code_review`, `cloud-infra-reviewer_ready_for_test`, `cloud-infra-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (plan, ambientes)
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Decisão: Mudanças de alto risco exigem HITL antes de apply em produção
- README: [`agents/01-role-based/cloud-infra-reviewer/README.md`](../cloud-infra-reviewer/README.md)

### `agents/01-role-based/database/`
- **Papel:** Creator — modela schema, escreve migrations e abre PRs de banco de dados do Guardião Família.
- Acionar: Task com `agent_role=database`
- Acionar: Migrations, índices, constraints, seeds e ajustes de performance SQL
- Acionar: Alinhamento de modelo de dados com requisitos de backend
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** migrations, ordem de deploy em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `database_*`; ver `agent.md`)
- Decisão: Nunca dropar dados em produção sem HITL explícito
- README: [`agents/01-role-based/database/README.md`](../database/README.md)

### `agents/01-role-based/database-reviewer/`
- **Papel:** Reviewer — revisa PRs de banco (migrations, schema) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `database`
- Acionar: Validação de integridade, rollback, impacto em dados e compatibilidade com API
- Acionar: Disputas de modelagem
- Decisão: **Gateway:** eventos role-based `database-reviewer_in_code_review`, `database-reviewer_ready_for_test`, `database-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/database-reviewer/README.md`](../database-reviewer/README.md)

### `agents/01-role-based/devops-cicd/`
- **Papel:** Creator — configura e mantém pipelines **CI/CD** (GitHub Actions, build, test, deploy hooks).
- Acionar: Task com `agent_role=devops-cicd`
- Acionar: Workflows YAML, secrets de CI, gates de qualidade no pipeline
- Acionar: Integração de testes automatizados no fluxo de PR/merge
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** workflows alterados, impacto em repos em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `devops-cicd_*`; ver `agent.md`)
- Decisão: Nunca expor secrets no repositório; nunca mergear sem reviewer
- README: [`agents/01-role-based/devops-cicd/README.md`](../devops-cicd/README.md)

### `agents/01-role-based/devops-cicd-reviewer/`
- **Papel:** Reviewer — revisa PRs de CI/CD e emite veredito via gateway.
- Acionar: Task em code review com handoff do `devops-cicd`
- Acionar: Validação de segurança de workflows, permissões, caches e impacto em builds
- Acionar: Disputas de pipeline
- Decisão: **Gateway:** eventos role-based `devops-cicd-reviewer_in_code_review`, `devops-cicd-reviewer_ready_for_test`, `devops-cicd-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/devops-cicd-reviewer/README.md`](../devops-cicd-reviewer/README.md)

### `agents/01-role-based/frontend-mobile/`
- **Papel:** Creator — implementa e abre PRs nos apps **React Native** Guardião Família (parent e child).
- Acionar: Task com `agent_role=frontend-mobile`
- Acionar: Telas, navegação, pairing, fluxos parent/child, integração com API
- Acionar: Correções de UX mobile ou bugs específicos de emulador/dispositivo
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** PR, branch, screenshots ou dúvidas em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `frontend-mobile_*`; ver `agent.md`)
- Decisão: Nunca mergear; não alterar Terraform ou harness de QA
- README: [`agents/01-role-based/frontend-mobile/README.md`](../frontend-mobile/README.md)

### `agents/01-role-based/frontend-mobile-reviewer/`
- **Papel:** Reviewer — revisa PRs dos apps React Native (parent/child) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `frontend-mobile`
- Acionar: Validação de navegação, acessibilidade, contratos com API e padrões RN
- Acionar: Disputas de implementação mobile
- Decisão: **Gateway:** eventos role-based `frontend-mobile-reviewer_in_code_review`, `frontend-mobile-reviewer_ready_for_test`, `frontend-mobile-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/frontend-mobile-reviewer/README.md`](../frontend-mobile-reviewer/README.md)

### `agents/01-role-based/frontend-web/`
- **Papel:** Creator — implementa e abre PRs no site **guardiao-familia-site** (frontend web).
- Acionar: Task com `agent_role=frontend-web`
- Acionar: Páginas, componentes, rotas, integração com API no browser
- Acionar: Ajustes de layout, SEO ou fluxos web do produto
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** PR e contexto em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `frontend-web_*`; ver `agent.md`)
- Decisão: Nunca mergear sem passar pelo reviewer pareado
- README: [`agents/01-role-based/frontend-web/README.md`](../frontend-web/README.md)

### `agents/01-role-based/frontend-web-reviewer/`
- **Papel:** Reviewer — revisa PRs do site web (guardiao-familia-site) e emite veredito via gateway.
- Acionar: Task em code review com handoff do `frontend-web`
- Acionar: Validação de UX, acessibilidade, performance e contratos com API
- Acionar: Disputas de implementação web
- Decisão: **Gateway:** eventos role-based `frontend-web-reviewer_in_code_review`, `frontend-web-reviewer_ready_for_test`, `frontend-web-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/frontend-web-reviewer/README.md`](../frontend-web-reviewer/README.md)

### `agents/01-role-based/qa/`
- **Papel:** Creator — executa e documenta testes **E2E cross-stack** (API + web + mobile) do Guardião Família.
- Acionar: Task com `agent_role=qa`
- Acionar: Cenários E2E integrados, regressão entre stacks, evidências de fluxo completo
- Acionar: Validação pós-implementação antes ou após gate formal
- Decisão: **Gateway:** eventos role-based `qa-author_in_progress`, `qa-author_ready_for_code_review` via `emit_status_event` (alias CSV `qa`; legado v1 rejeitado)
- Decisão: **Handoff:** cenários, logs e artefatos em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `qa_*`; ver `agent.md`)
- Decisão: Não iniciar harness em Todo — responsabilidade do `qa-author`
- README: [`agents/01-role-based/qa/README.md`](../qa/README.md)

### `agents/01-role-based/qa-author/`
- **Papel:** Creator — authora e mantém o **harness de testes** (fixtures, helpers, dados seed, estrutura de suites).
- Acionar: Task com `agent_role=qa-author`
- Acionar: Novos helpers de teste, seeds de DB para QA, utilitários Appium/E2E
- Acionar: Refatoração do harness compartilhado entre `qa` e `qa-gate`
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** arquivos alterados, contratos de seed em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `qa-author_*`; ver `agent.md`)
- Decisão: Harness deve ser reutilizável pelo `qa-gate` sem duplicar lógica
- README: [`agents/01-role-based/qa-author/README.md`](../qa-author/README.md)

### `agents/01-role-based/qa-author-reviewer/`
- **Papel:** Reviewer — revisa PRs de harness de testes e emite veredito via gateway.
- Acionar: Task em code review com handoff do `qa-author`
- Acionar: Validação de seeds, idempotência, isolamento de ambientes e reuso pelo gate
- Acionar: Disputas sobre estrutura do harness
- Decisão: **Gateway:** eventos role-based `qa-author-reviewer_in_code_review`, `qa-author-reviewer_ready_for_test`, `qa-author-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/qa-author-reviewer/README.md`](../qa-author-reviewer/README.md)

### `agents/01-role-based/qa-gate/`
- **Título:** qa-gate
- **Papel:** Gate de qualidade da pipeline — executa testes e evidências após review.
- Decisão: **MCP:** `on_status_event` → `qa_validate` → `execute` — suites em `KNOWLEDGE.md`
- Decisão: Não iniciar harness em Todo — responsabilidade do `qa-author` (`orchestrator_enter_in_progress`)
- Decisão: Mobile child: **seed parent** (`basic_parent`/`parent_home`) → `qa_appium_suite_child(child_only=true)` → evidência → cleanup
- Decisão: Mobile parent UI: sem seed → `qa_appium_suite_parent(feature=...)`
- Decisão: Status: eventos role-based `qa-gate_in_test`, `qa-gate_in_pull_request`, `qa-gate_return_in_progress`
- README: [`agents/01-role-based/qa-gate/README.md`](../qa-gate/README.md)

### `agents/01-role-based/qa-reviewer/`
- **Papel:** Reviewer — revisa planos, evidências e resultados E2E do `qa` e emite veredito via gateway.
- Acionar: Task em review com handoff do `qa`
- Acionar: Validação de cobertura de cenários, qualidade de evidências e classificação de bugs
- Acionar: Disputas sobre pass/fail de testes cross-stack
- Decisão: **Gateway:** eventos role-based `qa-reviewer_in_code_review`, `qa-reviewer_ready_for_test`, `qa-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (evidências anexas)
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- README: [`agents/01-role-based/qa-reviewer/README.md`](../qa-reviewer/README.md)

### `agents/01-role-based/stores-release/`
- **Papel:** Creator — prepara e executa releases nas **app stores** (Google Play, App Store) do Guardião Família.
- Acionar: Task com `agent_role=stores-release`
- Acionar: Versionamento, changelogs, metadados de loja, tracks de release
- Acionar: Coordenação de build assinado e submissão
- Decisão: **Gateway:** Status apenas via `emit_status_event`
- Decisão: **Handoff:** versão, track, links de release em `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `stores-release_*`; ver `agent.md`)
- Decisão: Nunca publicar em produção sem reviewer e HITL quando `release_blocker`
- README: [`agents/01-role-based/stores-release/README.md`](../stores-release/README.md)

### `agents/01-role-based/stores-release-reviewer/`
- **Papel:** Reviewer — revisa releases e configurações de app stores e emite veredito via gateway.
- Acionar: Task em review com handoff do `stores-release`
- Acionar: Validação de versão, metadados, compliance de loja e rollback plan
- Acionar: Disputas de submissão
- Decisão: **Gateway:** eventos role-based `stores-release-reviewer_in_code_review`, `stores-release-reviewer_ready_for_test`, `stores-release-reviewer_return_in_progress` via `emit_status_event`
- Decisão: **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- Decisão: **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Decisão: Releases de alto risco exigem HITL antes de go-live
- README: [`agents/01-role-based/stores-release-reviewer/README.md`](../stores-release-reviewer/README.md)

## board_automation/

### `board_automation/`
- **Papel:** GitHub Project, roteamento de tasks, templates de issue e sincronização de status.
- README: [`board_automation/README.md`](../../board_automation/README.md)

### `board_automation/board/`
- **Papel:** API de domínio do GitHub Project e roteamento de tasks.
- README: [`board_automation/board/README.md`](../../board_automation/board/README.md)

### `board_automation/data/`
- **Papel:** Decisão: alterar roteamento → editar CSV + `classify_tasks.py` / reconcile.
- README: [`board_automation/data/README.md`](../../board_automation/data/README.md)

### `board_automation/data/backlogs/`
- **Papel:** Backlogs de seed (Project 3, infra Fargate) usados por scripts em `scripts/seeds/`.
- README: [`board_automation/data/backlogs/README.md`](../../board_automation/data/backlogs/README.md)

### `board_automation/data/imports/`
- **Papel:** Snapshots para import/sync do Project #2 (módulo 7).
- README: [`board_automation/data/imports/README.md`](../../board_automation/data/imports/README.md)

### `board_automation/data/maps/`
- **Papel:** Env: `GUARDAO_TASK_MAP_CSV` (default `TASK_AGENT_MAP.csv`).
- README: [`board_automation/data/maps/README.md`](../../board_automation/data/maps/README.md)

### `board_automation/docs/`
- **Papel:** Templates de issue: [`../templates/`](../templates/)
- README: [`board_automation/docs/README.md`](../../board_automation/docs/README.md)

### `board_automation/schemas/`
- **Papel:** Espelho de `agents/00-orchestration/schemas/board_events.json`.
- README: [`board_automation/schemas/README.md`](../../board_automation/schemas/README.md)

### `board_automation/scripts/`
- **Papel:** Helper: `lib.paths.board_script("cli/reconcile_board.py")`
- README: [`board_automation/scripts/README.md`](../../board_automation/scripts/README.md)

### `board_automation/scripts/cli/`
- **Papel:** Sempre `--dry-run` primeiro em produção.
- README: [`board_automation/scripts/cli/README.md`](../../board_automation/scripts/cli/README.md)

### `board_automation/scripts/ops/`
- **Papel:** Manutenção estrutural de `board_automation/` (moves, reorganização).
- README: [`board_automation/scripts/ops/README.md`](../../board_automation/scripts/ops/README.md)

### `board_automation/scripts/seeds/`
- **Papel:** Logs: `agents/00-runtime/system/board/`
- README: [`board_automation/scripts/seeds/README.md`](../../board_automation/scripts/seeds/README.md)

### `board_automation/templates/`
- **Papel:** Copiar para repos produto conforme necessário.
- README: [`board_automation/templates/README.md`](../../board_automation/templates/README.md)

### `board_automation/templates/.github/`
- **Papel:** Copiar `ISSUE_TEMPLATE/agent-task.yml` para cada repo `guardiao-familia-*`.
- README: [`board_automation/templates/.github/README.md`](../../board_automation/templates/.github/README.md)

### `board_automation/templates/.github/ISSUE_TEMPLATE/`
- **Papel:** Copiar para `.github/ISSUE_TEMPLATE/` de cada repo produto.
- README: [`board_automation/templates/.github/ISSUE_TEMPLATE/README.md`](../../board_automation/templates/.github/ISSUE_TEMPLATE/README.md)

### `board_automation/templates/github-workflows/`
- **Papel:** Workflow YAML para copiar em **repos produto** (sinais CI → orquestrador).
- README: [`board_automation/templates/github-workflows/README.md`](../../board_automation/templates/github-workflows/README.md)

## certs/

### `certs/`
- **Papel:** CA bundle para `lib/env_load.py` e SDK Android em ambientes com proxy SSL.
- README: [`certs/README.md`](../../certs/README.md)

## docs/

### `docs/`
- **Papel:** Índice para **agentes e operadores**: comportamento, operação, autonomia.
- README: [`docs/README.md`](../../docs/README.md)

### `docs/apresentacao/`
- **Papel:** Material para banca e demonstrações paced.
- README: [`docs/apresentacao/README.md`](../../docs/apresentacao/README.md)

### `docs/autonomia/`
- **Papel:** Documentação as-is: fluxo, processo, tecnologia e execução.
- README: [`docs/autonomia/README.md`](../../docs/autonomia/README.md)

### `docs/autonomia/fases/`
- **Papel:** Registros das fases do [`GUIA_LANGGRAPH_MCP_LLM.md`](../GUIA_LANGGRAPH_MCP_LLM.md).
- README: [`docs/autonomia/fases/README.md`](../../docs/autonomia/fases/README.md)

### `docs/autonomia/orquestracao/`
- **Papel:** Visão completa do fluxo Guardião Família (módulo 8): **onde cada tecnologia entra**, papéis de agentes, modelos LLM, MCP, nós LangGraph e porta única do gateway.
- README: [`docs/autonomia/orquestracao/README.md`](../../docs/autonomia/orquestracao/README.md)

### `docs/comportamento/`
- **Papel:** Aponta para `agents/01-role-based/{role}/agent.md` e `SKILL.md` de cada papel.
- README: [`docs/comportamento/README.md`](../../docs/comportamento/README.md)

### `docs/live/`
- **Papel:** Espelho publicado em GitHub Pages (`dashboard.html`, `snapshot.json`).
- README: [`docs/live/README.md`](../../docs/live/README.md)

### `docs/operacao/`
- **Papel:** Procedimentos HITL, operação diária e E2E mobile local.
- README: [`docs/operacao/README.md`](../../docs/operacao/README.md)

### `docs/templates/`
- **Papel:** Templates de **issues e board**: [board_automation/templates/](../../board_automation/templates/)
- README: [`docs/templates/README.md`](../../docs/templates/README.md)

## lib/

### `lib/`
- **Papel:** Código de domínio do pipeline MCP + LangGraph. Board GitHub: [`board_automation/`](../board_automation/).
- README: [`lib/README.md`](../../lib/README.md)

### `lib/ci/`
- **Papel:** Integração: sinais CI via `scripts/cli/ci_signal.py` → gateway role-based; grafo v2 em `langgraph_app/registry/`.
- README: [`lib/ci/README.md`](../../lib/ci/README.md)

### `lib/core/`
- **Papel:** Usado por LangGraph v2, gateway e MCP.
- README: [`lib/core/README.md`](../../lib/core/README.md)

### `lib/gateway/`
- **Papel:** **Formato v2:** `{agent_role}_{status_slug}` ou `{agent_role}_return_{status_slug}`.
- README: [`lib/gateway/README.md`](../../lib/gateway/README.md)

### `lib/mobile/`
- README: [`lib/mobile/README.md`](../../lib/mobile/README.md)

### `lib/orchestrator/`
- README: [`lib/orchestrator/README.md`](../../lib/orchestrator/README.md)

### `lib/site/`
- **Papel:** Automação do site `guardiao-familia-site` (hero, smoke).
- README: [`lib/site/README.md`](../../lib/site/README.md)

## ./

### `./`
- **Papel:** Evolução do módulo 7 com HITL, multi-agent e gates enterprise.
- README: [`README.md`](../../README.md)

