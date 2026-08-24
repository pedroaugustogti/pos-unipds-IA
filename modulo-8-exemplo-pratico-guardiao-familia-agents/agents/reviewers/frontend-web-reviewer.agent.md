# Agente Revisor: Frontend Web

**frontend-web-reviewer** — par de `frontend-web`.

Skill: `skills/frontend-web-reviewer/SKILL.md`

Revisa backoffice/site; valida auth guards, LGPD links, responsivo.

## Board

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Assume | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Creator corrige → `resubmit_after_review` → **In Code Review**

Trigger: **Ready for Code Review** + `agent:frontend-web`. Finaliza: `--creator frontend-web --finalize`.
