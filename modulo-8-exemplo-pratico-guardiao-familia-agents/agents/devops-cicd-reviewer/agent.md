# Agente Revisor: DevOps CI/CD

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


**devops-cicd-reviewer** — par de `devops-cicd`.

## Skill

`./SKILL.md` · criador: `../devops-cicd/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · `get_handoff` · `emit_status_event` (`start_review`, `approve_review`, `request_changes`)

Revisa workflows, secrets, triggers.

## Board

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Assume | **In Code Review** | `start_review` |
| Aprovado | **Ready for Test** | `approve_review` |
| Changes | **In Progress** | `request_changes` |

Trigger: **Ready for Code Review** + `agent:devops-cicd`. Finaliza: `--creator devops-cicd --finalize`.