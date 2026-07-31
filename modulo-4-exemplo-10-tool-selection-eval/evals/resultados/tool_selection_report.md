# Tool Selection Eval — Relatorio

**Agente:** monitor-agent
**Casos:** 8

## Comparativo por Arquitetura

| Metrica | padrao | react | plan_execute | reflect |
|---|---|---|---|---|
| Tool selection accuracy | **87.5%** | 75.0% | 75.0% | **87.5%** |
| Argument accuracy | 56.2% | **75.0%** | **75.0%** | 68.8% |
| Unnecessary calls rate | **0.0%** | 25.0% | 12.5% | **0.0%** |
| Wrong tool rate | **12.5%** | 25.0% | 25.0% | **12.5%** |

## Detalhamento por Caso

| Caso | Tool Esperada | Tool Escolhida | Acertou | Args |
|------|--------------|----------------|---------|------|
| ts-001 | consultar_metricas | consultar_metricas | ✓ | 0% |
| ts-002 | buscar_logs | buscar_logs | ✓ | 100% |
| ts-003 | historico_deploys | historico_deploys | ✓ | 100% |
| ts-004 | buscar_logs_historico | buscar_logs_historico | ✓ | 100% |
| ts-005 | buscar_issues | buscar_issues | ✓ | 100% |
| ts-006 | relatorio_incidente | relatorio_incidente | ✓ | 50% |
| ts-007 | consultar_metricas | consultar_metricas | ✓ | 0% |
| ts-008 | buscar_issues | historico_deploys | ✗ | 0% |

## Violacoes

**react:** tool_selection_accuracy: 0.75 < 0.8, unnecessary_calls_rate: 0.25 > 0.1, wrong_tool_rate: 0.25 > 0.15
**plan_execute:** tool_selection_accuracy: 0.75 < 0.8, unnecessary_calls_rate: 0.125 > 0.1, wrong_tool_rate: 0.25 > 0.15
