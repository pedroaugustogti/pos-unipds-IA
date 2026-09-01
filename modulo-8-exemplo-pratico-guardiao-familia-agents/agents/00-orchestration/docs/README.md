# docs — base de conhecimento dos agentes (v2)

Documentação **canônica** consultada pelos agentes antes de agir. Referenciada em cada `agents/01-role-based/{role}/agent.md`.

## Estrutura

```
docs/
├── README.md           ← este índice
├── graph/              LangGraph v2 — fluxo e loop de arquivos
├── mcp/                Tools MCP e guia por papel
├── board/              Kanban, status e eventos role-based
├── routing/            Repo → agent_role, paths locais
├── knowledge/          Digest global (REPO_KNOWLEDGE)
└── policy/             HITL e guardrails de atuação
```

## Índice por tema

### Grafo LangGraph — `graph/`

| Documento | Conteúdo |
|-----------|----------|
| [`STATEGRAPH_FLOW.md`](graph/STATEGRAPH_FLOW.md) | 57 nós, status→evento, pipelines MCP |
| [`NODE_LOOP_SEQUENCE.md`](graph/NODE_LOOP_SEQUENCE.md) | Sequência do loop com encadeamento de arquivos |

### MCP — `mcp/`

| Documento | Conteúdo |
|-----------|----------|
| [`MCP_TOOLS.md`](mcp/MCP_TOOLS.md) | Catálogo das 14 tools |
| [`MCP_ROLE_GUIDE.md`](mcp/MCP_ROLE_GUIDE.md) | Tools, eventos e pipeline por creator/reviewer/qa-gate/ops |

### Board — `board/`

| Documento | Conteúdo |
|-----------|----------|
| [`WORKFLOW_BOARD.md`](board/WORKFLOW_BOARD.md) | Colunas GitHub Project, eventos v2, papéis |

### Roteamento — `routing/`

| Documento | Conteúdo |
|-----------|----------|
| [`REPOS_AND_ROUTING.md`](routing/REPOS_AND_ROUTING.md) | Mapa repo → `agent_role`, CSV, paths |

### Conhecimento global — `knowledge/`

| Documento | Conteúdo |
|-----------|----------|
| [`REPO_KNOWLEDGE.md`](knowledge/REPO_KNOWLEDGE.md) | Digest de todos os READMEs do módulo 8 |

Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`

### Política — `policy/`

| Documento | Conteúdo |
|-----------|----------|
| [`ACTUATION_GUARDRAIL_POLICY.md`](policy/ACTUATION_GUARDRAIL_POLICY.md) | Regras HITL lidas por `hitl_guard_actuation` |

## Ordem de leitura (agentes)

1. `mcp/MCP_ROLE_GUIDE.md` — seu papel
2. `board/WORKFLOW_BOARD.md` — status e eventos
3. `routing/REPOS_AND_ROUTING.md` — repo da task
4. `agents/01-role-based/{role}/KNOWLEDGE.md` — digest local
5. `knowledge/REPO_KNOWLEDGE.md` — visão global
6. `graph/STATEGRAPH_FLOW.md` — contexto no grafo
7. `policy/ACTUATION_GUARDRAIL_POLICY.md` — antes de `execute`

## Manutenção

| Script | Função |
|--------|--------|
| `scripts/ops/build_repo_knowledge.py` | Regenera `knowledge/REPO_KNOWLEDGE.md` + `agents/*/KNOWLEDGE.md` |
| `scripts/ops/patch_agent_mcp_knowledge.py` | Atualiza seção MCP nos KNOWLEDGE |
| `scripts/ops/patch_agent_docs.py` | Atualiza seção docs nos `agent.md` |

Autonomia (conceitual): [`../../../docs/autonomia/orquestracao/README.md`](../../../docs/autonomia/orquestracao/README.md)
