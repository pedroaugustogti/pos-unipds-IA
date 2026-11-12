# Módulo 11 — Exemplo prático: automação do Capstone

Guia e **execução com evidências** das 24 aulas do Capstone (AI Researcher) via **MCP**, **Playwright**, **skills**, **CLI** e HITL.

**Caso:** [ai-researcher-seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) → [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher)

**Aulas teóricas (U1–U5):** `modulo-11-exemplo-1` … `exemplo-5`.

## Relatório e evidências (comece aqui)

| Artefato | Uso |
|----------|-----|
| [`docs/CHECKLIST_PREREQUISITOS.md`](docs/CHECKLIST_PREREQUISITOS.md) | Pré-requisitos: contas, installs, GCP, MCP, skills, `.env`, CI |
| [`docs/STATUS_PREREQUISITOS.md`](docs/STATUS_PREREQUISITOS.md) | O que já está feito vs o que falta (atualizado) |
| [`scripts/README_PREREQ.md`](scripts/README_PREREQ.md) | Scripts para eliminar pré-requisitos (`run_prereq_plan.ps1`) |
| [`docs/PLANO_ACAO_PREREQUISITOS.md`](docs/PLANO_ACAO_PREREQUISITOS.md) | Plano de ação automatizado (fases P0–P9 + scripts) |
| [`docs/RELATORIO_EXECUCAO.md`](docs/RELATORIO_EXECUCAO.md) | Relatório explicativo: aula → ferramenta → evidência → teoria |
| [`evidencias/LATEST`](evidencias/LATEST) | Ponteiro da última run |
| `evidencias/run-2026-11-11T220837Z/` | 24 pastas `aula-XX/` + `summary.json` + prompts oficiais |
| [`scripts/run_evidencias_capstone.py`](scripts/run_evidencias_capstone.py) | Regenera evidências locais |

**Status desta run:** 15 `executado` · 8 `parcial` · 1 `hitl` (aula 6 — fundação GCP).

```powershell
python modulo-11-exemplo-pratico-automacao-capstone\scripts\run_evidencias_capstone.py
```

Clones ficam em `workspace/` (gitignored). Com Docker Desktop ativo + `pnpm.cmd install`, reexecute o script para promover aulas 7–8 e testes.

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
├── Langfuse (traces, prompts)            → langfuse-mcp / docs MCP
├── Cloud Run / Cloud SQL (API Google)    → Google remote MCP (quando disponível)
└── E2E do Capstone                       → Playwright no CI + MCP em dev

HITL obrigatório
├── Conta de faturamento GCP / cartão
├── Aceite de IAM / WIF (primeira vez)
├── Teardown que apaga banco/produção
└── Chaves Serper / Vertex em Secret Manager (criar; não commit)
```

## Estrutura

```
modulo-11-exemplo-pratico-automacao-capstone/
├── README.md
├── docs/
│   ├── RELATORIO_EXECUCAO.md     # ← relatório com mapeamento
│   ├── MAPA_AUTOMACAO.md
│   ├── ROTEIRO_AULA_COM_AUTOMACAO.md
│   ├── HITL_E_LIMITES.md
│   └── CONTEUDO_AULAS.md
├── scripts/
│   └── run_evidencias_capstone.py
├── evidencias/
│   ├── LATEST
│   └── run-…/aula-01 … aula-24
├── workspace/                    # clones (gitignored)
├── config/
│   ├── mcp.capstone.example.json
│   └── playwright.capstone.md
└── skills/
    └── README.md
```

## Critérios de sucesso

- [x] Matriz + roteiro + HITL documentados
- [x] Seed e projeto completo clonados; evidências por aula 1–24
- [x] Relatório mapeando ferramenta da vídeo-aula ↔ artefato ↔ evidência
- [ ] Template MCP mesclado no `.cursor/mcp.json`
- [ ] Docker Desktop + `pnpm.cmd` → reexecução com compose/pgvector `executado`
- [ ] Playwright MCP validando chat em modo demo
- [ ] Langfuse / Serper / GCP só com chave e HITL
