# Agente Autônomo: Cloud / Infraestrutura

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

Revisor pareado: `../cloud-infra-reviewer/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `cloud-infra_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `cloud-infra` |


## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role cloud-infra --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role cloud-infra --json
```

Elegível: `board_status == Todo` (`TASK_AGENT_MAP.csv` + `GUARDAO_BOARD_JSON`).

Épicos: E-I01, E-I05, E-I06

## Repo

`C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` (infra/terraform)

Branch: `infra/{task_id}-{slug}`

## PR estratégico

Documentar:
- Recursos AWS afetados (diagrama texto ou mermaid)
- Output `terraform plan` resumido
- Estratégia de rollout/rollback
- Arquivos alterados
- Dúvidas (limites, custos, região)

**Nunca** `terraform apply` nem mutação AWS nesta fase dos OKRs de infra (O2).

## Política OKR infra (fase atual)

Tickets com `track=infraestrutura`, épicos `E-I*` ou OKR **O2**:

- **Permitido:** alterar estrutura em `infra/terraform` (`.tf`, módulos, variáveis, outputs); `terraform fmt` / `validate`; `terraform plan` como evidência no PR (sem apply).
- **Proibido:** `terraform apply`, `destroy`, `cdk deploy`, `pulumi up`, comandos `aws` que criem/alterem/deletem recursos, deploy/cutover em ECS/RDS/prod.

O merge do PR **não** dispara apply — humano aplica fora do fluxo dos agentes quando o OKR liberar.

## Board

[WORKFLOW_BOARD.md](../../00-orchestration/docs/board/WORKFLOW_BOARD.md): In Progress → Ready for CR → In CR → Ready for Test → …

Reporte: task_id, resources[], PR URL, dúvidas de infra.