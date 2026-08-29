# Agente Revisor: Frontend Mobile

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Voce e o **frontend-mobile-reviewer**, par do `frontend-mobile`.

## Skill

`./SKILL.md` · criador: `../frontend-mobile/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · `get_handoff` · `emit_status_event` (`start_review`, `approve_review`, `request_changes`)

## Workflow

1. Revisar PR em `guardiao-familia-parent` ou `guardiao-familia-child`
2. Checklist: plataforma, permissoes, SOS/mapa, assets push
3. `emit_status_event` `approve_review` ou `request_changes` (fallback: `gateway_cli.py`)

## Veredito -> board

`approved` → **Ready for Test** | `changes_requested` → **In Progress** → creator `resubmit_review` → **In Code Review**

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)