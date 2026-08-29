# Você é o **agent-qa** legado

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Este arquivo aponta para a separação do módulo 8:

- **Criação de harness / cenários:** [../qa-author/agent.md](../qa-author/agent.md) → `./SKILL.md`
- **Gate da pipeline (Ready for Test):** [../qa-gate/agent.md](../qa-gate/agent.md) → `../qa-gate/SKILL.md`
- **Revisor de harness:** [../qa-author-reviewer/agent.md](../qa-author-reviewer/agent.md) → `../qa-author-reviewer/SKILL.md`

**MCP:** catálogo em [`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) — qa-author usa RAG; qa-gate usa tools `qa_*` + gateway.

Não use um único processo para claimar Todo de QA e ao mesmo tempo drenar a fila de teste.