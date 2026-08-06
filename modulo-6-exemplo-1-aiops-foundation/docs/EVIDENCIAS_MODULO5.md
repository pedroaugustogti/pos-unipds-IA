# Evidências de Execução — Módulo 5: AIOps Preditivo

**Data:** 06/08/2026  
**Script:** `nexus/labs/modulo5_aiops.py` (versão otimizada — 3 etapas + `crew_config`)  
**Log:** [`execucao-modulo5-2026-08-06-v2.log`](execucao-modulo5-2026-08-06-v2.log)  
**Exit code:** `0` ✅  
**Duração:** ~120s (inclui pausa TPM de 60s antes da execução)

---

## Resumo executivo

| Métrica | Resultado |
|---------|-----------|
| Etapas concluídas | **3/3** |
| Rate limit Groq (TPM) | **Nenhum** |
| Tools por etapa | **1** (sem loops) |
| `incident_dashboard.json` | ✅ Gerado e validado |
| Preview HTML | ✅ `nexus/incident_dashboard.html` (aberto no navegador) |

---

## Otimizações aplicadas (antes da execução)

| Mudança | Objetivo |
|---------|----------|
| 3 crews isolados (PromQL → ML → Dashboard) | Evitar acúmulo de contexto / TPM |
| Pausa `ROUND_DELAY_SECONDS=25s` entre etapas | Respeitar janela TPM Groq |
| `max_iter=2` no agente AIOps | Impedir loops de tool |
| `kickoff_with_retry()` | Backoff em rate limit |
| 1 tool por agente por etapa | Reduzir decisões do LLM |
| Fallback programático por etapa | Garantir conclusão se Crew falhar após tool |
| `_write_dashboard_preview()` | Visualização local sem Grafana |

---

## Etapa 1 — NL → PromQL ✅

| Item | Detalhe |
|------|---------|
| Tool | `nl_to_promql` (1×) |
| Entrada | `qual a porcentagem de disco livre?` |
| PromQL gerado | `node_filesystem_avail_bytes{mountpoint="/data"} / node_filesystem_size_bytes{mountpoint="/data"} * 100` |
| Status | **SUCESSO** |

---

## Etapa 2 — Alerta preditivo (ML) ✅

| Item | Detalhe |
|------|---------|
| Tool | `predictive_disk_alert` (1×) |
| Histórico | `Uso atual 85%. Crescimento de 2GB por hora contínuo` |
| Resultado | 🚨 Saturação **100% em 4 horas** (Prophet simulado) |
| Ação recomendada | Limpeza de logs ou escalar PVC |
| Status | **SUCESSO** |

---

## Etapa 3 — Dashboard Grafana ✅

| Item | Detalhe |
|------|---------|
| Tool | `generate_grafana_dashboard` (1×) |
| Contexto | `Disk Saturation` |
| Arquivo | `incident_dashboard.json` |
| Status | **SUCESSO** |

### Conteúdo do dashboard gerado

```json
{
  "title": "Dynamic Incident Dashboard: Disk Saturation",
  "panels": [
    { "title": "Disk Usage Prediction", "type": "timeseries", "targets": [{ "expr": "node_filesystem_avail_bytes" }] },
    { "title": "Error Rate Spike", "type": "stat", "targets": [{ "expr": "rate(http_requests_total{status='500'}[5m])" }] }
  ]
}
```

---

## Validação programática

| Check | Resultado |
|-------|-----------|
| Arquivo existe | ✅ |
| JSON válido | ✅ |
| Campo `title` | ✅ |
| Campo `panels` (2 painéis) | ✅ |
| Título referencia `Disk Saturation` | ✅ |

---

## Visualização

| Artefato | Caminho | Como abrir |
|----------|---------|------------|
| JSON (Grafana import) | `nexus/incident_dashboard.json` | Grafana → Import |
| Preview HTML | `nexus/incident_dashboard.html` | Aberto automaticamente no navegador |

### Grafana (opcional)

```powershell
docker run -d -p 3000:3000 --name meu-grafana grafana/grafana
# http://localhost:3000 → Import → upload incident_dashboard.json
```

---

## Comparativo de execuções

| Versão | Etapas | TPM | Dashboard |
|--------|--------|-----|-----------|
| v1 (1 crew, task única) | — | Não testado nesta sessão | — |
| v2 (3 crews, max_iter=3) | Falhou etapa 2 | Loop + LLM vazio | ❌ |
| **v3 (3 crews, max_iter=2 + fallback)** | **3/3** | **OK** | **✅** |

---

## Critérios de aceite

- [x] Pipeline conclui com exit 0
- [x] PromQL de disco gerado
- [x] Alerta preditivo 4h
- [x] `incident_dashboard.json` no disco
- [x] Preview HTML aberto no navegador
- [x] Sem rate limit Groq na execução final

---

## Próximo lab

**Módulo 6** — ChatOps com Human-in-the-Loop: `streamlit run labs/modulo6_chatops.py`
