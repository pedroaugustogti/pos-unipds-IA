"""Prompts MCP para orientar a LLM — descrições objetivas por tool."""

SERVER_INSTRUCTIONS = """\
Servidor MCP do Guardião Família (módulo 8). Siga estas regras em TODA sessão:

## Regras obrigatórias
1. **Use SOMENTE tools MCP** deste servidor (`list_mcp_tools`). **Nunca** importe CLI direto no board fora do gateway MCP.
2. **Status do board:** altere SOMENTE com `emit_status_event`. Nunca invente status.
3. **Escritas:** `dry_run=true` (padrão) para validar payload; `dry_run=false` só quando tiver certeza.
4. **HITL:** antes de **cada** `execute_agent_actuation_tool`, chame `hitl_guard_actuation` e use o `guard_pass_id` retornado.
5. **Ciclo por fase:** `on_status_event` → `hitl_guard_actuation` → tool de fase → `execute_agent_actuation_tool` (ou `emit_status_event` se orquestrar manualmente).

## Anti-padrões (não faça)
- Pular `on_status_event` — perde ticket, skill, handoff e playbook.
- Pular `hitl_guard_actuation` — `execute` rejeita sem `guard_pass_id`.
- Chamar `qa_db_seed` / Appium fora de `qa_validate` sem seguir a ordem da seção QA mobile.

## Fluxo por papel
| Papel | Sequência típica |
|-------|------------------|
| creator | `emit` → `on_status_event` → `hitl_guard` → **`developer_implement`** → `execute` |
| reviewer | `on_status_event` → `hitl_guard` → **`developer_review`** → `execute` |
| qa-gate | `on_status_event` → `hitl_guard` → **`qa_validate`** → `execute` |
| devops-cicd | `on_status_event` → `hitl_guard` → `execute` (fase merge leve) |
| orchestrator | `orchestrator_enter_in_progress` → ciclo acima |

## QA mobile (ordem obrigatória)
1. **task_id = ticket em execução** — use o ID da task do board; não reutilize entre execuções paralelas sem `qa_db_cleanup`.
2. **Seed de banco (`qa_db_seed`) — use somente quando a massa deve vir da API:**
   - Conta parent, família, filho e/ou pairing-code **já devem existir no Postgres** → `qa_db_seed(task_id, profile=..., dry_run=false)` (grava Postgres + `stage-handoff.json`) e depois suite com `from_db_seed=true` e o mesmo `task_id`.
   - O critério de aceite exige validar **cadastro ou configuração de família na UI do parent** → **não** chame `qa_db_seed`; execute `qa_appium_suite_parent` com `feature=create_account` ou `config_family`.
   - Seed com cadastro+família no DB e validação **somente no app child** → `qa_db_seed(profile=basic_parent|parent_home)` e depois `qa_appium_suite_child(from_db_seed=true, child_only=true)` — **obrigatório** `child_only=true`; não suba emulador/Metro do parent (5554).
3. Suite Appium conforme **app alvo** (parent ou child) e flags (`child_only`, `parent_only`, `feature`, `from_db_seed`).
   - Com seed: a suite **infere** `parent_only` ou `child_only` automaticamente — não suba emulador desnecessário.
   - Ao final de cada cenário: `reset_handoff_after=true` (padrão) zera `stage-handoff.json`; complemente com `qa_db_cleanup` para purge do DB.
4. Evidências → `agents/00-runtime/output/{task_id}/qa-gate-({cycle})/evidence/`.
5. `qa_db_cleanup(task_id, dry_run=false)` após evidências.
6. `emit_status_event(qa-gate_in_pull_request|qa-gate_return_in_progress)` com paths das evidências no summary.

Catálogo completo: `list_mcp_tools`. Detalhes: `agents/_shared/MCP_TOOLS.md`.
"""

# --- Gateway / HITL ---

EMIT_STATUS_EVENT = """\
**Quando:** mover task no board Kanban (única porta de status).

**Faz:** valida evento → transição de status → atualiza board GitHub → opcionalmente handoff.

**Formato preferido (role-based):**
- Avanço: `{agent_role}_{status_slug}` — ex: `frontend-mobile_in_progress`
- Retrocesso: `{agent_role}_return_{status_slug}` — ex: `frontend-mobile-reviewer_return_in_progress`

**Forma alternativa:** `agent_role` + `board_status` (+ `return_event=true` para retrocesso) — a tool monta o evento.

**Parâmetros:**
- task_id: ID da task (ex: T-P3-009)
- event: string role-based (opcional se usar agent_role + board_status)
- agent_role + board_status: montam o evento automaticamente
- return_event: true para retrocesso (`{role}_return_{status_slug}`)
- summary: resumo curto do motivo (obrigatório em produção)
- dry_run: true (padrão) simula; false aplica
- pr_url: URL do PR (`{creator}_ready_for_code_review`)
- from_agent: papel emissor — deve bater com o prefixo do evento (orchestrator pode emitir claim do creator)

**Catálogo completo:** `list_status_events`.

**Antes de dry_run=false:** confirme handoff, AC da issue e papel correto.
"""

