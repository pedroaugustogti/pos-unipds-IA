# Contexto compartilhado dos agentes

Documentos lidos por **todos** os papéis antes de agir.

| Arquivo | Conteúdo |
|---------|----------|
| `STATEGRAPH_FLOW.md` | Nós LangGraph e transições de Status |
| `REPOS_AND_ROUTING.md` | Mapa repo → agent_role, paths locais |
| `WORKFLOW_BOARD.md` | Pipeline de status, eventos e papéis (Project + CSV) |
| `MCP_TOOLS.md` | Catálogo de tools MCP e dry_run |
| `REPO_KNOWLEDGE.md` | Digest de todos os READMEs do módulo 8 |

## Decisões

- Nunca alterar Status fora de `emit_status_event`
- Roteamento de task: `board_automation.board.task_router` + CSV
- Repositório de produto ≠ este módulo (só orquestração)
