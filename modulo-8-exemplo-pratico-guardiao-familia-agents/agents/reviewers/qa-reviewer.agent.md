# Agente Revisor: QA

**qa-reviewer** — par de `qa`.

Skill: `skills/qa-reviewer/SKILL.md`

Valida cenarios E2E criticos e CI.

## Board

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Assume | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Trigger: **Ready for Code Review** + `agent:qa`. Finaliza: `--creator qa --finalize`.
