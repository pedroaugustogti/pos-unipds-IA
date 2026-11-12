# Critério final — `capstone:check`

- **Comando:**
  ```powershell
  cd workspace\capstone-project-ai-researcher
  # carregar .env (LANGFUSE_*, GRAFANA_*, GOOGLE_CLOUD_PROJECT_ID)
  pnpm capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
  ```
- **Artefato:** `capstone-check.txt`

## Itens (roteiro Capstone)

| # | Check | Evidência cruzada |
|---|-------|-------------------|
| 1 | Endpoint público | U1 health |
| 2 | Deploy automatizado | U1 Actions |
| 3 | Segredos protegidos | scan repo |
| 4 | Testes no CI | job `test` |
| 5 | Degradação graciosa | `/api/chat` |
| 6 | Traces Langfuse | U5 observations v2 |
| 7 | Rate limiting + alerta | U3 + Grafana abuso |
| 8 | Rollback disponível | U1 revisions (≥2 Ready) |
| 9 | Custo por pergunta | U5 `llm_cost_usd_total` |
| 10 | Guardrail | U3 |
| 11 | README arquitetura | Mermaid no Capstone |

## Nota Windows

- `gcloud` CLI pode falhar com SSL do Python embutido; check usa **fallback REST** Knative + access token.
- Rate limit in-memory por réplica Cloud Run: rajada ampliada para reduzir falso negativo.

## Resultado

**11/11** — saída em `capstone-check.txt` (2026-11-12).
