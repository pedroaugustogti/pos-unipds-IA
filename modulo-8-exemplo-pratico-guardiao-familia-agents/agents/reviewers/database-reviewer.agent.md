# Agente Revisor: Database

**database-reviewer** — par de `database`.

Skill: `skills/database-reviewer/SKILL.md`

Revisa migrations, indices, rollback.

## Board

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Assume | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Trigger: **Ready for Code Review** + `agent:database`. Finaliza: `--creator database --finalize`.
