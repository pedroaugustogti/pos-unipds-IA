"""Prompts MCP para orientar a LLM — descrições objetivas por tool."""

SERVER_INSTRUCTIONS = """\
Servidor MCP do Guardião Família (módulo 8). Siga estas regras em TODA sessão:

## Regras obrigatórias
1. **Status do board:** altere SOMENTE com `emit_status_event`. Nunca invente status nem use CLI direto.
2. **Escritas:** `dry_run=true` (padrão) para validar payload; `dry_run=false` só quando tiver certeza.
3. **Merge:** `merge_pr` exige `approve_hitl` humano antes de `dry_run=false`.
4. **ReAct:** após cada ação relevante, registre com `append_task_action_tool` (thought + action + observation).
5. **Handoff:** leia com `get_handoff` antes de agir; grave com `write_handoff_tool` ao passar fase.

## Fluxo por papel
| Papel | Sequência típica |
|-------|------------------|
| creator | `pick_task_tool` → `get_handoff` → implementar → `emit_status_event(open_pr)` |
| reviewer | `get_handoff` → `emit_status_event(start_review)` → review → `approve_review` ou `request_changes` |
| qa-gate | `get_handoff` → `emit_status_event(start_test)` → `query_mobile_flow_rag` → `qa_db_seed` → `qa_appium_suite_child` → evidências → `qa_db_cleanup` → `test_passed` ou `test_failed_bug` |
| devops-cicd | `list_hitl_queue` → `approve_hitl` → `emit_status_event(merge_pr)` |

## QA mobile (ordem obrigatória)
1. `qa_db_seed(task_id, profile, dry_run=false)` — Postgres + stage-handoff.json
2. `qa_appium_suite_child(from_db_seed=true, task_id=..., feature=pairing, dry_run=false)` — dual emulator
3. Capturar PNG/MP4 em `agents/00-runtime/output/mobile/qa_evidence/{task_id}/`
4. `qa_db_cleanup(task_id, dry_run=false)` — purge + reset handoff
5. `emit_status_event(test_passed|test_failed_bug, dry_run=false)`

Catálogo completo: `list_mcp_tools`. Detalhes: `agents/_shared/MCP_TOOLS.md`.
"""

# --- Gateway / HITL ---

EMIT_STATUS_EVENT = """\
**Quando:** mover task no board Kanban (única porta de status).

**Faz:** valida evento → transição de status → atualiza board GitHub → opcionalmente handoff.

**Eventos válidos e status alvo:**
| event | status alvo | quem usa |
|-------|-------------|----------|
| claim, start_work | In Progress | creators |
| open_pr | Ready for Code Review | creators |
| start_review | In Code Review | reviewers |
| request_changes | In Progress | reviewers |
| resubmit_review | In Code Review | creators (pós-correção) |
| approve_review | Ready for Test | reviewers |
| start_test | In Test | qa-gate |
| test_passed | In Pull Request | qa-gate |
| test_failed_bug | In Progress | qa-gate |
| merge_pr | Done | devops-cicd (requer HITL) |
| reopen | Todo | orchestrator |

**Parâmetros:**
- task_id: ID da task (ex: T-P3-009)
- event: um dos eventos acima
- summary: resumo curto do motivo (obrigatório em produção)
- dry_run: true (padrão) simula; false aplica
- pr_url: URL do PR (use em open_pr)
- from_agent: papel que dispara (ex: qa-gate)

**Antes de dry_run=false:** confirme handoff, AC da issue e papel correto.
"""

LIST_HITL_QUEUE = """\
**Quando:** antes de merge ou quando suspeitar de bloqueio humano.

**Faz:** lista eventos pendentes de aprovação (merge_pr, blocker, review alto risco).

**Retorna:** fila HITL com task_id, event e contexto.
"""

APPROVE_HITL = """\
**Quando:** humano aprovou ação bloqueada (tipicamente merge_pr).

**Faz:** libera evento na fila HITL para execução posterior.

**Parâmetros:** task_id, event (ex: merge_pr), dry_run (padrão true).

**Depois:** chame `emit_status_event` com o mesmo event e dry_run=false.
"""

# --- Observability / model ---

SNAPSHOT_OBSERVABILITY = """\
**Quando:** supervisor/orchestrator precisa visão do sistema.

**Faz:** snapshot de agentes idle/busy, filas dispatch e Kanban piloto.

**Parâmetros:** write_html=true gera dashboard HTML em output/.
"""

SELECT_MODEL_TIER = """\
**Quando:** escolher tier de modelo antes de implementar/revisar.

**Faz:** consulta `select_model` (Fase A) com base em purpose e metadados da task.

**purpose:** route | implement_low | implement_high | review | summarize | cursor
"""

# --- Orchestrator ---

LIST_IDLE_AGENTS = """\
**Quando:** despachar trabalho ou verificar capacidade.

**Faz:** lista papéis (agent_role) ociosos no agent_runtime.
"""