LIST_STATUS_EVENTS = """\
**Quando:** consultar todos os eventos role-based válidos antes de chamar `emit_status_event`.

**Faz:** retorna catálogo com event, agent_role, board_status, kind (advance|return), classification.

**Filtros opcionais:** agent_role, classification (creator|reviewer|qa-gate|ops|orchestrator).
"""

ON_STATUS_EVENT = """\
**Quando:** imediatamente após `emit_status_event` (ou antes de atuar, se o status já mudou).

**Faz:**
1. Resolve o evento role-based
2. Identifica `acting_agent` (emissor) e `assigned_agent` (quem atua no status alvo)
3. Lê o ticket no board (GitHub Project → fallback JSON)
4. Extrai `ticket` filtrado por papel: AC, escopo, arquivos, QA, merge, user_flow
5. Anexa `handoff`, `ci`, `model_tier`, `playbook` (skill, passos ReAct, hint)

**Parâmetros:** task_id + event **ou** agent_role + board_status (+ return_event).

**Retorno chave:** `assigned_agent`, `target_status`, `ticket`, `playbook`, `handoff`.

**Não altera board** — somente leitura/contexto.
"""

HITL_GUARD_ACTUATION = """\
**Quando:** obrigatório **antes de cada** `execute_agent_actuation_tool`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:**
1. Carrega policy `agents/_shared/ACTUATION_GUARDRAIL_POLICY.md`
2. Analisa ticket, handoff e playbook (prompt injection, comportamentos críticos, alto risco)
3. Calcula `importance_score` e decide `proceed` ou `blocked`
4. Se **blocked:** interrompe fluxo, enfileira HITL e comenta na issue do board (`dry_run=false`)
5. Se **proceed:** retorna `guard_pass_id` (uso único, TTL 1h)

**Parâmetros:**
- actuation_context: JSON de on_status_event (obrigatório)
- mode: dry_run | live (merge em live aumenta score)
- human_clearance: true após triagem humana no board
- clearance_note: motivo da liberação (obrigatório com human_clearance)
- dry_run: true (padrão) não comenta na issue

**Policy:** anti prompt-injection, skip tests, bypass HITL, segredos, ações destrutivas, merge live.

**Após bloqueio:** humano tria → `hitl_guard_actuation(human_clearance=true)` → novo `guard_pass_id`.
"""

EXECUTE_AGENT_ACTUATION = """\
**Quando:** imediatamente após `hitl_guard_actuation` com `proceed=true`.

**Entrada:** `actuation_context` + `guard_pass_id` (obrigatório).

**Faz:**
1. Identifica fase pelo `target_status`
2. Marca `assigned_agent` como busy
3. Executa tool de fase MCP (`developer_implement` | `developer_review` | `qa_validate`)
4. Emite próximo evento via `emit_status_event` (gateway MCP)
5. Marca agente idle

**Para LLM (Cursor):** prefira chamar a tool de fase **explicitamente** antes de `execute`, para inspecionar plano/review/AC; depois `execute` com o mesmo `actuation_context` + `guard_pass_id`.

**Mapeamento target_status → fase → emit típico:**
| target_status | fase | emit seguinte (exemplo) |
|---------------|------|-------------------------|
| In Progress | implement | `{creator}_ready_for_code_review` |
| Ready for Code Review | start_review | `{reviewer}_in_code_review` |
| In Code Review | review | `{reviewer}_ready_for_test` ou `_return_in_progress` |
| Ready for Test | start_test | `qa-gate_in_test` |
| In Test | qa | `qa-gate_in_pull_request` ou `_return_in_progress` |
| In Pull Request | merge | `devops-cicd_done` (HITL em live) |

**Parâmetros:**
- actuation_context: JSON de on_status_event (obrigatório)
- guard_pass_id: token de `hitl_guard_actuation` (obrigatório, uso único)
- mode: dry_run | live (padrão: GUARDIAO_LANGGRAPH_MODE)
- use_role_events: true emite eventos role-based

**Retorno:** phase, emit_event, board_status_out, work, apply.gateway

**Nota:** `execute` reexecuta a fase internamente se você não chamou antes. Histórico de ações é gravado pelo runtime — não existe tool MCP `append_task_action`; use `react_trace` retornado pelas tools de fase.
"""

