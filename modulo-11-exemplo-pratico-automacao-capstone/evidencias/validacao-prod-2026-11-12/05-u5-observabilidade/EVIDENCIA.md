# U5 — Observabilidade (produção)

- **Status:** ok
- **Timestamp:** 2026-11-12
- **Ferramenta:** Browser MCP + APIs Langfuse/Grafana + `/api/metrics`

## Passo a passo — métricas Prometheus

1. `GET https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app/api/metrics`
2. Confirmar séries `llm_tokens_total` e `llm_cost_usd_total` (nós grade/answer)

## Passo a passo — Langfuse

1. Abrir https://cloud.langfuse.com → projeto **My Project**
2. Aba **Tracing**: spans `retrieve` / `grade` / `answer` / `webSearch` + generations `ChatVertexAI`
3. API: `GET /api/public/v2/observations` (v2; traces legacy indisponível para org nova)

## Passo a passo — Grafana

1. Service Account token `glsa_*` em `GRAFANA_CLOUD_DASH`
2. Dashboard `ai-researcher-api-operacional` (RED por rota)
3. Alert rule group `abuso`: **Abuso: taxa de 429 acima do normal** (`fg435yv2bcmioa`)
4. UI Cloud exige login interativo; evidência de painéis/alerta via API + HTML `grafana-evidence.html`

## Evidências

| Arquivo | Conteúdo |
|---------|----------|
| `api-metrics.txt` | Dump Prometheus |
| `01-api-metrics-browser.png` | Métricas no browser |
| `02-langfuse-tracing.png` | UI Tracing com spans do grafo |
| `langfuse-observations-summary.json` | Sample API v2 |
| `grafana-dashboard-meta.json` | Meta do dashboard |
| `grafana-alert-ai-researcher.json` | Alerta de abuso |
| `grafana-evidence.html` | Resumo visual para screenshot |

## Resultado

Custo/tokens, traces e dashboard/alerta de abuso ativos em produção.
