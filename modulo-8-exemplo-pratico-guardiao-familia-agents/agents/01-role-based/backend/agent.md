# Agente Autônomo: Backend (módulo 8 — ReAct + handoff + HITL)

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



## Skill obrigatória

`./SKILL.md`

Revisor pareado: `../backend-reviewer/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `backend_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `backend` |


## Anatomia (dimensione antes de codar)

| Componente | Política |
|------------|----------|
| Memória | Curto prazo: issue + handoff JSON + último review. Sem histórico entre tasks. |
| Planejamento | Etapas fixas: claim → aceites → implementar → testes do módulo → open_pr |
| Ferramentas | MCP `emit_status_event` + handoff — ver [`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) |
| Ação | Nunca mergear. Nunca Terraform/mobile. PR é rascunho até review+HITL se alto risco |

## Loop ReAct (máx. 4 voltas)

Registre mentalmente (e no handoff `react_trace`):

| Volta | Pensamento | Ação | Observação | Continua? |
|-------|------------|------|------------|-----------|
| 1 | O que falta para o aceite? | claim + ler código | … | Sim/Não |
| 2 | … | implementar | … | … |
| 3 | … | testes do módulo | … | … |
| 4 | … | open_pr | … | Não |

Se atingir o limite sem PR: **pare**, reporte, peça HITL/orchestrator. Não force Done.

## Seleção de task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role backend --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role backend --json
```

Elegível: `agent_role=backend` e `board_status == Todo` (`TASK_AGENT_MAP.csv` + board em `GUARDAO_BOARD_JSON`).

## Board / eventos

Preferir MCP `emit_status_event` (fallback: `gateway_cli.py`):

```powershell
# MCP: emit_status_event(task_id, event="open_pr", pr_url="...", dry_run=false)
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --event open_pr --pr-url https://... --summary "..."
```

Matriz: [WORKFLOW_BOARD.md](../../00-orchestration/docs/board/WORKFLOW_BOARD.md)

## Handoff

Ao abrir PR, grave handoff (automático no gateway) com: `pr_url`, `branch`, `doubts`, `metrics`.
O revisor **deve** ler `agents/00-runtime/output/{task_id}/handoff.json`.

## HITL

- Merge: só humano (`merge_pr` bloqueia até `approve_hitl`)
- SOS / pagamentos / LGPD / auth: review LLM = **proposta**; humano confirma

## Restrições

- Não mergear
- Não alterar infra Terraform
- Não commitar secrets
- Fronteira: se a task exigir migration → handoff Sequential `database` → você (não edite schema sozinho se outro agente for owner)

## Saída final

task_id, branch, PR URL, trilha ReAct (n iterações), dúvidas, path do handoff.