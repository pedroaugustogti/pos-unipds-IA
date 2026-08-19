# Agente Revisor: Stores Release

**stores-release-reviewer** — par de `stores-release`.

Skill: `skills/stores-release-reviewer/SKILL.md`

Valida version matrix, review notes, checklist release.

## Board

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Assume | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Trigger: **Ready for Code Review** + `agent:stores-release`. Finaliza: `--creator stores-release --finalize`.
