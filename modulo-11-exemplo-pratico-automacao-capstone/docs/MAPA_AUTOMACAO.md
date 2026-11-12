# Mapa de automação — ferramentas do Capstone

> Critério: **dá para o agente fazer sozinho via MCP / Playwright / skill / CLI?**  
> Níveis: **A** = automatizar com confiança · **B** = automatizar com revisão · **C** = só humano (HITL)

## Matriz mestre

| Ferramenta / serviço (aula) | Canal preferido | Nível | Notas |
|-----------------------------|-----------------|-------|-------|
| GitHub (fork, clone, PR, Actions) | **GitHub MCP** + `gh` CLI | A | Já há `github-cli` no workspace (`.cursor/github-mcp.ps1`) |
| GitHub Actions YAML / status | GitHub MCP + leitura de logs | A/B | Deploy ainda depende de WIF configurado |
| CLAUDE.md / Agent Skills | arquivos + **Cursor/Claude skills** | A | Não é MCP — é contexto versionado |
| Claude Design / UI mock | skill `frontend-design` + prompt | B | Saída visual; humano valida UX |
| Angular CLI / scaffolding | **Angular CLI MCP** (`npx @angular/cli mcp`) | A | Padrão já usado no Módulo 5 |
| Browser genérico (Console GCP, Firebase, Langfuse UI) | **`@playwright/mcp`** | B | Bom para cliques/forms; frágil se a UI mudar |
| Playwright E2E do Capstone | Playwright Test + `run-test-mcp-server` | A | Modo demo do grafo (aula 21) |
| gcloud / provisionamento | **gcloud CLI** + Google MCP (`gcloud`, Cloud Run, Cloud SQL) | B | Preferir IaC/prompt + dry-run; HITL em IAM |
| Cloud Run | Google **Cloud Run MCP** (remoto) / gcloud | B | Deploy após imagem no Artifact Registry |
| Cloud SQL + pgvector | Google **Cloud SQL for PostgreSQL MCP** + SQL MCP | B | Criar instância = lento/caro → HITL |
| Query/embeddings no Postgres | **MCP Toolbox for Databases** / postgres MCP | A | Após o banco existir |
| Artifact Registry | gcloud CLI / MCP Google | B | Push de imagem via Actions é o caminho canônico |
| Firebase Hosting | **Firebase MCP** / CLI `firebase` | B | Rewrite `/api` → Cloud Run |
| Secret Manager | gcloud + HITL | C/B | Criar secret: humano; ler em runtime: app |
| Workload Identity Federation | prompt IaC + Console/Playwright assistido | C | Primeira configuração = HITL |
| Vertex AI (embedding/chat) | SDK no código (não MCP de provision) | A* | *Uso em runtime; quotas/billing = HITL |
| Serper (busca web) | HTTP API / wrapper MCP custom | A* | Precisa de API key no Secret Manager |
| Coleta corpus CVM | script Node/Python; Playwright só se portal exigir UI | A | Preferir download HTTP dos dados abertos |
| Langfuse (instrumentação) | SDK no código | A | Boot + callbacks (aula 22) |
| Langfuse (consultar traces) | **`langfuse-mcp`** / Langfuse docs MCP | A | Debug pós-deploy |
| Mermaid / README | CLI Mermaid + agente de docs | A | Aula 24 |
| Servidor MCP do próprio Capstone | produto da U3 — stdio/HTTP | A | Tools do agente para IDE/outros agentes |
| Teardown GCP | Console + Playwright assistido / gcloud delete | C | Sempre HITL |

## Canais explicados

### 1. MCP (Model Context Protocol)

O agente chama **tools** tipadas (list repos, query SQL, abrir URL, criar PR) sem scrapear HTML.

| MCP | Papel no Capstone |
|-----|-------------------|
| GitHub | Issues, PRs, contents, checks |
| Playwright | Browser accessibility tree |
| Angular CLI | Generate components/routes |
| Google (Cloud Run, Cloud SQL, gcloud) | Inventário e operações cloud |
| Langfuse | Traces, sessions, prompts |
| Postgres / Toolbox | `ORDER BY embedding <=> …` |
| Capstone MCP (U3) | Expor o agente como tools |

### 2. Playwright

Dois usos distintos:

| Uso | Quando |
|-----|--------|
| **`@playwright/mcp`** | Agente explora UI (Console GCP, Langfuse, chat) em desenvolvimento |
| **Playwright Test + MCP test server** | Suite E2E repetível no CI (modo demo) |

### 3. Skills / plugins

| Skill / plugin | Substitui |
|----------------|-----------|
| `frontend-design` | Ida manual ao Claude Design (parcial) |
| Skills oficiais Angular / LangGraph / Langfuse | Reduz prompt genérico |
| CLAUDE.md do seed | “Memória” do agente de código |

### 4. CLI (sem MCP, mas automatizável pelo agente)

`gcloud`, `firebase`, `gh`, `docker`, `npx mermaid-cli` — o agente já usa shell; MCP só ajuda quando o cliente não tem shell ou quando a API é mais segura/estruturada.

## O que já existe neste monorepo

| Recurso | Caminho |
|---------|---------|
| GitHub MCP | [`.cursor/github-mcp.ps1`](../../.cursor/github-mcp.ps1) · server `github-cli` em [`.cursor/mcp.json`](../../.cursor/mcp.json) |
| Playwright Test MCP (CFP) | `playwright-test-cfp` no mesmo `mcp.json` — **padrão** a espelhar para o Capstone |
| Angular CLI MCP | `angular-cli-pix-app` — **padrão** a espelhar |
| Guardião MCP | `guardiao-familia-agents` — analogia do MCP do próprio produto (U3) |

## Template

Config sugerida: [`../config/mcp.capstone.example.json`](../config/mcp.capstone.example.json)
