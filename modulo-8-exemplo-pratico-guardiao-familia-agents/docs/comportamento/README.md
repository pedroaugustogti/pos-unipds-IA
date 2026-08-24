# Comportamento dos agentes (índice)

Os **prompts de runtime** e **skills** permanecem em `agents/` e `skills/` (carregados por scripts/Cursor).  
Este índice só organiza a leitura acadêmica/operacional.

## Creators (`agents/`)

| Arquivo | Papel |
|---------|-------|
| [backend.agent.md](../../agents/backend.agent.md) | Backend |
| [frontend-mobile.agent.md](../../agents/frontend-mobile.agent.md) | Mobile parent/child |
| [frontend-web.agent.md](../../agents/frontend-web.agent.md) | Web |
| [database.agent.md](../../agents/database.agent.md) | Database |
| [cloud-infra.agent.md](../../agents/cloud-infra.agent.md) | Cloud / Terraform |
| [devops-cicd.agent.md](../../agents/devops-cicd.agent.md) | CI/CD / observabilidade |
| [stores-release.agent.md](../../agents/stores-release.agent.md) | Stores / release |
| [qa-author.agent.md](../../agents/qa-author.agent.md) | Escreve harness |
| [qa-gate.agent.md](../../agents/qa-gate.agent.md) | Gate de teste na pipeline |
| [qa.agent.md](../../agents/qa.agent.md) | Ponte legado author/gate |

## Reviewers (`agents/reviewers/`)

Ver [agents/reviewers/README.md](../../agents/reviewers/README.md).

## Skills (`skills/*/SKILL.md`)

Cada role tem skill creator e, quando aplicável, `*-reviewer`.  
Fonte de verdade operacional para fronteiras de código.

## Workflow e operação (docs)

- [ESTADO_ATUAL_FLUXO_E_PROCESSO.md](../autonomia/ESTADO_ATUAL_FLUXO_E_PROCESSO.md)
- [WORKFLOW_BOARD.md](../operacao/WORKFLOW_BOARD.md)
- [PROCESSO_HITL.md](../operacao/PROCESSO_HITL.md)
- [RELATORIO_OPERACAO_AGENTES.md](../operacao/RELATORIO_OPERACAO_AGENTES.md)
- [CLASSIFICACAO_TASKS.md](../operacao/CLASSIFICACAO_TASKS.md)