DEVELOPER_IMPLEMENT = """\
**Quando:** fase **implement** (`target_status=In Progress`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:**
1. Carrega skill + agent.md do `assigned_agent`
2. Gera `execution_plan` (passos, arquivos, testes unitários) via LLM
3. Executa implementação (artefato/código conforme task)
4. Retorna `changed_files`, `unit_tests`, `execution_plan`

**Retorno chave:** `execution_plan`, `changed_files`, `unit_tests`, `decision.next_event={creator}_ready_for_code_review`
"""

DEVELOPER_REVIEW = """\
**Quando:** fase **review** (`target_status=In Code Review`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` de `on_status_event` (inclui handoff/PR).

**Faz:** review estruturado — boas práticas, arquitetura, manutenibilidade, cobertura de testes.

**Retorno:** `review`, `findings`, `verdict`, `decision` (`{reviewer}_ready_for_test` | `{reviewer}_return_in_progress`)
"""

QA_VALIDATE = """\
**Quando:** fase **qa** (`target_status=In Test`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` com AC e config QA do ticket.

**Faz:**
1. Sobe ambiente via MCP: `qa_db_seed` → `qa_appium_suite_*` → `qa_db_cleanup` (quando aplicável)
2. Coleta evidências e comenta na issue
3. Valida cada critério de aceite (`ac_validation`)

**Retorno:** `mcp_steps`, `evidence_paths`, `ac_validation`, `decision` (`qa-gate_in_pull_request` | `qa-gate_return_in_progress`)
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

ORCHESTRATOR_ENTER_IN_PROGRESS = """\
**Quando:** orchestrator inicia o ciclo — claim da task Todo de maior prioridade no board.

**Faz:**
1. Seleciona task em **Todo** (menor `priority_rank`; bonus sprint atual)
2. Emite `orchestrator_enter_in_progress` via `emit_status_event` (`from_agent=orchestrator`)
3. Status alvo: **In Progress** · creator: `agent_role` da task

**Parâmetros:**
- sprint / sprint_only: filtros de priorização
- task_id: opcional — força uma task Todo específica
- summary: motivo do claim
- dry_run: true (padrão) simula; false aplica no board

**Próximo passo:** `on_status_event` → `execute_agent_actuation_tool`.

**Alias semântico:** claim do orchestrator com emissor `orchestrator`. Hint: `{creator}_in_progress`.
"""

# --- Handoff / history ---

GET_HANDOFF = """\
**Quando:** SEMPRE no início de uma fase (antes de codar, revisar ou testar).

**Faz:** lê handoff JSON em `agents/00-runtime/output/{task_id}/handoff.json` (espelho legado: `handoffs/{task_id}.json`).

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
**Quando:** criar massa de teste via API (Postgres) **sem** percorrer cadastro/família na UI.

**Importante — cadastro de conta:** todos os profiles criam o parent via `POST /auth/register` (script `00-seed_app_parent`). **Nunca** insira usuários direto no Postgres — quebra a criptografia de senha e o login Appium falha.

**Não use quando:** o critério de aceite exige validar telas de cadastro ou configuração de família no app parent — nesse caso vá direto à `qa_appium_suite_parent` com o `feature` correspondente.

**Faz:**
1. Bootstrap API (Docker Postgres/Redis) se `bootstrap_api=true`
2. Via HTTP: login parent → cria família → cria filho → gera pairing-code
3. Grava `stage-handoff.json` (`lastStep` = último passo **já concluído** via API)
4. Cache em `agents/00-runtime/output/{task_id}/seed-cache.json`

**Profiles — escolha pelo estado desejado após o seed:**
| profile | lastStep no handoff | Use quando |
|---------|---------------------|------------|
| pairing_warm | null | Pairing completo do zero (UI fará cadastro+pareamento) |
| basic_parent | config_family | Cadastro API + família + 3 filhos (`00-seed_app_parent`) |
| parent_home | config_family | Parent já tem conta+família; Appium retoma em login→home |
| child_home | copy_code_pairing | Parent/família/filho/código no DB; Appium retoma no child (paste→home) |
| permissions_resume | paste_code_parent | Child já pareado; falta só permissões+ChildHome |

