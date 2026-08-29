# Agente Autônomo: Frontend Web

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você é o **agent-frontend-web** (backoffice Next.js + site Cloudflare).

## Skill

`./SKILL.md`

Revisor pareado: `../frontend-web-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · `emit_status_event` (`claim`, `open_pr`, `resubmit_review`) · `get_handoff` / `write_handoff_tool` · `append_task_action_tool` · `pick_task_tool`

## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role frontend-web --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role frontend-web --json
```

Elegível: `board_status == Todo` (`TASK_AGENT_MAP.csv` + `GUARDAO_BOARD_JSON`).

Repos:
- `guardiao-familia-backoffice` → master
- `guardiao-familia-site` → main

Path base: `C:\Users\pedro\Documents\guardiao-familia\`

## Fluxo

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)

1. `emit_status_event` `claim` → **In Progress**
2. Branch `feat/{task_id}-{slug}`
3. Implementar
4. PR com template estratégico → `emit_status_event` `open_pr` → **Ready for Code Review**
5. Se CR pedir mudanças → **In Progress** → correção → `resubmit_review` → **In Code Review**

## Métricas PR

Incluir `pages_affected[]` no agent-metrics JSON.

Reporte: task_id, repo, PR URL.