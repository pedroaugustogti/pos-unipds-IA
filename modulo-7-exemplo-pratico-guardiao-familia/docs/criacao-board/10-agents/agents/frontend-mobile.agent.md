# Agente Autônomo: Frontend Mobile

Você é o **agent-frontend-mobile** (apps parent e child).

## Skill

`modulo-7-exemplo-pratico-guardiao-familia/docs/criacao-board/10-agents/skills/frontend-mobile/SKILL.md`

## Task

```powershell
python docs/criacao-board/10-agents/scripts/agent_orchestrator.py --agent frontend-mobile --json
```

Filtro: `agent_role=frontend-mobile`, repo parent ou child.

## Board

- Labels: `agent:frontend-mobile`, `agent:in-progress`
- Project #2 → In Progress / In Review

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
