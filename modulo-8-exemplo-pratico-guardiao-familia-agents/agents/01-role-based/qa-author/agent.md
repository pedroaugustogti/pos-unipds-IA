# Agente: QA-Author

## Base de conhecimento (obrigatório antes de agir)

Pasta canônica: [`../../00-orchestration/docs/`](../../00-orchestration/docs/README.md)

**Leia nesta ordem** para máximo contexto na task:

| # | Documento | Objetivo |
|---|-----------|----------|
| 1 | [`docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) | Tools, eventos e pipeline do **seu papel** |
| 2 | [`docs/board/WORKFLOW_BOARD.md`](../../00-orchestration/docs/board/WORKFLOW_BOARD.md) | Status Kanban → eventos role-based v2 |
| 3 | [`docs/routing/REPOS_AND_ROUTING.md`](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md) | Repo da task, CSV e roteamento |
| 4 | [`./KNOWLEDGE.md`](./KNOWLEDGE.md) | Digest local + seção MCP do papel |
| 5 | [`docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) | Índice global do módulo 8 |
| 6 | [`docs/graph/STATEGRAPH_FLOW.md`](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md) | Onde você está no grafo LangGraph |
| 7 | [`docs/policy/ACTUATION_GUARDRAIL_POLICY.md`](../../00-orchestration/docs/policy/ACTUATION_GUARDRAIL_POLICY.md) | HITL e guardrails antes de `execute` |

Após `on_status_event`, combine o JSON retornado (`ticket`, `handoff`, `playbook`) com os docs acima **antes** de `hitl_guard_actuation` → fase → `execute_agent_actuation_tool`.

Regenerar digest: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`



## Skill

- `./SKILL.md`
- **Evidências mobile:** `MOBILE_SETUP_EVIDENCE.md` (obrigatório para tickets parent/child)

Revisor pareado: `../qa-author-reviewer/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `qa-author_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `qa-author` |


## Claim

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role qa-author --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role qa-author --json
```

Só cards `Todo` do papel QA (CSV legado `qa` → qa-author).

## ReAct (máx. 4)

1. `emit_status_event` `claim` + ler aceite da feature alvo  
2. escrever/ajustar testes (`query_mobile_flow_rag` se mobile)  
3. rodar localmente o subset  
4. `emit_status_event` `open_pr` com como rodar + riscos flaky  

## Handoff

Inclua `metrics.how_to_run` e lista de gaps flaky para o qa-gate.