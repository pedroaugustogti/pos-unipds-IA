# Agente Autônomo: DevOps / CI/CD

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

`./SKILL.md`

Revisor pareado: `../devops-cicd-reviewer/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `devops-cicd_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `devops-cicd` |


## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role devops-cicd --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role devops-cicd --json
```

Elegível: tasks devops com `board_status == Todo`, ou fila de merge `In Pull Request` (trilha ≠ stores). Status via JSON + `gh`.

Épicos E-I02, E-I03

## Escopo

- `.github/workflows/` — build, test, **ECR push, ECS deploy Fargate**
- OIDC GitHub → AWS (sem keys estáticas prod)
- Observabilidade ECS (logs, metrics, OTel)
- Sentry, alertas PagerDuty

Branch: `ci/{task_id}-{slug}`

Backlog ativo: `docs/operacao/BACKLOG_INFRA_FARGATE.csv` (onda **T-I08-***).

## PR estratégico

- Workflows alterados e triggers
- Secrets necessários (nomes only)
- Como validar pipeline
- Dúvidas (runners, permissões org)

Reporte: task_id, test_files[], scenarios_count, PR URL.

## Workflow board (merge)

Ver [WORKFLOW_BOARD.md](../../00-orchestration/docs/board/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Após QA pass | **In Pull Request** | (entrada automática) |
| Merge concluído | **Done** | `merge_pr` (+ `approve_hitl` humano) |

Trilha **stores** → preferir `stores-release` como owner merge.