RESOLVE_AGENT_FOR_BOARD_EVENT = """\
**Quando:** após um evento, descobrir qual agent_role deve atuar.

**Faz:** resolve papel responsável dado task_id + event.

**Pré-requisito:** task_id deve existir no CSV do board.
"""

DRAIN_DISPATCH_QUEUE = """\
**Quando:** agentes idle e há jobs na fila.

**Faz:** despacha até `limit` itens da dispatch_queue para agentes ociosos.

**Parâmetros:** limit (padrão 5, máx recomendado 10).
"""

MARK_AGENT_IDLE = """\
**Quando:** agente terminou trabalho e deve liberar slot.

**Faz:** marca agent_role como idle e tenta drenar 1 item da fila.
"""

# --- Board ---

LOAD_TASKS_TOOL = """\
**Quando:** listar backlog ou inspecionar status de várias tasks.

**Faz:** carrega tasks do CSV + status do board (limitado).

**Retorna:** id, title, agent_role, board_status, sprint, depends_on.

**Parâmetros:** limit (1–200, padrão 50).
"""

PICK_TASK_TOOL = """\
**Quando:** creator/orchestrator precisa da próxima task elegível.

**Faz:** scoring do task_router — respeita depends_on, sprint e status.

**Parâmetros:**
- agent_role: papel do agente (ex: frontend-mobile, qa-gate)
- sprint: sprint atual (padrão 1)

**Retorna:** task elegível ou null se nenhuma disponível.
"""

# --- Handoff / history ---

GET_HANDOFF = """\
**Quando:** SEMPRE no início de uma fase (antes de codar, revisar ou testar).

**Faz:** lê handoff JSON em `agents/00-runtime/output/handoffs/{task_id}.json`.

**Contém:** from_agent, to_agent, event, status, summary, pr_url, deliverables.

**Se ausente:** não avance — peça handoff ou rode fase anterior.
"""

WRITE_HANDOFF_TOOL = """\
**Quando:** passar trabalho para outro agente ou registrar entrega.

**Faz:** grava/atualiza handoff JSON da task.

**Parâmetros obrigatórios:** task_id, from_agent, to_agent, event, status.
**Opcionais:** summary, pr_url.
**dry_run:** true (padrão) mostra payload; false grava.

**Não use** para status do board — use `emit_status_event`.
"""

APPEND_TASK_ACTION_TOOL = """\
**Quando:** após cada passo ReAct (pensar → agir → observar).

**Faz:** append no histórico da task (auditoria + trace para orchestrator).

**Campos obrigatórios:**
- thought: raciocínio curto (o que decidiu e por quê)
- action: tool/comando executado (nome + args resumidos)
- observation: resultado lido da tool (ok/erro, paths, métricas)

**Opcionais:** from_status, to_status, focus (ponto da execução), model, tokens_*.

**dry_run:** true (padrão) simula; false persiste no histórico.
"""

# --- Dispatch ---

DISPATCH_JOB_TOOL = """\
**Quando:** despachar job worker (Cursor SDK). Raro — requer flag de ambiente.

**Pré-requisito:** GUARDIAO_MCP_ALLOW_DISPATCH=1.

**Parâmetros:** job_id (da fila worker), dry_run (padrão true).
"""

# --- Mobile RAG ---

QUERY_MOBILE_FLOW_RAG = """\
**Quando:** antes de implementar (frontend-mobile) ou planejar QA (qa-gate).

**Faz:** busca semântica em fluxos mobile (telas, labels, passos 0→N) no Postgres pgvector.

**Como formular query:**
- Inclua task_id ou nome da tela (ex: "ChildHomeV2 greeting header T-P3-009")
- Mencione app (parent/child), ação do usuário e elemento alvo

**Parâmetros:**
- query: texto de busca (obrigatório)
- app_id: filtrar app (parent | child | vazio=todos)
- chunk_type: filtrar tipo de chunk (screen | step | vazio=todos)
- top_k: hits retornados (1–15, padrão 5)

**Retorna:** hits + user_flow sintetizado (telas, arquivos, rota).

**Se falhar:** rode `ingest_mobile_flow_rag` e verifique DATABASE_URL + pgvector.
"""

INGEST_MOBILE_FLOW_RAG = """\
**Quando:** manutenção do índice RAG (qa-author ou setup inicial).

**Faz:** ingere mobile_user_flows.db → agent_mobile_flow_chunks (pgvector).

**Parâmetros:**
- discover_first: true roda discovery antes de ingerir
- fake_embed: true usa embeddings fake (dev sem API)
- dry_run: true (padrão) mostra plano; false executa

**Não use** em loop de QA normal — só manutenção.
"""

# --- QA mobile ---

