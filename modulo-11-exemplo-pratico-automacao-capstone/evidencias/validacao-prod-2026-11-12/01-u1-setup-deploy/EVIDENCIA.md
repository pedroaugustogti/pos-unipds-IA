# U1 — Setup & deploy (produção)

- **Status:** ok
- **Timestamp:** 2026-11-12
- **Ferramenta:** Browser MCP + `curl` + Cloud Run REST + GitHub Actions UI

## Passo a passo

1. Abrir Hosting Firebase: `https://ai-researcher-cap-pedro.web.app/`
2. Confirmar shell Angular “AI RESEARCHER” + disclaimer de não-recomendação
3. Consultar health da API: `GET /api/health` → `{"status":"ok","database":"ok"}`
4. Listar revisions Cloud Run (`ai-researcher-api`, `us-central1`) via REST Knative (3 prontas → rollback possível)
5. Abrir Actions do fork: workflow `deploy` verde (run #4, commit `38904d4`)

## Evidências

| Arquivo | Conteúdo |
|---------|----------|
| `01-hosting-home.png` | Home do app em produção |
| `02-api-health.png` / `03-api-health-browser.png` | Health no browser (tema claro) |
| `api-health.json` | Payload bruto |
| `cloud-run-revisions.txt` / `.json` | 3 revisions Ready |
| `04-github-actions.png` | Lista de runs do `deploy.yml` |

## Resultado

Hosting + API + CI de deploy operacionais; múltiplas revisions permitem rollback.
