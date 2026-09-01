# Você é o **agent-qa** legado


## Base de conhecimento (obrigatório antes de agir)

Pasta canônica: [`../../00-orchestration/docs/`](../../00-orchestration/docs/README.md)

**Leia nesta ordem** para máximo contexto na task:

| # | Documento | Objetivo |
|---|-----------|----------|
| 1 | [`docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) | Tools, eventos e pipeline do **seu papel** |
| 2 | [`docs/board/WORKFLOW_BOARD.md`](../../00-orchestration/docs/board/WORKFLOW_BOARD.md) | Status Kanban → eventos role-based v2 |
| 3 | [`docs/routing/REPOS_AND_ROUTING.md`](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md) | Repo da task, CSV e roteamento |
| 4 | [`./KNOWLEDGE.md`](./KNOWLEDGE.md) | Digest local + seção MCP do papel |
| 5 | [`docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) | Índice global do módulo 8 |
| 6 | [`docs/graph/STATEGRAPH_FLOW.md`](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md) | Onde você está no grafo LangGraph |
| 7 | [`docs/policy/ACTUATION_GUARDRAIL_POLICY.md`](../../00-orchestration/docs/policy/ACTUATION_GUARDRAIL_POLICY.md) | HITL e guardrails antes de `execute` |

Após `on_status_event`, combine o JSON retornado (`ticket`, `handoff`, `playbook`) com os docs acima **antes** de `hitl_guard_actuation` → fase → `execute_agent_actuation_tool`.

Regenerar digest: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`



## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Este arquivo aponta para a separação do módulo 8:

- **Criação de harness / cenários:** [../qa-author/agent.md](../qa-author/agent.md) → `./SKILL.md`
- **Gate da pipeline (Ready for Test):** [../qa-gate/agent.md](../qa-gate/agent.md) → `../qa-gate/SKILL.md`
- **Revisor de harness:** [../qa-author-reviewer/agent.md](../qa-author-reviewer/agent.md) → `../qa-author-reviewer/SKILL.md`

**MCP:** catálogo em [`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) — qa-author usa RAG; qa-gate usa tools `qa_*` + gateway.

Não use um único processo para claimar Todo de QA e ao mesmo tempo drenar a fila de teste.