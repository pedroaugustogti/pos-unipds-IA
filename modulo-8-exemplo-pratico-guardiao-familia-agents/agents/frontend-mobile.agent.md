# Agente Autônomo: Frontend Mobile

Você é o **agent-frontend-mobile** (apps parent e child).

## Skill

`modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/10-agents/skills/frontend-mobile/SKILL.md`

## Task

```powershell
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent frontend-mobile --json
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent frontend-mobile --claim --json
```

Filtro: `agent_role=frontend-mobile`, `board_status == Todo` (`github-project-2-import.json`).
Claim atualiza JSON local + Project #2 via `gh`.

## Board

Ver [WORKFLOW_BOARD.md](WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Claim | **In Progress** | `claim_task_on_board` |
| PR aberto | **Ready for Code Review** | `mark_task_in_review` |
| CR pediu mudanças | **In Progress** | aguardar revisor |
| Correção reenviada | **In Code Review** | `resubmit_after_review` |

Labels: `agent:frontend-mobile`, `agent:in-progress` / `agent:ready-for-cr`

## Repos

| Task repo | Path |
|-----------|------|
| guardiao-familia-parent | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent` |
| guardiao-familia-child | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child` |

Branch base: `master`

## PR estratégico

Template: `10-agents/templates/PR_TEMPLATE.md`

Obrigatório documentar:
- Plataforma (iOS/Android/both)
- Permissões alteradas
- Estratégia de implementação
- Arquivos alterados
- Dúvidas (ex.: comportamento background location, sons push)

## Commit

`feat({task_id}): {descrição}`

## Coordenação

Se precisar endpoint novo → comentar issue tag `agent:backend` antes do merge.

Reporte final: task_id, repo, PR URL, platform, dúvidas.
