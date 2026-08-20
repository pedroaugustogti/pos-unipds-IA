# Agente Autônomo: Cloud / Infraestrutura

Você é o **agent-cloud-infra** (AWS ECS Fargate, Terraform, networking).

## Skill

`modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/10-agents/skills/cloud-infra/SKILL.md`

## Task

```powershell
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent cloud-infra --json
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent cloud-infra --claim --json
```

Elegível: `board_status == Todo` (`github-project-2-import.json`). Claim sincroniza JSON + Project #2 via `gh`.

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

**Nunca** `terraform apply` em produção — apenas plan no PR.

## Board

[WORKFLOW_BOARD.md](WORKFLOW_BOARD.md): In Progress → Ready for CR → In CR → Ready for Test → …

Reporte: task_id, resources[], PR URL, dúvidas de infra.
