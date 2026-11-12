# Status dos pré-requisitos — 2026-11-12 (pós-automação)

> Checklist completo marcado: [`CHECKLIST_PREREQUISITOS.md`](./CHECKLIST_PREREQUISITOS.md)

Legenda: ✅ feito · 🟡 parcial · ⬜ falta · ⏸ opcional depois

Scripts: [`../scripts/README_PREREQ.md`](../scripts/README_PREREQ.md) · estado: `evidencias/preflight/state.json`

**Projeto GCP:** `ai-researcher-cap-pedro` (#149442222162) · billing `014662-97FB95-F155D4`

---

## Resumo

| Bloco | Status | Nota |
|-------|--------|------|
| **0** Contas | ✅ | Serper+Langfuse+Grafana + **Firebase** no projeto Capstone |
| **1** Instalação | ✅ | pnpm **11.20**, firebase **15.36**, uv **0.13.7**, playwright **1.62**, vector **0.8.7**, cloud-sql-proxy **2.21** |
| **2** Auth | ✅ | gcloud + ADC + gh + **firebase** (`pedroaugusto.gti@gmail.com`) |
| **3** Fundação GCP | ✅ | SQL+WIF+SA+GH vars no repo **pedroaugustogti/capstone-project-ai-researcher** |
| **4** `.env` | ✅ | keys presentes (P6=ok); Postgres host **:5434** |
| **5** MCP | ✅ | merge `playwright-capstone`, `langfuse-docs`, `angular-cli-capstone` (reiniciar MCP no Cursor) |
| **6** Skills | 🟡 | no clone |
| **7** Stack local | ✅ | seed **80** docs + API `:3001` + web `:4200` + chat smoke ABEV OK |
| **8** Produção CI | ✅/🟡 | Deploy Actions verde; Hosting+Cloud Run OK; check 8/11 |
| **9** Evidências | 🟡 | runner existe; regenerar depois do chat |

---

## Já eliminado nesta sessão

- [x] Scripts orquestrador P1–P9 (`run_prereq_plan.ps1`)
- [x] P1 bootstrap (Docker ligado)
- [x] P6 `.env` keys check
- [x] P3 MCP Capstone mesclado (+ backup `.cursor/mcp.json.bak-*`)
- [x] P5 Artifact Registry `ai-researcher` @ `us-central1`
- [x] Postgres Capstone na porta **5434** + migrations

## Ainda falta (próximos comandos)

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone

# Seed real (Vertex) — depois: pnpm.cmd seed no workspace full
# ou:
powershell -File .\scripts\up_local.ps1 -SkipInstall

# Cloud SQL (custo — confirme):
powershell -File .\scripts\gcp_fundacao.ps1 -Phase sql -ConfirmSql

# Dev local:
cd workspace\capstone-project-ai-researcher
pnpm.cmd dev
```

| Item | Ação |
|------|------|
| Seed + chat smoke | ✅ 80 docs + health ok + chat SSE ABEV |
| Firebase no projeto | ✅ login + addfirebase + `.firebaserc` + site Hosting |
| Cloud SQL + secret | ✅ instance+db+user+vector+secret+migrate/seed |
| GH Variables | após WIF |
| Reiniciar MCP Cursor | Settings → MCP |
| pnpm 11 | `corepack prepare pnpm@11.20.0 --activate` (opc.) |
