# Status dos pré-requisitos — 2026-11-12 (pós-produção)

> Checklist: [`CHECKLIST_PREREQUISITOS.md`](./CHECKLIST_PREREQUISITOS.md) · scripts: [`../scripts/README_PREREQ.md`](../scripts/README_PREREQ.md)

Legenda: ✅ feito · 🟡 parcial · ⏸ opcional / HITL depois

**Projeto GCP:** `ai-researcher-cap-pedro` (#149442222162)  
**Repo Capstone:** [pedroaugustogti/capstone-project-ai-researcher](https://github.com/pedroaugustogti/capstone-project-ai-researcher)  
**`capstone:check`:** **11/11** contra `https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app`

---

## Resumo

| Bloco | Status | Nota |
|-------|--------|------|
| **0** Contas | ✅ | Serper + Langfuse + Grafana + Firebase |
| **1** Instalação | ✅ | pnpm 11.20, firebase, uv, playwright, vector, cloud-sql-proxy |
| **2** Auth | ✅ | gcloud + ADC + gh + firebase |
| **3** Fundação GCP | ✅ | SQL + WIF + SA + GH Variables no fork pessoal |
| **4** `.env` | ✅ | keys + `GRAFANA_URL` / `GRAFANA_CLOUD_DASH` (`glsa_*`) / `ALERTA_EMAIL` |
| **5** MCP | ✅ | merge Capstone (reiniciar MCP no Cursor se necessário) |
| **6** Skills | 🟡 | documentadas no clone |
| **7** Stack local | ✅ | seed 80 docs + API `:3001` + web `:4200` + smoke ABEV |
| **8** Produção CI | ✅ | Actions verde · Hosting · Cloud Run · check **11/11** |
| **9** Evidências | ✅ | preflight P1–P8 + run aulas 1–24 |

---

## Produção

| Recurso | Valor |
|---------|--------|
| Hosting | https://ai-researcher-cap-pedro.web.app |
| Cloud Run | https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app |
| Langfuse | Observations API v2 (traces OK) |
| Grafana | dashboard `ai-researcher-api-operacional` + alerta 429 |

## HITL restante

- [ ] Teardown GCP (apagar Cloud SQL / Run / secrets) quando não precisar mais do custo
- [ ] Reiniciar MCP no Cursor após mudanças em `.cursor/mcp.json`
