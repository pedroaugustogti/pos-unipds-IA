# Checklist de pré-requisitos — AI Researcher ponta a ponta

> Disciplina: **Projeto Integrador – Capstone Project** (UNIPDS / Anhanguera AVA)  
> Produto: **AI Researcher** · Repos: `ai-researcher-seed` → `capstone-project-ai-researcher`  
> Autoria didática: material e prompts oficiais da pós; este checklist só organiza a automação local.

**Atualizado:** 2026-11-12 (Firebase login + addfirebase Capstone) · Snapshot: [`STATUS_PREREQUISITOS.md`](./STATUS_PREREQUISITOS.md) · `evidencias/preflight/install-pending.json` · scripts: [`../scripts/README_PREREQ.md`](../scripts/README_PREREQ.md) · `install_pending.ps1`

| Campo | Valor |
|-------|--------|
| Projeto GCP | `ai-researcher-cap-pedro` (#149442222162) |
| Billing | `014662-97FB95-F155D4` (Minha conta de faturamento) |
| Conta gcloud | `pedroaugusto.gti@gmail.com` |
| Postgres local | `localhost:5434` → container Capstone + extensão `vector` 0.8.7 |

Legenda: `[x]` feito · `[ ]` falta · notas `🟡` = parcial. Itens **HITL** exigem aprovação humana (billing / IAM / teardown / Cloud SQL).

### Progresso (estimado)

| Bloco | Feito | Parcial | Falta |
|-------|-------|---------|-------|
| 0 Contas | **7** | 0 | 0 |
| 1 Instalação | **9** | 0 | 0 |
| 2 Auth | **5** | 0 | 0 |
| 3 Fundação GCP | **11** | 0 | 0 |
| 4 `.env` local | 6 | 1 (OTEL) | 1 (DEMO opcional) + 4 prod secrets |
| 5 MCP | 4 | 0 | 3 (playwright-test, langfuse-mcp wire, capstone-agent) |
| 6 Skills | 2 | 1 | 1 (frontend-design explícito) |
| 7 Stack local | **6** | 0 | 0 (tests E2E opcional depois) |
| 8 Produção | **4** | 1 (capstone 8/11) | 1 (Langfuse/Grafana polish) |
| 9 Didática | 3 | 1 | 0 |

---

## 0. Contas e acessos

- [x] Conta no **AVA** (Plato) — disciplina Capstone
- [x] Conta **GitHub** (`pedroaugustogti` / clones no workspace)
- [x] Conta **Google Cloud** com **billing** ativo — `014662-97FB95-F155D4` **(HITL ok)**
- [x] Conta **Serper** — API key no `.env`
- [x] Conta **Langfuse Cloud** — public + secret no `.env` (projeto My Project / Hobby)
- [x] Conta **Grafana Cloud** (opc. U5) — OTLP `sa-east-1` + token/header no `.env`
- [x] Firebase ligado ao **mesmo** projeto GCP `ai-researcher-cap-pedro` — login `pedroaugusto.gti@gmail.com` + `projects:addfirebase` + site Hosting

---

## 1. Instalação local (máquina)

| # | Item | Notas |
|---|------|--------|
| [x] | **Node.js ≥ 24** | v24.22.2 |
| [x] | **pnpm 11.x** | **11.20.0** (`npm i -g pnpm@11.20.0`; corepack bloqueado em `C:\BEES\node`) |
| [x] | **Git** + **GitHub CLI (`gh`)** | gh logado |
| [x] | **Docker Desktop** | daemon up |
| [x] | **gcloud CLI** | SDK 565 + `scripts/gcloud_env.ps1` |
| [x] | **Cloud SQL Auth Proxy** | `cloud-sql-proxy` **2.21.2** (componente gcloud) |
| [x] | **Firebase CLI** | `firebase-tools` **15.36.0** (global npm) |
| [x] | **Cursor** | ativo |
| [x] | **uv / uvx** | **0.13.7** em `%USERPROFILE%\.local\bin` — adicionar ao PATH da sessão se faltar |
| [x] | **Playwright** | CLI **1.62.1** + browsers (`apps/web`) |
| [x] | **pgvector** no Postgres Capstone | extensão `vector` **0.8.7** |

Download / clone:

- [x] Clone **seed**: `workspace/ai-researcher-seed`
- [x] Clone **full**: `workspace/capstone-project-ai-researcher`
- [x] Workspace em `modulo-11-exemplo-pratico-automacao-capstone/workspace/`

---

## 2. Autenticações (conexões)

```powershell
. .\scripts\gcloud_env.ps1
gcloud auth login
gcloud auth application-default login
gh auth login
npx firebase-tools login
```

- [x] `gcloud` autenticado (CLI) — `pedroaugusto.gti@gmail.com`
- [x] Application Default Credentials OK (quota project = Capstone)
- [x] `gh` autenticado
- [x] `firebase login` / addfirebase no projeto Capstone (`ai-researcher-cap-pedro`)
- [x] Vertex AI API **habilitada** + teste real (`pnpm seed` 80 docs + chat smoke)

---

## 3. Fundação GCP **(HITL — cena a cena)**

Roteiro: `prompts_aula/aula-1.6-fundacao-gcp.md` + `infra/README.md`  
Automação: `scripts/gcp_fundacao.ps1`

- [x] Projeto GCP criado e **vinculado à billing** — `ai-researcher-cap-pedro`
- [x] APIs: Cloud Run, Cloud SQL Admin, Artifact Registry, Secret Manager, IAM Credentials, Vertex, Cloud Build, Firebase API
- [x] Artifact Registry repo Docker `ai-researcher` (`us-central1`)
- [x] Cloud SQL `ai-researcher-db` · Postgres 16 · `db-f1-micro` ENTERPRISE · banco `ai_researcher` · extensão `vector` 0.8.5 · user `app_user`
  → `powershell -File .\scripts\gcp_fundacao.ps1 -Phase sql -ConfirmSql`
- [x] Secret Manager `database-url` (socket Unix Cloud Run — v3 UTF-8)
- [x] Workload Identity Federation (pool/provider restrito ao repo GitHub) — `github-actions-pool` / `github-actions-provider`
  → `-ConfirmWif` / prompts aula 1.6
- [x] SA `github-actions-deployer` + 7 roles do `infra/README.md`
- [x] Firebase Hosting no projeto — site `ai-researcher-cap-pedro` → https://ai-researcher-cap-pedro.web.app
- [x] `GOOGLE_CLOUD_PROJECT_ID=ai-researcher-cap-pedro` no `.env`
- [x] GitHub **Variables** em `pedroaugustogti/capstone-project-ai-researcher`: `GCP_PROJECT_ID`, `GCP_WIF_PROVIDER`, `GCP_DEPLOY_SERVICE_ACCOUNT`
- [x] `.firebaserc` com o project id (local) → `ai-researcher-cap-pedro`

---

## 4. Variáveis e secrets (app)

### Local — `.env` na raiz do Capstone (gitignored)

Path: `workspace/capstone-project-ai-researcher/.env`  
Check: `scripts/check_env_keys.ps1` → **P6=ok**

- [x] `DATABASE_URL=postgresql://postgres:postgres@localhost:5434/ai_researcher` (porta **5434** — 5432 ocupada pelo Guardião)
- [x] `GOOGLE_CLOUD_PROJECT_ID` / `GOOGLE_CLOUD_PROJECT`
- [x] `GOOGLE_CLOUD_LOCATION=global`
- [x] `MODEL_GRADE` / `MODEL_ANSWER` / `MODEL_EMBEDDING`
- [x] `SERPER_API_KEY`
- [x] `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL`
- [x] 🟡 `OTEL_*` (endpoint + headers presentes; limpar linhas duplicadas no `.env` se ainda houver)
- [ ] `DEMO=true` só quando quiser CI/E2E sem rede (fixtures) — opcional

### Produção — Secret Manager / env Cloud Run

- [x] `database-url` (Secret Manager — socket Unix Cloud Run)
- [x] `serper-api-key`
- [x] `langfuse-public-key` / `langfuse-secret-key`
- [x] `otel-exporter-otlp-headers` + endpoint Grafana (env no deploy.yml)

Nunca versionar: JSON de service account, `.env` real, senhas.

---

## 5. MCP (Cursor / Claude Code)

Mesclar template: [`../config/mcp.capstone.example.json`](../config/mcp.capstone.example.json)  
Feito via `scripts/setup_mcp_skills.ps1` (backup `.cursor/mcp.json.bak-*`).

| # | Server | Para quê | Status |
|---|--------|----------|--------|
| [x] | **github-cli** | repos, PR, Actions | já no monorepo |
| [x] | **playwright-capstone** | Console / chat UI | adicionado |
| [ ] | **playwright-test-capstone** | E2E `apps/web` | pendente config path |
| [x] | **angular-cli-capstone** | scaffold web | adicionado |
| [x] | **langfuse-docs** (HTTP) | docs Langfuse | adicionado |
| [ ] | **langfuse** (`uvx langfuse-mcp`) | traces | falta uvx + env no mcp.json |
| [ ] | **capstone-agent** (`mcp:stdio`) | tool `perguntar` | após build mcp-server |
| [x] 🟡 | **gcloud** CLI | inventário cloud | CLI ok; Google remote MCP opc. |

**Ação:** reiniciar servidores MCP no Cursor após o merge.

Serper: **sem MCP oficial** — key no `.env`.

---

## 6. Skills / plugins

- [x] `CLAUDE.md` / skills no clone full (`.agents/skills`, etc.)
- [x] Skills oficiais no repo (Angular, Langfuse, …)
- [ ] Skill **frontend-design** (aula 18) — confirmar no Cursor
- [x] 🟡 Precedência skill oficial → local → prompt (documentada; seguir na prática)

---

## 7. Subir o stack local (mínimo funcional)

```powershell
cd workspace\capstone-project-ai-researcher
docker compose up -d postgres    # porta host 5434
pnpm.cmd install --frozen-lockfile
pnpm.cmd db:migrate              # OK em 2026-11-12
pnpm.cmd seed                    # OK — 80 docs
pnpm.cmd dev                     # api :3001 + web :4200
```

Automação: `scripts/up_local.ps1` (P4=ok com migrate; seed/dev à parte)

- [x] Postgres healthy (compose Capstone em **:5434**)
- [x] Migrations aplicadas (`drizzle`)
- [x] Extensão `vector` confirmada no banco local (0.8.7)
- [x] `/api/health` OK (`status=ok`, `database=ok` em `:3001`)
- [x] Web abre (`http://localhost:4200/`) + proxy `/api` → `:3001`
- [ ] `pnpm test` / `pnpm test:e2e` (E2E com `DEMO=true`)
- [x] Chat real: quantitativo (corpus) + qualitativo (Serper) — smoke ABEV SSE
- [x] `pnpm seed` (embeddings Vertex) — 80 documentos

---

## 8. Produção / automação CI

- [x] Push em `main` → workflow `deploy.yml` verde (https://github.com/pedroaugustogti/capstone-project-ai-researcher/actions/runs/43238604836)
- [x] WIF sem chave SA (OIDC GitHub → deployer)
- [x] 🟡 `pnpm capstone:check` **8/11** (falhas: Langfuse 410, Grafana vars, gcloud PATH)
- [ ] Langfuse recebendo spans; `/api/metrics` exposto
- [ ] Rate limit / budget (U5) revisados antes de abrir `/chat` público caro

---

## 9. Automação didática (este monorepo)

- [x] Lido [`MAPA_AUTOMACAO.md`](./MAPA_AUTOMACAO.md) + [`HITL_E_LIMITES.md`](./HITL_E_LIMITES.md) + [`PLANO_ACAO_PREREQUISITOS.md`](./PLANO_ACAO_PREREQUISITOS.md)
- [x] [`CATALOGO_VIDEOAULAS_LMS.md`](./CATALOGO_VIDEOAULAS_LMS.md) ↔ `prompts_aula/`
- [x] Runner: `scripts/run_evidencias_capstone.py` + `run_prereq_plan.ps1`
- [x] 🟡 Relatório: [`RELATORIO_EXECUCAO.md`](./RELATORIO_EXECUCAO.md) — regenerar após seed/chat/P5 completo

---

## 10. Ordem sugerida “verde” (restante)

1. ~~Máquina + auth + `.env` + MCP + Postgres local + migrate~~ ✅  
2. `pnpm seed` + `pnpm dev` + smoke chat (**§7**)  
3. Extensão `vector` no Postgres local  
4. ~~Cloud SQL + Secret `database-url`~~ ✅
5. WIF + SA + GitHub Variables + Firebase Hosting  
7. Regenerar evidências (**§9**)

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone
powershell -File .\scripts\run_prereq_plan.ps1 -Until P4
cd workspace\capstone-project-ai-researcher
pnpm.cmd seed                    # OK — 80 docs
pnpm.cmd dev                     # api :3001 + web :4200
```

---

## Fora do escopo deste checklist

- Download / rip de videoaulas do AVA  
- Commitar secrets  
- Recomendação de investimento (proibido por domínio CVM)
