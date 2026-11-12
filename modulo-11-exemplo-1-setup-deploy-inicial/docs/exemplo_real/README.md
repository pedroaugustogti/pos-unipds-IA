# Exemplo real — Capstone · Setup & Deploy Inicial (U1)

Etapa Capstone correspondente às **aulas 1–7**: walking skeleton (API health + Angular) até deploy em GCP com CI/CD.

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/) · Evidências: `evidencias/validacao-prod-2026-11-12/01-u1-setup-deploy/`  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

| Caso | Valor |
|------|--------|
| Fork | [pedroaugustogti/capstone-project-ai-researcher](https://github.com/pedroaugustogti/capstone-project-ai-researcher) |
| GCP | `ai-researcher-cap-pedro` · `us-central1` · serviço `ai-researcher-api` |
| App | https://ai-researcher-cap-pedro.web.app |
| API | https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app |

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| Contas | GitHub, Google Cloud **com billing**, Firebase no mesmo projeto GCP |
| CLI | Node ≥ 24, pnpm 11, Git, `gh`, Docker Desktop, gcloud, Firebase CLI |
| Auth | `gcloud auth login` + ADC, `gh auth login`, `firebase login` |
| Docs | [`CHECKLIST_PREREQUISITOS.md`](../../../modulo-11-exemplo-pratico-automacao-capstone/docs/CHECKLIST_PREREQUISITOS.md) |
| HITL | Aceite de billing / criação Cloud SQL / IAM WIF |

---

## Ferramentas desta etapa

GitHub Actions (WIF/OIDC) · gcloud · Docker (Postgres local `:5434`) · Firebase Hosting · Artifact Registry · Cloud Run · Cloud SQL · Secret Manager · scripts do exemplo-pratico: [`install_pending.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/install_pending.ps1), [`run_prereq_plan.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_prereq_plan.ps1), [`gcp_fundacao.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcp_fundacao.ps1), [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1), [`set_gh_vars.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/set_gh_vars.ps1).

---

## Scripts e comandos

Rodar a partir de `modulo-11-exemplo-pratico-automacao-capstone` salvo indicação contrária.

Arquivos desta etapa:

| Script | Função |
|--------|--------|
| [`install_pending.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/install_pending.ps1) | Instalações pendentes |
| [`run_prereq_plan.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_prereq_plan.ps1) | Orquestra P1–P9 |
| [`gcloud_env.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcloud_env.ps1) | Helper SSL/auth gcloud |
| [`gcp_fundacao.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcp_fundacao.ps1) | Projeto, APIs, AR, WIF, SQL |
| [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) | Compose + migrate |
| [`set_gh_vars.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/set_gh_vars.ps1) | Variáveis GitHub |
| [`rollback.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/rollback.ts) | Rollback Cloud Run (`pnpm rollback`) |
| [`destroy.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/destroy.ts) | Teardown HITL (`pnpm destroy`) |
| [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) | Aceite produção (`pnpm capstone:check`) |

```powershell
# Toolchain + plano de pré-req
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_pending.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_prereq_plan.ps1 -Until P6

# Auth helper (Windows / SSL)
. .\scripts\gcloud_env.ps1
gcloud auth login
gcloud auth application-default login
gh auth login
npx firebase-tools login

# Fundação GCP (HITL na fase SQL)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\gcp_fundacao.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\gcp_fundacao.ps1 -Phase sql -ConfirmSql

# Stack local
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\up_local.ps1

# No repo Capstone (workspace)
cd workspace\capstone-project-ai-researcher
pnpm.cmd install --frozen-lockfile
pnpm.cmd db:migrate
pnpm.cmd seed          # Vertex
pnpm.cmd dev

# Vars/secrets GH (após fundação)
cd ..\..
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\set_gh_vars.ps1
```

---

## Ações (o que fazer nesta etapa)

1. Clonar seed + full em `workspace/` (ou usar fork pessoal).
2. Completar auth e pré-requisitos (P1–P6) via [`run_prereq_plan.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_prereq_plan.ps1).
3. Provisionar fundação GCP com [`gcp_fundacao.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcp_fundacao.ps1) (SQL com `-ConfirmSql`).
4. Subir stack local com [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1); confirmar health da API.
5. Configurar secrets/vars com [`set_gh_vars.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/set_gh_vars.ps1); push em `main` → `.github/workflows/deploy.yml`.
6. Confirmar Hosting + Cloud Run + ≥ 2 revisions (ver [`rollback.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/rollback.ts)).

Prompts oficiais no Capstone: `prompts_aula/aula-1.5` … `aula-1.7`.

---

## Validação de funcionamento

```powershell
# Health produção
curl.exe -sS --ssl-no-revoke https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app/api/health
# esperado: {"status":"ok","database":"ok"}

# Revisions (rollback)
gcloud run revisions list --service=ai-researcher-api --region=us-central1 --project=ai-researcher-cap-pedro

# Actions
# https://github.com/pedroaugustogti/capstone-project-ai-researcher/actions  → deploy verde

# Check agregado (carregar .env antes) — script: scripts/capstone-check.ts
cd workspace\capstone-project-ai-researcher
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
# itens 1–4 e 8 relevantes a esta unidade
```

Abrir o check: [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts).

**Evidências:** `01-hosting-home.png`, `api-health.json`, `04-github-actions.png`, `cloud-run-revisions.txt`.

### Critérios

- [x] Hosting + `/api/health` ok  
- [x] Workflow `deploy` success  
- [x] ≥ 2 revisions Ready  
