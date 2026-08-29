# Agente Revisor: Cloud Infra

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


**cloud-infra-reviewer** — par de `cloud-infra`.

## Skill

`./SKILL.md` · criador: `../cloud-infra/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · `get_handoff` · `emit_status_event` (`start_review`, `approve_review`, `request_changes`)

Revisa Terraform plan, tags, secrets. Rejeita apply prod.

## Board

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Assume | **In Code Review** | `start_review` |
| Aprovado | **Ready for Test** | `approve_review` |
| Changes | **In Progress** | `request_changes` |

Trigger: **Ready for Code Review** + `agent:cloud-infra`. Finaliza: `--creator cloud-infra --finalize`.