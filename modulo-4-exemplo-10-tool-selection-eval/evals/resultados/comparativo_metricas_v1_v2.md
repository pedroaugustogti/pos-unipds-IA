# Comparativo de metricas — tool-eval v1 vs v2

Gerado em: 2026-07-30T13:42:24.434847

## Configuracao

| Aspecto | v1 (baseline) | v2 (assertiva) |
|---------|-----------------|----------------|
| historico_simulado | False | True |
| passar_entrada | False | True |
| modo argumentos | substring | normalizado |

## Metricas agregadas

| Metrica | v1 | v2 | Delta |
|---------|----|----|-------|
| argument_accuracy | 12.5% | 100.0% | +87.5pp |
| repeat_tool_violation_rate | 50.0% | 0.0% | +50.0pp |
| tool_confusion_rate | 0.0% | 25.0% | -25.0pp |
| unnecessary_calls_rate | 62.5% | 12.5% | +50.0pp |
| argument_exact_accuracy | 43.8% | 100.0% | +56.2pp |
| prohibited_tool_violation_rate | 62.5% | 12.5% | +50.0pp |
| tool_selection_accuracy | 25.0% | 37.5% | +12.5pp |
| wrong_tool_rate | 75.0% | 62.5% | +12.5pp |
| composite_assertiveness_score | 16.9% | 43.8% | +26.9pp |

## Impacto por caso (config v2)

| Caso | Esperada | v1 escolheu | v2 escolheu | v1 OK | v2 OK | Melhorou |
|------|----------|-------------|-------------|-------|-------|----------|
| ts-001 | consultar_metricas | consultar_metricas | consultar_metricas | OK | OK | sim |
| ts-002 | buscar_logs | consultar_metricas | buscar_logs | X | OK | sim |
| ts-003 | historico_deploys | consultar_metricas | consultar_metricas | X | X | nao |
| ts-004 | buscar_logs_historico | consultar_metricas | historico_deploys | X | X | sim |
| ts-005 | buscar_issues | consultar_metricas | buscar_logs_historico | X | X | sim |
| ts-006 | relatorio_incidente | consultar_metricas | buscar_logs_historico | X | X | sim |
| ts-007 | consultar_metricas | consultar_metricas | consultar_metricas | OK | OK | sim |
| ts-008 | buscar_issues | consultar_metricas | consultar_metricas | X | X | sim |

## Violacoes de limiar

**v1:** tool_selection_accuracy: 0.25 < 0.8, unnecessary_calls_rate: 0.625 > 0.1, wrong_tool_rate: 0.75 > 0.15
**v2:** tool_selection_accuracy: 0.375 < 0.8, prohibited_tool_violation_rate: 0.125 > 0.05, tool_confusion_rate: 0.25 > 0.1, composite_assertiveness_score: 0.438 < 0.75

## Arquivos gerados

- `tool_eval_v1.log` / `tool_eval_v2.log`
- `tool_eval_v1_padrao.json` / `tool_eval_v2_padrao.json`
- `comparativo_metricas_v1_v2.log` / `.md`
