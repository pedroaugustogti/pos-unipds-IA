# Módulo 11 — Exemplo prático: automação do Capstone

Guia e **execução com evidências** das 24 aulas do Capstone (AI Researcher) via **MCP**, **Playwright**, **skills**, **CLI** e HITL — incluindo deploy GCP e validação `capstone:check` **11/11**.

**Caso (fork pessoal):** [pedroaugustogti/capstone-project-ai-researcher](https://github.com/pedroaugustogti/capstone-project-ai-researcher)  
**Upstream UNIPDS:** [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher) · seed: [ai-researcher-seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed)

**Aulas teóricas (U1–U5):** `modulo-11-exemplo-1` … `exemplo-5` · **RAG corretivo:** `modulo-11-exemplo-6-rag-corretivo` · **exemplo_real Capstone:** cada `docs/exemplo_real/README.md`.

## Status (2026-11-12)

| Item | Estado |
|------|--------|
| GCP `ai-researcher-cap-pedro` | Cloud SQL, WIF, Secret Manager, Artifact Registry |
| Produção | [Hosting](https://ai-researcher-cap-pedro.web.app) + [Cloud Run API](https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app) |
| CI | GitHub Actions `deploy.yml` verde no fork pessoal |
| `pnpm capstone:check` | **11/11** (Langfuse Observations v2 + Grafana SA `glsa_*` + `gcloud.cmd` no Windows) |
| Observabilidade | Langfuse Cloud · Grafana dashboard + alerta 429 |

Clone do projeto completo: `workspace/capstone-project-ai-researcher/` (**gitignored** neste módulo — versionado no repo Capstone acima).

## Relatório e evidências

| Artefato | Uso |
|----------|-----|
| [`docs/CHECKLIST_PREREQUISITOS.md`](docs/CHECKLIST_PREREQUISITOS.md) | Pré-requisitos: contas, installs, GCP, MCP, skills, `.env`, CI |
| [`docs/STATUS_PREREQUISITOS.md`](docs/STATUS_PREREQUISITOS.md) | Snapshot do que foi concluído |
| [`scripts/README_PREREQ.md`](scripts/README_PREREQ.md) | Scripts P0–P9 (`run_prereq_plan.ps1`, `gcp_fundacao.ps1`, …) |
| [`docs/PLANO_ACAO_PREREQUISITOS.md`](docs/PLANO_ACAO_PREREQUISITOS.md) | Plano de ação automatizado |
| [`docs/RELATORIO_EXECUCAO.md`](docs/RELATORIO_EXECUCAO.md) | Aula → ferramenta → evidência → teoria |
| [`evidencias/LATEST`](evidencias/LATEST) | Ponteiro da última run de aulas |
| `evidencias/preflight/` | P1–P8 (GCP, WIF, Firebase, deploy) |
| `evidencias/run-2026-11-11T220837Z/` | 24 pastas `aula-XX/` + `summary.json` |
| [`evidencias/validacao-prod-2026-11-12/`](evidencias/validacao-prod-2026-11-12/README.md) | Validação produção U1–U5 + screenshots + `capstone:check` |
| [`scripts/run_evidencias_capstone.py`](scripts/run_evidencias_capstone.py) | Regenera evidências locais |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone
python .\scripts\run_evidencias_capstone.py
```

## Produção — validar

```powershell
cd workspace\capstone-project-ai-researcher
# carregar .env (GRAFANA_*, LANGFUSE_*, GOOGLE_CLOUD_PROJECT_ID, …)
pnpm capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

| Recurso | URL / nota |
|---------|------------|
| App | https://ai-researcher-cap-pedro.web.app |
| API health | https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app/api/health |
| Grafana dashboard | `ai-researcher-api-operacional` na stack Cloud |
| `GRAFANA_CLOUD_DASH` | Service Account token **`glsa_*`** (Access Policy `glc_*` não autentica `/api/dashboards`) |

## Planejamento de automação

| Doc | Uso |
|------|-----|
| [`docs/MAPA_AUTOMACAO.md`](docs/MAPA_AUTOMACAO.md) | Matriz ferramenta → canal |
| [`docs/ROTEIRO_AULA_COM_AUTOMACAO.md`](docs/ROTEIRO_AULA_COM_AUTOMACAO.md) | As 24 aulas com “o que automatizar” |
| [`docs/HITL_E_LIMITES.md`](docs/HITL_E_LIMITES.md) | Billing, IAM, teardown |
| [`config/mcp.capstone.example.json`](config/mcp.capstone.example.json) | Template MCP |
| [`config/playwright.capstone.md`](config/playwright.capstone.md) | Playwright MCP + E2E |
| [`skills/README.md`](skills/README.md) | Skills / plugins |

## Visão rápida

```
Automatizável com MCP / Playwright / skill
├── GitHub (repos, PR, Actions status)     → github MCP / gh
├── Browser (Console GCP, Firebase, chat) → @playwright/mcp
├── Angular CLI / app web                 → angular-cli MCP
├── Postgres / pgvector (query)           → MCP Toolbox / postgres MCP
├── Langfuse (traces, prompts)            → Observations API v2 / langfuse-mcp
├── Cloud Run / Cloud SQL                 → gcloud + WIF (Actions)
└── E2E do Capstone                       → Playwright no CI + MCP em dev

HITL obrigatório
├── Conta de faturamento GCP / cartão
├── Aceite de IAM / WIF (primeira vez)
├── Teardown que apaga banco/produção
└── Chaves Serper / Vertex / Grafana SA (criar; não commit)
```

## Estrutura

```
modulo-11-exemplo-pratico-automacao-capstone/
├── README.md
├── docs/           # checklist, status, plano, relatório, mapa, HITL
├── scripts/        # pré-req + evidências + GCP/GH
├── evidencias/     # preflight + run por aula
├── workspace/      # clone Capstone (gitignored)
├── config/
└── skills/
```

## Critérios de sucesso

- [x] Matriz + roteiro + HITL documentados
- [x] Seed/projeto clonados; evidências aulas 1–24 + preflight P1–P8
- [x] Relatório ferramenta ↔ artefato ↔ evidência
- [x] Template MCP mesclado no `.cursor/mcp.json` (reiniciar MCP no Cursor)
- [x] Stack local (Postgres `:5434`, seed, `pnpm dev`) + smoke chat
- [x] Produção: Hosting + Cloud Run + Actions no fork pessoal
- [x] Langfuse com traces; Grafana dashboard + alerta; `capstone:check` **11/11**
- [ ] Teardown GCP quando encerrar o custo do projeto (HITL)
