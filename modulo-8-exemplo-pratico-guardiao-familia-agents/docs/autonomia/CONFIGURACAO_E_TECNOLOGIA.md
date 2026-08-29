# Configuração e tecnologia dos agentes

> Atualizado: 2026-08-25  
> Par: [ESTADO_ATUAL_FLUXO_E_PROCESSO.md](ESTADO_ATUAL_FLUXO_E_PROCESSO.md) · [EXECUCAO_E_OBSERVABILIDADE.md](EXECUCAO_E_OBSERVABILIDADE.md)

---

## 1. Stack tecnológica

| Camada | Tecnologia |
|--------|------------|
| Orquestração | **LangGraph** (`agents/00-orchestration/langgraph_app/`) · CLI `agents/00-orchestration/scripts/langgraph/langgraph_run.py` |
| Eventos / Status | Python 3 · `lib/gateway` · CLI `agents/00-orchestration/scripts/cli/gateway_cli.py` |
| Tools tipadas | MCP `agents/00-orchestration/guardiao_mcp/` (Cursor) · `tools_bridge` no grafo |
| LLM orquestração | OpenRouter + `lib/model_tier.py` (`GUARDIAO_LLM_*`) |
| Implementação código | Cursor SDK (`Agent.prompt`) via `lib/dispatch_adapter.py` |
| Board remoto | GitHub Project #2 · `gh` / GraphQL |
| Board local | JSON módulo 7 |
| Observabilidade | snapshot + dashboard live + LangSmith + HTML ReAct |
| Config / runtime | `.env` + `.env.example` na raiz · `agents/00-runtime/requirements.txt` · `agents/00-runtime/output/` |

---

## 2. Como um agente está “configurado”

Cada papel tem **três camadas** (não misturar):

```text
agents/{role}/agent.md     → prompt / política Cursor (o que o agente “é”)
agents/{role}/SKILL.md     → fronteiras de código e checklist
board_automation/data/maps/TASK_AGENT_MAP.csv  → qual task esse role pode claimar
```

Reviewers: `agents/{role}-reviewer/agent.md` + `SKILL.md`, pareados em `lib/reviewer_pairs.py`.

Resolução de paths: `lib/agent_paths.py`.

Índice de leitura: [../comportamento/README.md](../comportamento/README.md).

### 2.1 Regras embutidas no código

| Módulo | Responsabilidade |
|--------|------------------|
| `task_router.py` | Elegibilidade Todo, score, sprint, roles CSV |
| `claim_lock.py` | WIP 1 por role + lock por task |
| `dependencies.py` | `depends_on` do CSV |
| `react_policy.py` | Teto de iterações ReAct + ações permitidas |
| `hitl_gates.py` | auto / propose_only / block_until_human |
| `event_schema.py` | Validação (ex.: `open_pr` exige `react_trace`) |
| `handoff.py` | Pacote between agents |
| `lib/model_tier.py` | Escolha de modelo por purpose + budget (Fase A) |

---

## 3. Variáveis de ambiente relevantes

De `.env.example` (raiz do módulo):

| Variável | Função |
|----------|--------|
| `OPENAI_API_KEY` + `OPENAI_API_BASE` | LLM via OpenRouter (LangGraph / Fase A) |
| `GUARDIAO_LLM_DEFAULT` | Modelo orquestração low-risk (alias: `CREWAI_MODEL`) |
| `GUARDIAO_LLM_HIGH` | Modelo orquestração alto risco (alias: `CREWAI_MODEL_HIGH`) |
| `GUARDIAO_LLM_ROUTE` | `deterministic` (sem LLM) ou modelo leve de roteamento |
| `GUARDIAO_CURSOR_MODEL` | Modelo Cursor SDK (código); alias legado `GUARDAO_CURSOR_MODEL` |
| `CREWAI_MODEL` | Fallback legado se `GUARDIAO_LLM_*` ausente |
| `CURSOR_API_KEY` | Dispatch Cursor Automation |
| `GUARDAO_DISPATCH_BACKEND` | `auto` \| `cursor_automation` \| `manual_fallback` |
| `GUARDAO_CURSOR_RUNTIME` | `local` \| `cloud` |
| `GUARDAO_DISPATCH_WAIT` | `1` espera Agent.prompt; `0` só bundle |
| `GUARDAO_*_PATH` | Clones locais dos repos produto |
| `GITHUB_TOKEN` / auth `gh` | Project + issues |
| `GUARDIAO_MCP_ALLOW_DISPATCH` | `1` habilita tool `dispatch_job_tool` no MCP |
| `LANGSMITH_API_KEY` | Tracing LangSmith |
| `LANGCHAIN_TRACING_V2` / `LANGCHAIN_PROJECT` | Projeto default `guardiao-familia-agents` |

MCP (Fase B): `python -m guardiao_mcp` · launcher Windows `agents/00-orchestration/guardiao_mcp/guardiao-mcp.cmd` · Cursor server `guardiao-familia-agents` (`.cursor/mcp.json`).
Sem `CURSOR_API_KEY`, o adapter cai em **manual_fallback** (bundle para colar/abrir manualmente) — o gateway de Status continua funcionando.

---

## 4. Artefatos de runtime (onde o estado vive)

```text
agents/00-runtime/output/
  orchestrator/agent_runtime.json   # agents idle/busy, hitl_queue, idempotency
  orchestrator/claim_locks.json     # WIP
  dispatch/worker_jobs.json         # fila de jobs
  handoffs/{task}.json
  dispatch/results/
  orchestrator/outbox.jsonl         # falhas gh para retry
  observability/
    snapshot.json
    dashboard.html
    workflow.jsonl
    tasks/{task}.json|.html
  demo/                             # artefatos da demo acadêmica
```

---

## 5. Integração com o Project #2

1. **Leitura / alinhamento:** `python board_automation/scripts/cli/reconcile_board.py --project-wins`  
2. **Escrita:** `lib/board_client.update_project_status` (chamado pelo fluxo de board no emit)  
3. **Falha remota:** enfileira outbox; Status **local** já aplicado (fail-open local, fail-closed no merge HITL)  
4. **Retry:** `python board_automation/scripts/cli/outbox_retry.py`

Labels `agent:*` nas issues acompanham o Status quando o cliente consegue atualizar.

---

## 6. Piloto (conjunto de tasks monitoradas)

IDs em `lib/pilot.py` (`PILOT_TASK_IDS`). O dashboard Kanban prioriza esse conjunto + cards ativos (não-Todo/Done).  
Isso é **filtro de visualização**, não limite do Project (272+ itens no remoto).

---

## 7. Demo vs produção (configuração)

| Aspecto | Demo (`demo_apresentacao.py`) | Produção / autonomia |
|---------|-------------------------------|----------------------|
| Implementação | Markdown + commit local | Cursor SDK / worker no repo |
| Conteúdo ReAct | `DEMO_ACTIONS` + overrides por task | handoff + LLM |
| HITL merge | auto-aprovado na demo | humano obrigatório |
| Histórico HTML | sempre gerado | só se `append_task_action` for chamado |
| Sync Project | sim (via gateway/board_client) | sim + outbox |

A configuração de **papéis e Status** é a mesma nos dois modos.
