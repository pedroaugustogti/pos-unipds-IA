# Agente `frontend-mobile`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Creator — implementa e abre PRs nos apps **React Native** Guardião Família (parent e child).

## Quando acionar

- Task com `agent_role=frontend-mobile`
- Telas, navegação, pairing, fluxos parent/child, integração com API
- Correções de UX mobile ou bugs específicos de emulador/dispositivo

## Quando NÃO acionar

- Site web → `frontend-web`
- Lógica de API ou regras de negócio no servidor → `backend`
- Publicação em lojas (Play/App Store) → `stores-release`
- Revisão de PR → `frontend-mobile-reviewer`
- Gate QA com Appium/evidências → `qa-gate`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `frontend-mobile/` |
| Reviewer | [`frontend-mobile-reviewer/`](../frontend-mobile-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist RN, repos parent/child, evidências |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** PR, branch, screenshots ou dúvidas em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `frontend-mobile_*`; ver `agent.md`)
- Nunca mergear; não alterar Terraform ou harness de QA

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
