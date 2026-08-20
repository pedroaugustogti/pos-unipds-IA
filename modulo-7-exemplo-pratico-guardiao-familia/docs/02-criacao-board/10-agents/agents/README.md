# Definições de agentes autônomos

Cada arquivo abaixo é um **prompt completo** para Cursor Agent ou Automation. Copie o conteúdo do `.agent.md` correspondente.

**Workflow board (obrigatório):** [WORKFLOW_BOARD.md](WORKFLOW_BOARD.md) · [AGENT_BOARD_STAGES.md](../../11-workflow/AGENT_BOARD_STAGES.md)

| Arquivo | Agente | Trigger sugerido |
|---------|--------|------------------|
| [backend.agent.md](backend.agent.md) | Backend NestJS | schedule 2h / label `agent:backend` |
| [frontend-mobile.agent.md](frontend-mobile.agent.md) | Mobile Expo/RN | schedule 2h |
| [frontend-web.agent.md](frontend-web.agent.md) | Web Next/HTML | schedule 4h |
| [cloud-infra.agent.md](cloud-infra.agent.md) | AWS/Terraform | schedule 4h |
| [database.agent.md](database.agent.md) | PostgreSQL/Redis | on-demand |
| [devops-cicd.agent.md](devops-cicd.agent.md) | CI/CD | on-demand |
| [qa.agent.md](qa.agent.md) | Testes | após PR dev |
| [stores-release.agent.md](stores-release.agent.md) | Stores | sprint 11+ |

## Execução local

```powershell
## Como rodar um agente

```powershell
cd docs/02-criacao-board/10-agents

# Seleciona task com board_status==Todo (github-project-2-import.json)
python ../scripts/agent_orchestrator.py --agent backend --json

# Claim: Status In Progress no JSON local + Project #2 (gh)
python ../scripts/agent_orchestrator.py --agent backend --claim --json

# Transicao por evento
python ../scripts/task_status_cli.py --task T-P05-001 --event open_pr --json
```

Requer `gh` no PATH (ou `GH_PATH`) e `GITHUB_TOKEN` / `CURSOR_GITHUB_TOKEN` para o Project online.

## Observabilidade

```powershell
python ../scripts/observability_cli.py --summary --dashboard
python ../scripts/observability_cli.py --open
```

Dashboard: `../crew/output/observability/dashboard.html`
```

Depois invoque o Cursor Agent colando o prompt do `.agent.md` desejado.
