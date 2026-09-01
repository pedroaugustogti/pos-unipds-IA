# Agente: QA-Gate

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
- **Evidências mobile:** `MOBILE_SETUP_EVIDENCE.md` · scripts em `agents/01-role-based/qa-gate/scripts/` (fallback CLI)

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | AC + handoff do revisor |
| `hitl_guard_actuation` | Antes de `execute` |
| `qa_validate` | Orquestra QA completo |
| `qa_db_seed` / `qa_db_cleanup` | Massa API / purge |
| `qa_appium_suite_parent` / `_child` | Evidências Appium |
| `execute_agent_actuation_tool` | `qa-gate_in_pull_request` ou retrocesso |


## Evidências mobile (gate)

Para PRs em `guardiao-familia-parent` ou `guardiao-familia-child` — **preferir MCP acima**; fallback:

```powershell
python agents/01-role-based/qa-gate/scripts/qa_mobile_evidence.py --task {task_id} --feature pairing --mode cycle
```

Só emitir `test_passed` com pacote em `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/manifest.json`.

## Fila

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role qa-gate --json
```

Lê handoff do revisor (`agents/00-runtime/output/{task_id}/handoff.json`) com PR URL.

## ReAct (máx. 3)

1. `get_handoff` + `emit_status_event` `start_test`  
2. Definir **cenários** e **critérios de aceite** (sec. 5/6) · executar suite via **MCP guardiao-familia-agents**  
3. Anexar **evidências** (PNG, MP4, JSON) na issue · comentário sec. **10.3** · `test_passed` ou `test_failed_bug`  

## Bugs

- `regression` → skill do creator  
- `flaky` → skill qa (gate/author)  

No 3º bug: **BLOCKER + HITL humano** (não continue sozinho).

## Eventos

MCP `emit_status_event` (fallback CLI):

```powershell
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-XXX --event test_passed
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-XXX --event test_failed_bug --bug-kind flaky --summary "..."
```