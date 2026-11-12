# Validação produção — Capstone AI Researcher

- **Data:** 2026-11-12
- **Projeto GCP:** `ai-researcher-cap-pedro`
- **App:** https://ai-researcher-cap-pedro.web.app
- **API:** https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
- **Ferramenta de browser:** Cursor IDE Browser MCP (`cursor-ide-browser`) — Playwright MCP (`user-playwright`) indisponível nesta sessão (auth rejeitada / discovery error)
- **Check:** `pnpm capstone:check --url …` → ver `06-check-11-11/`

## Índice por tópico (U1–U5)

| Pasta | Unidade | O que valida |
|-------|---------|--------------|
| [`01-u1-setup-deploy/`](01-u1-setup-deploy/EVIDENCIA.md) | U1 Setup & deploy | Hosting, health, Cloud Run revisions, GitHub Actions |
| [`02-u2-rag-pipeline/`](02-u2-rag-pipeline/EVIDENCIA.md) | U2 RAG / grafo | Retrieve → grade → answer + citações ABEV |
| [`03-u3-resiliencia-guardrails/`](03-u3-resiliencia-guardrails/EVIDENCIA.md) | U3 Resiliência | Guardrail de investimento + rate limit |
| [`04-u4-frontend/`](04-u4-frontend/EVIDENCIA.md) | U4 Frontend | Chat, disclaimer, pipeline panel, chips |
| [`05-u5-observabilidade/`](05-u5-observabilidade/EVIDENCIA.md) | U5 Observabilidade | `/api/metrics`, Langfuse, Grafana |
| [`06-check-11-11/`](06-check-11-11/EVIDENCIA.md) | Critério final | Score `capstone:check` |

Cada pasta tem **EVIDENCIA.md** (passo a passo) + imagens/artefatos capturados em produção.
