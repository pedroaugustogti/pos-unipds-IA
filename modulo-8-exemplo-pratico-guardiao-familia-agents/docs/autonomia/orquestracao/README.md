# Mapa didático da orquestração

Visão completa do fluxo Guardião Família (módulo 8): **onde cada tecnologia entra**, papéis de agentes, modelos LLM, MCP, nós LangGraph e porta única do gateway.

**Orquestração:** somente LangGraph. CrewAI removido (`crew/` = env + `output/` runtime).

## Abrir o relatório visual

| Superfície | Como |
|------------|------|
| **HTML interativo** (recomendado no browser) | Abra [`index.html`](index.html) no navegador (duplo clique ou Live Preview) |
| **Canvas Cursor** | [guardiao-orquestracao.canvas.tsx](/Users/pedro/.cursor/projects/c-Users-pedro-Documents-pos-unipds-pos-unipds-IA/canvases/guardiao-orquestracao.canvas.tsx) — abre ao lado do chat |
| **Este README** | Índice e links para os `.md` de fase |

Plugins usados no HTML (CDN, sem instalar no repo):

- [Mermaid](https://mermaid.js.org/) — diagramas de fluxo / sequência
- Tipografia sistema + CSS próprio (sem framework pesado)

## Conteúdo do HTML

1. Visão em camadas (CLI → LangGraph → LLM/MCP → gateway → board)  
2. Diagrama do StateGraph (nós e arestas condicionais)  
3. Detalhe etapa a etapa (Status Kanban × nó × evento × agente × modelo)  
4. Catálogo MCP (16 tools)  
5. Model tiers (Fase A)  
6. Modes `dry_run` / `demo` / `live`  
7. Observabilidade (HTML task + LangSmith + evals)  
8. Referências aos relatórios A–D  

## Relatórios e guias referenciados

| Doc | Papel |
|-----|--------|
| [../ESTADO_ATUAL_FLUXO_E_PROCESSO.md](../ESTADO_ATUAL_FLUXO_E_PROCESSO.md) | Status e papéis as-is |
| [../CONFIGURACAO_E_TECNOLOGIA.md](../CONFIGURACAO_E_TECNOLOGIA.md) | Stack e env |
| [../EXECUCAO_E_OBSERVABILIDADE.md](../EXECUCAO_E_OBSERVABILIDADE.md) | Como rodar / dashboard |
| [../GUIA_LANGGRAPH_MCP_LLM.md](../GUIA_LANGGRAPH_MCP_LLM.md) | Evolução LLM + MCP + LangGraph |
| [../fases/RELATORIO_FASE_A_MODEL_TIER.md](../fases/RELATORIO_FASE_A_MODEL_TIER.md) | select_model |
| [../fases/RELATORIO_FASE_B_MCP.md](../fases/RELATORIO_FASE_B_MCP.md) | MCP server |
| [../fases/RELATORIO_FASE_C_LANGGRAPH.md](../fases/RELATORIO_FASE_C_LANGGRAPH.md) | Grafo |
| [../fases/RELATORIO_FASE_D_LANGSMITH.md](../fases/RELATORIO_FASE_D_LANGSMITH.md) | Tracing + dataset estático |

## Comandos rápidos

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python scripts/langgraph_run.py --task T-P05-006 --mode dry_run --from-zero
python scripts/langsmith_eval.py
python -m guardiao_mcp   # server MCP stdio (Cursor)
```
