# Agentes Revisores — pareados com criadores

Cada criador tem um revisor dedicado que **finaliza o PR** e **atualiza o board**.

| Criador | Revisor | Skill |
|---------|---------|-------|
| `backend` | `backend-reviewer` | [skills/backend-reviewer](../skills/backend-reviewer/SKILL.md) |
| `frontend-mobile` | `frontend-mobile-reviewer` | [skills/frontend-mobile-reviewer](../skills/frontend-mobile-reviewer/SKILL.md) |
| `frontend-web` | `frontend-web-reviewer` | [skills/frontend-web-reviewer](../skills/frontend-web-reviewer/SKILL.md) |
| `cloud-infra` | `cloud-infra-reviewer` | [skills/cloud-infra-reviewer](../skills/cloud-infra-reviewer/SKILL.md) |
| `database` | `database-reviewer` | [skills/database-reviewer](../skills/database-reviewer/SKILL.md) |
| `devops-cicd` | `devops-cicd-reviewer` | [skills/devops-cicd-reviewer](../skills/devops-cicd-reviewer/SKILL.md) |
| `qa` | `qa-reviewer` | [skills/qa-reviewer](../skills/qa-reviewer/SKILL.md) |
| `stores-release` | `stores-release-reviewer` | [skills/stores-release-reviewer](../skills/stores-release-reviewer/SKILL.md) |

## Fluxo

```
Criador (PR) -> Ready for Code Review -> Revisor -> In Code Review
  -> approved -> Ready for Test -> QA -> In Pull Request -> Done
  -> changes_requested -> In Progress -> resubmit -> In Code Review
```

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `backend-reviewer.agent.md` | Prompt Cursor/Automation |
| `scripts/review_orchestrator.py` | CLI finalize board |
| `templates/REVIEW_TEMPLATE.md` | Body padrao do review |

## CLI

```powershell
python scripts/review_orchestrator.py --creator backend --task T-P04-005
python scripts/review_orchestrator.py --creator backend --task T-P04-005 --verdict approved --finalize
```
