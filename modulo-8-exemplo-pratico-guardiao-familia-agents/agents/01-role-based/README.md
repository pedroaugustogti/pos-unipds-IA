# 01-role-based — agentes por papel

Pastas **creator**, **reviewer**, **qa-gate** e **ops** — cada `agent_role` com prompt, skill e KNOWLEDGE.

## Estrutura

```
01-role-based/
  backend/                  creator
  backend-reviewer/         reviewer pareado
  frontend-mobile/          creator
  frontend-mobile-reviewer/ reviewer
  qa-author/                creator (testes)
  qa-author-reviewer/       reviewer pareado
  qa-gate/                  gate QA (+ scripts mobile)
  ...
```

Cada pasta: `agent.md` · `SKILL.md` · `KNOWLEDGE.md` · `README.md`

## Mapa de papéis

| Tipo | Papéis |
|------|--------|
| Creator | `backend`, `frontend-mobile`, `frontend-web`, `cloud-infra`, `database`, `devops-cicd`, `stores-release`, `qa-author` |
| Reviewer | `{creator}-reviewer` (ex.: `backend-reviewer`, `qa-author-reviewer`) |
| Gate | `qa-gate` |

Roteamento repo → role: [`../00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Docs compartilhados (ler antes de agir)

Base canônica: [`../00-orchestration/docs/`](../00-orchestration/docs/README.md)

| # | Documento | Objetivo |
|---|-----------|----------|
| 1 | [`docs/mcp/MCP_ROLE_GUIDE.md`](../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) | Tools e eventos do seu papel |
| 2 | [`docs/board/WORKFLOW_BOARD.md`](../00-orchestration/docs/board/WORKFLOW_BOARD.md) | Status Kanban → eventos v2 |
| 3 | [`docs/routing/REPOS_AND_ROUTING.md`](../00-orchestration/docs/routing/REPOS_AND_ROUTING.md) | Repo da task e roteamento |
| 4 | `{role}/KNOWLEDGE.md` | Digest local do papel |
| 5 | [`docs/knowledge/REPO_KNOWLEDGE.md`](../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) | Índice global do módulo 8 |
| 6 | [`docs/graph/STATEGRAPH_FLOW.md`](../00-orchestration/docs/graph/STATEGRAPH_FLOW.md) | Posição no grafo LangGraph |
| 7 | [`docs/policy/ACTUATION_GUARDRAIL_POLICY.md`](../00-orchestration/docs/policy/ACTUATION_GUARDRAIL_POLICY.md) | HITL antes de `execute` |

## Manutenção

```bash
python agents/00-orchestration/scripts/ops/build_repo_knowledge.py
python agents/00-orchestration/scripts/ops/patch_agent_docs.py
python agents/00-orchestration/scripts/ops/patch_agent_mcp_knowledge.py
```
