# Evidências de aceite — Exemplo 13 (Evals de Memória)

**Data:** 2026-08-03  
**Referência UNIPDS:** [aula15-evals-memoria](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula15-evals-memoria)

## Veredito

| Status | Critério geral |
|--------|----------------|
| **APROVADO** | Scaffold UNIPDS, `memory_eval`, `MEMORY_DISABLED` e validação local atendem critérios da aula |
| **RESSALVA** | `memory_utilization` e `hallucination_from_memory` com FAIL esperado (heurística didática; ver README UNIPDS) |

---

## Critérios de sucesso (README)

| # | Critério | Status | Evidência |
|---|----------|--------|-----------|
| 1 | Pasta `modulo-4-exemplo-13-*` | ✅ | `modulo-4-exemplo-13-evals-memoria/` |
| 2 | README local completo | ✅ | `README.md` |
| 3 | `memory_eval.py` + CLI | ✅ | `runtime/memory_eval.py`, `main.py memory-eval` |
| 4 | `MEMORY_DISABLED=1` | ✅ | `runtime/ciclo.py` |
| 5 | Dataset 5 casos | ✅ | `evals/datasets/memory_impact_cases.json` |
| 6 | Suite 6 métricas | ✅ | `evals/suites/memory_impact_eval.yaml` |
| 7 | Eval executado + relatório | ✅ | `memory_impact_report_20260803_104028.md` |
| 8 | README raiz atualizado | ✅ | `README.md` raiz |

---

## Validação automatizada

Script: `validar_execucao_memory.py` (2 casos demo)  
Saída: [`resultados/relatorio_execucao_memory.json`](./resultados/relatorio_execucao_memory.json)

| Métrica | Resultado | Status |
|---------|-----------|--------|
| `retrieval_precision` | 0,812 | PASS |
| `retrieval_recall` | 0,875 | PASS |
| `memory_utilization` | 0,236 | FAIL (heurística) |
| `hallucination_from_memory` | 0,900 | FAIL (heurística) |
| `decision_improvement` | 0,571 | PASS |
| `lesson_quality` | 1,000 | PASS |
| **Sucesso geral** | **SIM** | `decision_improvement` + `lesson_quality` OK |
| Duração | 31,02s | 2 casos × 2 modos |

---

## Checklist Unidade 4 (fechamento)

| Item | Status |
|------|--------|
| 4 tipos de memória + reflection | ✅ |
| `embedding_adapter.py` | ✅ |
| `reflection_store/licoes/` populado | ✅ (3 lições) |
| Eval de impacto de memória | ✅ |
| `decision_improvement` positivo | ✅ (0,571) |

**Módulo 4 concluído.** Próximo: [`modulo-5-exemplo-1-discovery-refinement`](../../modulo-5-exemplo-1-discovery-refinement/).
