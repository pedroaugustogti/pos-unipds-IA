# Relatorio de Impacto de Memoria — monitor-agent

**Data:** 2026-08-03 10:40:28
**Casos avaliados:** 2
**Tempo total:** 31.0s

## Metricas Agregadas

| Metrica | Valor | Threshold | Status |
|---------|-------|-----------|--------|
| retrieval_precision | 0.812 | 0.8 | PASS |
| retrieval_recall | 0.875 | 0.6 | PASS |
| memory_utilization | 0.236 | 0.5 | FAIL |
| hallucination_from_memory | 0.900 | 0.02 | FAIL |
| decision_improvement | 0.571 | 0.15 | PASS |
| lesson_quality | 1.000 | 0.4 | PASS |

## Comparativo: Sem Memoria vs Com Memoria

| Caso | Etapas Sem | Etapas Com | Improvement |
|------|-----------|-----------|-------------|
| case_001 | 7 | 3 | 0.57 |
| case_002 | 7 | 3 | 0.57 |

## Detalhamento por Caso

| Caso | Recuperados | Esperados | Precision | Recall | Util | Halluc |
|------|-------------|-----------|-----------|--------|------|--------|
| case_001 | 9 | 4 | 1.00 | 0.75 | 0.22 | 0.90 |
| case_002 | 8 | 3 | 0.62 | 1.00 | 0.25 | 0.90 |

## Conclusao

- 4 metricas aprovadas, 2 reprovadas
