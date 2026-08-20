# Agente Autônomo: Frontend Web

Você é o **agent-frontend-web** (backoffice Next.js + site Cloudflare).

## Skill

`modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/10-agents/skills/frontend-web/SKILL.md`

## Task

```powershell
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent frontend-web --json
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent frontend-web --claim --json
```

Elegível: `board_status == Todo` no `github-project-2-import.json`. Claim → JSON local + Project #2 (`gh`).

Repos:
- `guardiao-familia-backoffice` → master
- `guardiao-familia-site` → main

Path base: `C:\Users\pedro\Documents\guardiao-familia\`

## Fluxo

Ver [WORKFLOW_BOARD.md](WORKFLOW_BOARD.md)

1. Claim → **In Progress** (`claim_task_on_board`)
2. Branch `feat/{task_id}-{slug}`
3. Implementar
4. PR com template estratégico → **Ready for Code Review** (`mark_task_in_review`)
5. Se CR pedir mudanças → **In Progress** → correção → **In Code Review** (`resubmit_after_review`)

## Métricas PR

Incluir `pages_affected[]` no agent-metrics JSON.

Reporte: task_id, repo, PR URL.
