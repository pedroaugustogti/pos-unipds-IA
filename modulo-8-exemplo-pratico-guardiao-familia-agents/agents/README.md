# Agentes — Guardião Família (módulo 8)

Prompts Cursor/Automation. Workflow: [docs/operacao/WORKFLOW_BOARD.md](../docs/operacao/WORKFLOW_BOARD.md).

Índice de comportamento: [docs/comportamento/README.md](../docs/comportamento/README.md).

| Arquivo | Papel |
|---------|-------|
| backend.agent.md | Creator backend (ReAct + HITL) |
| frontend-*.agent.md | Creators front |
| cloud-infra / database / devops / stores | Creators infra |
| qa-author.agent.md | Escreve harness |
| qa-gate.agent.md | Gate Ready for Test |
| qa.agent.md | Ponte legado → author/gate |
| reviewers/* | Revisores (proposta em alto risco) |

```powershell
python scripts/agent_orchestrator.py --agent backend --claim --json
python scripts/gateway_cli.py --task T-XXX --event open_pr --dry-run
```