**Regra de infraestrutura (child):**
Se o seed já inclui cadastro parent + configuração de família **e** a validação é **somente no app child**, use na suite:
`qa_appium_suite_child(from_db_seed=true, child_only=true)` — **não** suba emulador/Metro do parent (5554).

**Parâmetros:**
- task_id: obrigatório — ID do ticket em execução
- profile: pairing_warm | basic_parent | parent_home | child_home | permissions_resume — vazio=child_home
  - **basic_parent:** seed básico via `appium/00-seed_app_parent` (cadastro API + família + 3 filhos)
- use_task_config: true lê `qa.db_seed` da task no CSV/issue (recomendado em tickets reais)
- bootstrap_api: true sobe stack API se necessário; false se API já UP
- dry_run: true (padrão) mostra plano; **false executa**

**Pré-requisitos:** Docker, `ANDROID_HOME`, mobile-setup.

**Importante:** pairing-code expira — reprovisiona automaticamente se reuse falhar.
**Próximo:** suite Appium com `from_db_seed=true` e `task_id` igual.
"""

QA_DB_CLEANUP = """\
**Quando:** APÓS capturar evidências QA — sempre ao final do ciclo.

**Faz:** purge usuários de teste no Postgres + reset stage-handoff.json + remove cache seed.

**Parâmetros:** task_id (preferido) | handoff_path | parent_email
**dry_run:** true (padrão) simula; false executa purge.
"""

QA_APPIUM_SCENARIOS = """\
## Como escolher seed + suite (decisão genérica)

Leia o critério de aceite da task e aplique:

| Objetivo do teste | Seed? | Tool | Flags obrigatórias |
|-------------------|-------|------|-------------------|
| Validar cadastro/família **na UI do parent** | **Não** | `qa_appium_suite_parent` | `feature=create_account` ou `config_family`, `skip_appium=false` |
| Parent já tem conta+família no DB; testar login→home | **Sim** `parent_home` | `qa_appium_suite_parent` | `from_db_seed=true`, `task_id`, `feature=login` (auto `parent_only=true`) |
| Child — validar **direto no app child** (home, greeting, header) | **Sim** `basic_parent` ou `parent_home` | `qa_appium_suite_child` | `from_db_seed=true`, **`child_only=true`**, `task_id` |
| Pairing parent+child (dois apps interagindo) | **Sim** `child_home` | `qa_appium_suite_child` | `from_db_seed=true`, `child_only=false`, `feature=pairing` |
| Child já pareado; só permissões+home | **Sim** `permissions_resume` | `qa_appium_suite_child` | `from_db_seed=true`, `task_id` |
| Seed básico (cadastro API + 3 filhos) | **Sim** `basic_parent` | `qa_db_seed` → suite child/parent | script `appium/00-seed_app_parent` |
| Só validar infra (API, emulador, Metro) | opcional | qualquer suite | `skip_appium=true` |

### Regras de infraestrutura
- **Child-only (padrão qa-gate para AC no app child):** seed **parent** (`basic_parent` ou `parent_home`) na API + `qa_appium_suite_child(..., child_only=true)`. Parent só no Postgres; boot **apenas** emulador child (5556) e Metro 9090.
- **Parent-only:** seed `parent_home` ou teste parent com massa no DB → `parent_only=true` (auto com `from_db_seed` no parent). Não boota emulador child (5556).
- **Dual:** pairing ou fluxo que exige parent e child simultâneos → `child_only=false` (5554+5556).
- **Handoff cleanup:** `reset_handoff_after=true` (padrão com `from_db_seed` ou `task_id`) zera `stage-handoff.json` ao final da suite — evita ruído em testes seguintes.
- **Isolamento:** 1 `task_id` por ticket; `qa_db_cleanup(task_id)` após evidências antes de outro ticket.
- **Build:** `skip_build=true` (padrão); `skip_build=false` só se o binário mudou.

### Evidências (critério de aceite)
- PNG + page-source por step: `mobile-setup/docs/appium-evidence/{step}_{timestamp}/`
- Empacotado em: `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/manifest.json`
- Cite paths no `emit_status_event(test_passed)`.

**Emuladores:** parent=5554 (Metro 8082) | child=5556 (Metro 9090)
**phase:** sempre `All`. Não use `Smoke` isolado — não boota emuladores.
**Sucesso:** markers `APPIUM_OK` ou `partial_success` (child_only com childHome atingido).
"""

QA_APPIUM_SUITE_PARENT = """\
**Quando:** validar funcionalidades no app **parent** (guardiao-familia-parent, emulator-5554, Metro 8082).

