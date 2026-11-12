# Skills e plugins úteis no Capstone

Alinhado à aula 2 (`CLAUDE.md` + AI Dev Skills) e ao restante do roteiro.

## Precedência (regra da disciplina)

1. Skill **oficial** do framework (Angular, LangGraph, Langfuse…)  
2. Skill **local** do projeto (seed)  
3. Prompt solto  

## Mapa skill → aula

| Skill / plugin | Aulas | Automatiza |
|----------------|-------|------------|
| `CLAUDE.md` do seed | 2, todas | Regras: perguntar antes de deps/schema |
| `frontend-design` | 18 | Do mock ao código UI |
| Angular CLI skill / MCP | 7, 18–20 | Components, routes, standalone |
| LangGraph skill (se disponível) | 9–13 | Nós retrieve/grade/answer |
| Langfuse skill / docs MCP | 22–23 | Instrumentação e leitura de traces |
| Mermaid / docs skill | 24 | Diagramas no README |
| GitHub skill / MCP | 4, 7, 21 | Workflows, PR, checks |

## Plugins Cursor / Claude Code

| Plugin | Uso |
|--------|-----|
| MCP GitHub | Já no monorepo |
| MCP Playwright | Browser + E2E assistido |
| MCP Angular | Scaffold no `apps/web` |
| Google MCP (Cloud Run / SQL / gcloud) | Inventário cloud (HITL em create) |
| langfuse-mcp | Debug de spans |

## O que versionar no seed

```
CLAUDE.md
.claude/skills/   ou  .cursor/skills/
.mcp.json         # opcional — servers do projeto
```

Não versionar: API keys, JSON de service account, `.env` com secrets.
