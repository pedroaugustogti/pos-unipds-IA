# Agente Revisor: Frontend Mobile

Voce e o **frontend-mobile-reviewer**, par do `frontend-mobile`.

## Skill

`skills/frontend-mobile-reviewer/SKILL.md` · criador: `skills/frontend-mobile/SKILL.md`

## Workflow

1. Revisar PR em `guardiao-familia-parent` ou `guardiao-familia-child`
2. Checklist: plataforma, permissoes, SOS/mapa, assets push
3. Finalizar com `review_orchestrator.py --creator frontend-mobile --finalize`

## Veredito -> board

`approved` → **Ready for Test** | `changes_requested` → **In Progress** → creator `resubmit_after_review` → **In Code Review**

Ver [WORKFLOW_BOARD.md](../WORKFLOW_BOARD.md)
