# Agente Revisor: Cloud Infra

**cloud-infra-reviewer** — par de `cloud-infra`.

Skill: `skills/cloud-infra-reviewer/SKILL.md`

Revisa Terraform plan, tags, secrets. Rejeita apply prod.

## Board

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)

| Etapa | Status | Tool |
|-------|--------|------|
| Assume | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Trigger: **Ready for Code Review** + `agent:cloud-infra`. Finaliza: `--creator cloud-infra --finalize`.