QA_DB_SEED = """\
**Quando:** início do QA mobile — criar dados de teste sem cadastro manual.

**Faz:**
1. Bootstrap API (Docker Postgres/Redis) se bootstrap_api=true
2. Cria família + filho + código de pareamento no Postgres
3. Gera `stage-handoff.json` no mobile-setup (retoma Appium do lastStep)
4. Salva cache em `agents/00-runtime/output/mobile/qa_seed_cache/{task_id}.json`

**Profiles:**
| profile | resume_after_step | uso |
|---------|-------------------|-----|
| pairing_warm | — | pairing completo do zero |
| child_home | paste_code_parent | QA na home child (mais comum) |
| permissions_resume | allow_permissions | só permissões + home |

**Parâmetros:**
- task_id: obrigatório (ex: T-P3-009)
- profile: vazio usa child_home; ou valor da issue qa.db_seed
- use_task_config: true lê qa.db_seed do CSV/issue; false usa defaults
- bootstrap_api: true sobe stack API se necessário
- dry_run: true (padrão) mostra plano; **false executa de fato**

**Pré-requisitos:** Docker, mobile-setup configurado, variáveis API.

**Próximo passo:** `qa_appium_suite_child(from_db_seed=true, task_id=...)`.
"""

QA_DB_CLEANUP = """\
**Quando:** APÓS capturar evidências QA — sempre ao final (se cleanup=true na task).

**Faz:** purge usuários de teste no Postgres + reset stage-handoff.json + remove cache seed.

**Parâmetros (um dos identificadores):**
- task_id: preferido — usa cache do último qa_db_seed
- handoff_path: caminho explícito ao JSON
- parent_email: fallback se handoff tiver só email

**dry_run:** true (padrão) simula; false executa purge.

**Não rode** antes das evidências — só no final do ciclo QA.
"""

QA_APPIUM_SUITE_PARENT = """\
**Quando:** QA no app parent (guardiao-familia-parent) ou infra parent isolada.

**Faz:** executa `fast-stack.ps1` no mobile-setup:
API → emulator-5554 → Metro 8082 → build → APPS_READY → Appium (opcional).

**Modos:**
| flags | comportamento |
|-------|---------------|
| padrão (skip_appium=true) | só infra, sem testes Appium |
| from_db_seed=true | retoma handoff pós-seed, abre ParentHome, skip_appium=false auto |
| skip_build=true | pula rebuild (mais rápido em dev) |

**Parâmetros:**
- phase: Smoke (padrão) | Regression
- feature: create_account | pairing | go_to_home_parent (vazio=auto com from_db_seed)
- from_db_seed + task_id: usa handoff do qa_db_seed
- timeout_sec: padrão 1800 (30 min)

**dry_run:** true mostra comando/flags; false executa (longo, bloqueante).

**Sucesso:** ok=true, apps_ready=true, markers APPS_READY_OK / SMOKE_PARENT_OK.
"""

QA_APPIUM_SUITE_CHILD = """\
**Quando:** QA no app child (guardiao-familia-child) — caso mais comum do qa-gate.

**Faz:** executa `fast-stack.ps1` dual-emulator:
API → emulator-5554 (parent) + 5556 (child) → Metro 9090 → build → APPS_READY → Appium.

**Modo recomendado (pós-seed):**
```
qa_db_seed(task_id="T-P3-009", profile="child_home", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="T-P3-009", feature="pairing", dry_run=false)
```

**O que from_db_seed faz:**
- Lê handoff do seed (lastStep, childHome)
- Define feature automaticamente (pairing | go_to_home_child)
- skip_appium=false, dual emulator, GF_SKIP_DB_CLEANUP=1
- Retoma Appium após paste_code_parent → ChildHome

**Parâmetros:**
- from_db_seed: true após qa_db_seed (obrigatório para fluxo seed→suite)
- task_id: mesmo do seed (cache handoff)
- feature: pairing (padrão) | go_to_home_child — vazio=auto com from_db_seed
- phase: Smoke (padrão)
- skip_build: true (padrão, mais rápido)
- resume_from_handoff: legado — prefira from_db_seed
- timeout_sec: 1800

**Emulador alvo QA:** emulator-5556 (child). Parent em 5554 para pairing.

**Após suite:** ajuste hora via adb, screenshots header, MP4 por cenário.
Evidências: `agents/00-runtime/output/mobile/qa_evidence/{task_id}/`

**dry_run:** true valida flags; false executa (15–30 min).

**Sucesso:** ok=true, apps_ready=true, markers APPIUM_OK / SMOKE_CHILD_OK.

**Próximo:** evidências → qa_db_cleanup → emit_status_event(test_passed|test_failed_bug).
"""

LIST_MCP_TOOLS = """\
**Quando:** início de sessão ou dúvida sobre catálogo.

**Faz:** lista todas as tools com grupo (gateway, board, handoff, qa_mobile, …) e flag writes.

**Use** antes de inventar comandos CLI alternativos.
"""