**Faz:** `fast-stack.ps1 -Single` → API → boot 5554 → Metro 8082 → build → APPS_READY → Appium.

### Quando usar (sem seed)
Critério de aceite exige percorrer telas de cadastro ou família na UI:
```
qa_appium_suite_parent(feature="create_account", skip_appium=false, dry_run=false)
qa_appium_suite_parent(feature="config_family", skip_appium=false, dry_run=false)
```
**Não** chame `qa_db_seed` — o objetivo é testar o fluxo visual.

### Quando usar (com seed)
Conta e família já existem no Postgres; testar login→ParentHome:
```
qa_db_seed(task_id="<ID_DO_TICKET>", profile="parent_home", dry_run=false)
qa_appium_suite_parent(from_db_seed=true, task_id="<ID_DO_TICKET>", feature="login", skip_appium=false, dry_run=false)
# parent_only=true é inferido automaticamente — não sobe emulador child (5556)
```

**Parâmetros:**
- phase: All (padrão) | Api | Boot | Metro | Build | Smoke
- feature: create_account | config_family | login | pairing | go_to_home_parent — vazio=auto com from_db_seed
- from_db_seed + task_id: retoma handoff do seed (emulador 5554)
- parent_only: true = só parent 5554 (auto com seed parent_home / from_db_seed)
- reset_handoff_after: true (padrão com from_db_seed/task_id) zera stage-handoff ao final
- skip_build: true (padrão)
- skip_appium: true só infra; false executa testes
- timeout_sec: 1800

**dry_run:** true valida payload; false executa.

**Sucesso:** ok=true, markers APPS_READY_OK / APPIUM_OK / SMOKE_PARENT_OK.
**Evidências:** `qa_evidence/{task_id}/` · **Cleanup:** handoff reset automático (`reset_handoff_after`) + `qa_db_cleanup(task_id)` para purge DB.

---
""" + QA_APPIUM_SCENARIOS

QA_APPIUM_SUITE_CHILD = """\
**Quando:** validar funcionalidades no app **child** (guardiao-familia-child, emulator-5556, Metro 9090).

**Faz:** fast-stack com emulador child; dual (5554+5556) **somente** se `child_only=false`.

### Child com massa parent no DB (sem subir app parent)
Seed já criou conta parent, família, filho e pairing-code. Validação é **somente no child**:
```
qa_db_seed(task_id="<ID_DO_TICKET>", profile="child_home", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="<ID_DO_TICKET>", child_only=true, skip_appium=false, dry_run=false)
```
`child_only=true` → boot **apenas** 5556; parent existe só no Postgres. Não exige `go_to_home_parent`.

### Pairing dual (parent + child simultâneos)
Fluxo exige interação entre os dois apps:
```
qa_db_seed(task_id="<ID_DO_TICKET>", profile="child_home", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="<ID_DO_TICKET>", child_only=false, feature="pairing", skip_appium=false, dry_run=false)
```

### Child já pareado (permissões + home)
```
qa_db_seed(task_id="<ID_DO_TICKET>", profile="permissions_resume", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="<ID_DO_TICKET>", skip_appium=false, dry_run=false)
```

**Parâmetros:**
- child_only: **true** = só child (auto com seed child_home/basic_parent)
- reset_handoff_after: true (padrão com from_db_seed/task_id) zera stage-handoff ao final
- from_db_seed: true após qa_db_seed
- task_id: mesmo do seed / ticket
- feature: pairing (padrão) | go_to_home_child — vazio=auto
- phase: All (padrão) · skip_build: true (padrão) · timeout_sec: 1800

**Evidências extras:** tasks com `qa.scenarios` contendo `greeting-*` geram PNG/MP4 adicionais (requer adb root).

**dry_run:** true valida flags; false executa.

**Sucesso:** ok=true ou partial_success=true com childHome no handoff.
**Próximo:** evidências → qa_db_cleanup → emit_status_event(test_passed).

---
""" + QA_APPIUM_SCENARIOS

LIST_MCP_TOOLS = """\
**Quando:** início de sessão ou dúvida sobre catálogo.

**Faz:** lista todas as tools com grupo (gateway, board, handoff, qa_mobile, …) e flag writes.

**Use** antes de inventar comandos CLI alternativos.
"""
