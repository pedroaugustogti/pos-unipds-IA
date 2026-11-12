# Exemplo real — Capstone · Observabilidade e produção (U5)

Etapa Capstone das **aulas 22–24**: Langfuse, métricas/custo/budget, rate limit, Grafana, README e teardown.

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/)  
**Evidências:** `05-u5-observabilidade/` · `06-check-11-11/` (**11/11**)  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| Contas | Langfuse Cloud; Grafana Cloud (stack + SA) |
| Env `.env` | `LANGFUSE_*`, `GRAFANA_URL`, `GRAFANA_CLOUD_DASH` (**`glsa_*`**) |
| GCP | `GOOGLE_CLOUD_PROJECT_ID` (rollback no check) |
| Deploy | API Cloud Run instrumentada |

Checklist keys: [`check_env_keys.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/check_env_keys.ps1)

---

## Ferramentas e artefatos

| Peça | Arquivo |
|------|---------|
| Langfuse | [`langfuse.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/langfuse.ts) |
| Metrics | [`metrics.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/metrics.ts) |
| Pricing | [`pricing.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/pricing.ts) |
| Budget | [`budget.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/budget.ts) |
| Dashboard Grafana | [`grafana-apply-dashboard.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-dashboard.ts) |
| Alerta Grafana | [`grafana-apply-alert.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-alert.ts) |
| Load test | [`load-test.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/load-test.ts) |
| Check 11/11 | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |
| Teardown HITL | [`destroy.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/destroy.ts) |

---

## Scripts e comandos

| Comando | Script |
|---------|--------|
| `pnpm grafana:dashboard` | [`grafana-apply-dashboard.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-dashboard.ts) |
| `pnpm grafana:alert` | [`grafana-apply-alert.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-alert.ts) |
| `pnpm load:test` | [`load-test.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/load-test.ts) |
| `pnpm capstone:check` | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |
| `pnpm destroy` | [`destroy.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/destroy.ts) |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher
# carregar .env (LANGFUSE_*, GRAFANA_*, GOOGLE_CLOUD_PROJECT_ID)

pnpm.cmd grafana:dashboard
pnpm.cmd grafana:alert

curl.exe -sS --ssl-no-revoke https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app/api/metrics

pnpm.cmd load:test
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
# pnpm.cmd destroy   # HITL
```

| Recurso Grafana | Valor |
|-----------------|--------|
| Dashboard | UID `ai-researcher-api-operacional` |
| Alerta abuso | `Abuso: taxa de 429 acima do normal` · group `abuso` |

---

## Ações

1. Keys Langfuse no `.env` / Secret Manager (validar com [`check_env_keys.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/check_env_keys.ps1)).
2. Tráfego de chat → Tracing ([`langfuse.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/langfuse.ts)).
3. Conferir `/api/metrics` ([`metrics.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/observability/metrics.ts)).
4. Aplicar Grafana: [`grafana-apply-dashboard.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-dashboard.ts) + [`grafana-apply-alert.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/grafana-apply-alert.ts).
5. Rajada / [`load-test.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/load-test.ts) → 429.
6. [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) até **11/11**.
7. Teardown só HITL: [`destroy.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/destroy.ts).

---

## Validação de funcionamento

| Item | Como |
|------|------|
| Langfuse | UI Tracing + Observations v2 |
| Métricas | `curl …/api/metrics` → `llm_cost_usd_total` |
| Grafana | dashboard + alerta abuso |
| Check | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) → SCORE **11/11** |

### Critérios

- [x] Traces Langfuse  
- [x] Custo em `/api/metrics`  
- [x] Dashboard + alerta 429  
- [x] `capstone:check` 11/11  
