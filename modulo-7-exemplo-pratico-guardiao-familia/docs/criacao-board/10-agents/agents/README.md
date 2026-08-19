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
python ../scripts/agent_orchestrator.py --agent backend --dry-run
```

Depois invoque o Cursor Agent colando o prompt do `.agent.md` desejado.
