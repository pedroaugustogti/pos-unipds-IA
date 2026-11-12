# Roteiro das 24 aulas — o que automatizar

Para cada aula: **objetivo** · **ferramentas** · **automação sugerida** · **HITL**.

Conteúdo completo das aulas: pastas `modulo-11-exemplo-1` … `5` (ver [`CONTEUDO_AULAS.md`](./CONTEUDO_AULAS.md)).

---

## Unidade 1 — Setup e Deploy Inicial (1–7)

### Aula 1 — Bem-vindo / RAG corretivo

| | |
|--|--|
| Ferramentas | GitHub (ler repo), browser (opcional) |
| Automatizar | GitHub MCP: clonar/listar seed e projeto completo; abrir diagramas locais |
| HITL | Entender a regra “não recomenda investimento” |

### Aula 2 — CLAUDE.md e skills

| | |
|--|--|
| Ferramentas | Editor, skills Cursor/Claude |
| Automatizar | Agente edita `CLAUDE.md` / skills via filesystem; skill oficial do framework > skill local (precedência) |
| HITL | Revisar o que o agente **deve perguntar** antes de instalar deps / mudar schema |

### Aula 3 — Tour GCP

| | |
|--|--|
| Ferramentas | Console GCP, docs Google |
| Automatizar | **Playwright MCP** para navegar Console (leitura); Google MCP / gcloud para listar serviços |
| HITL | Conta e faturamento |

### Aula 4 — GitHub Actions + WIF

| | |
|--|--|
| Ferramentas | GitHub Actions, IAM GCP |
| Automatizar | GitHub MCP: criar/editar workflow YAML, ver runs; gcloud para inspecionar pool WIF |
| HITL | **Criar** Workload Identity Pool / binding IAM (primeira vez) |

### Aula 5 — Corpus CVM

| | |
|--|--|
| Ferramentas | Portal Dados Abertos CVM, script de coleta |
| Automatizar | Script HTTP (preferencial); Playwright só se o download for só via UI |
| HITL | Validar amostra JSON (empresa/trimestre) |

### Aula 6 — Fundação GCP

| | |
|--|--|
| Ferramentas | gcloud, Cloud SQL, Artifact Registry, Secret Manager |
| Automatizar | Prompts IaC + **gcloud MCP** / Cloud SQL MCP (list/describe); gerar connection string |
| HITL | Criar instância Cloud SQL (custo/tempo); gerar e guardar secrets |

### Aula 7 — Walking Skeleton / Deploy Zero

| | |
|--|--|
| Ferramentas | Docker, Actions, Cloud Run, Firebase, Angular |
| Automatizar | GitHub MCP dispara/observa workflow; Angular MCP gera health UI; Playwright MCP valida `/health` |
| HITL | Primeiro deploy se WIF ainda não estiver verde |

---

## Unidade 2 — Orquestração cognitiva (8–13)

### Aula 8 — pgvector / seed

| | |
|--|--|
| Ferramentas | Cloud SQL / Postgres local, Vertex embeddings |
| Automatizar | SQL MCP: `CREATE EXTENSION`, índice HNSW, `ORDER BY embedding <=> $1 LIMIT k` |
| HITL | Quotas Vertex na primeira carga massiva |

### Aulas 9–13 — retrieve, grade, Serper, fallback, grafo, answer SSE

| | |
|--|--|
| Ferramentas | LangGraph.js, Serper, Vertex, Fastify SSE |
| Automatizar | Agente de código + testes; Serper via env; Playwright no chat quando a UI existir (U4) |
| HITL | API key Serper; revisar guardrail de citação / “não recomendar” |

**Não há MCP oficial Serper** — opção: tool MCP **custom** no Capstone (`web_search`) na U3.

---

## Unidade 3 — Qualidade, resiliência e MCP (14–17)

### Aula 14 — Testes sem rede

| | |
|--|--|
| Automatizar | Runner de testes via shell/MCP do projeto; modo demo do grafo |
| HITL | Definir quais stubs são aceitáveis |

### Aula 15–16 — Circuit breaker / erros

| | |
|--|--|
| Automatizar | Testes de falha; Playwright MCP forçando timeout em stub |
| HITL | Contratos de erro expostos ao cliente |

### Aula 17 — Servidor MCP do Capstone

| | |
|--|--|
| Automatizar | Registrar o MCP do app no Cursor (stdio), listar tools, smoke invoke |
| HITL | Escopo das tools (não expor escrita perigosa sem gate) |

---

## Unidade 4 — Frontend (18–21)

### Aula 18 — Claude Design → skill frontend-design

| | |
|--|--|
| Automatizar | Skill `frontend-design`; Angular MCP para gerar componentes |
| HITL | Aprovar layout / acessibilidade |

### Aula 19–20 — Chat streaming + painel do grafo

| | |
|--|--|
| Automatizar | **Playwright MCP**: abrir chat, enviar pergunta demo, ler painel retrieve→grade→answer |
| HITL | Conferir citações CVM vs web |

### Aula 21 — Disclaimer + E2E CI

| | |
|--|--|
| Automatizar | Playwright Test (modo demo) + MCP test server no Cursor; GitHub Actions roda a suite |
| HITL | Texto legal do disclaimer |

---

## Unidade 5 — Observabilidade e produção (22–24)

### Aula 22 — Langfuse

| | |
|--|--|
| Automatizar | SDK no boot; **langfuse-mcp** para inspecionar spans; Playwright MCP no dashboard |
| HITL | Criar projeto/API keys no Langfuse |

### Aula 23 — Métricas / budget / rate limit

| | |
|--|--|
| Automatizar | Endpoint `/metrics`; testes de estouro de budget |
| HITL | Valores de teto diário em produção |

### Aula 24 — README Mermaid + teardown

| | |
|--|--|
| Automatizar | Gerar Mermaid + `mmdc`; GitHub MCP atualiza README |
| HITL | **Desligar Cloud SQL / projeto GCP** (custo) |

---

## Sequência mínima recomendada (setup do aluno)

1. Ligar **GitHub MCP** + **Playwright MCP** + **Angular MCP** (template).  
2. Seguir U1 com gcloud/`gh` e HITL em SQL/WIF.  
3. Na U3, adicionar o **MCP do Capstone**.  
4. Na U4, Playwright E2E modo demo.  
5. Na U5, **langfuse-mcp** + teardown humano.
