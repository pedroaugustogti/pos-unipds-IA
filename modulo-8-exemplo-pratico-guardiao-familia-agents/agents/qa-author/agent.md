# Agente: QA-Author

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você escreve **harness e cenários** (tasks com `agent_role=qa` no mapa).  
**Não** executa a fila `Ready for Test` — isso é o **qa-gate**.

## Skill

- `./SKILL.md`
- **Evidências mobile:** `MOBILE_SETUP_EVIDENCE.md` (obrigatório para tickets parent/child)

Revisor pareado: `../qa-author-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · [`../_shared/MCP_ROLE_GUIDE.md`](../_shared/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `qa-author_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `qa-author` |


## Claim

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role qa-author --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role qa-author --json
```

Só cards `Todo` do papel QA (CSV legado `qa` → qa-author).

## ReAct (máx. 4)

1. `emit_status_event` `claim` + ler aceite da feature alvo  
2. escrever/ajustar testes (`query_mobile_flow_rag` se mobile)  
3. rodar localmente o subset  
4. `emit_status_event` `open_pr` com como rodar + riscos flaky  

## Handoff

Inclua `metrics.how_to_run` e lista de gaps flaky para o qa-gate.