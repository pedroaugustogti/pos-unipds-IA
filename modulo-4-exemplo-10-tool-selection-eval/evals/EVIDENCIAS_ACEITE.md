# Evidências de aceite — Exemplo 10 (Tool Selection Eval)

**Data:** 2026-07-30  
**Referência UNIPDS:** [aula12-tool-selection-eval](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula12-tool-selection-eval)

## Veredito

| Status | Critério geral |
|--------|----------------|
| **APROVADO** | Estrutura, runtime, dataset, CLI, evals e refinamento de skills atendem os critérios da aula |
| **RESSALVA** | `react` e `plan_execute` violam limiares no comparativo LLM completo (75%); `padrao` e `reflect` aprovam (87,5%) |

---

## Critérios de sucesso (README)

| # | Critério | Status | Evidência |
|---|----------|--------|-----------|
| 1 | Pasta `modulo-4-exemplo-10-*` | ✅ | `modulo-4-exemplo-10-tool-selection-eval/` (114 arquivos) |
| 2 | Base UNIPDS aula12 | ✅ | `evals/`, `runtime/tool_eval.py`, `monitor-agent/`, `architectures/`, `api_local/` |
| 3 | Runtime Ex.9 + `tool_eval.py` + CLI | ✅ | `runtime/main.py` → `tool-eval`, `tool-eval-comparar` |
| 4 | `tool_selection_cases.json` (5+ casos) | ✅ | 8 casos (`ts-001` … `ts-008`) |
| 5 | `tool-eval` gera JSON | ✅ | `evals/resultados/tool_eval_*.json` |
| 6 | `tool-eval-comparar` gera relatório | ✅ | `evals/resultados/tool_selection_report.md` |
| 7 | Refino de skills melhora accuracy | ✅ | `comparativo_metricas_v1_v2.md` — v2 +12,5pp tool accuracy (mock) |
| 8 | README local e raiz atualizados | ✅ | `README.md` local + entrada no `README.md` raiz |

---

## Desafios da aula

| # | Desafio | Resultado | Evidência |
|---|---------|-----------|-----------|
| 1 | Rodar tool-eval e anotar accuracy | **87,5%** (padrao, LLM) | `tool_selection_report.md` |
| 2 | Identificar confusão logs vs logs_historico | **ts-004 OK** com LLM | relatório — `buscar_logs_historico` acertado |
| 3 | Refinar `skills.md` e rerodar | Melhoria mensurável | `skills.md` + `comparativo_metricas_v1_v2.md` |
| 4 | Comparar arquiteturas | 4 arquiteturas executadas | `tool_eval_{padrao,react,plan_execute,reflect}.json` |

---

## Limiares de métricas (suite `tool_selection.yaml`)

| Arquitetura | tool_selection_accuracy | unnecessary_calls | wrong_tool | Limiares |
|-------------|------------------------|-------------------|------------|----------|
| **padrao** | **87,5%** | 0% | 12,5% | ✅ Aprovado |
| **reflect** | **87,5%** | 0% | 12,5% | ✅ Aprovado |
| react | 75% | 25% | 25% | ❌ ts-006, ts-008 |
| plan_execute | 75% | 12,5% | 25% | ❌ ts-006, ts-008 |

**Caso único de falha comum:** `ts-008` (issues vs deploy) — documentado em `CHECKLIST_MITIGACAO_VIOLACOES.md`.

---

## Execuções registradas

### LLM completo (4 arquiteturas × 8 casos)
- **Arquivo:** `evals/resultados/tool_selection_report.md`
- **Duração:** ~46 min
- **Modo:** `RUNTIME_PLANEJADOR=llm`

### LLM rápido (smoke 30s)
- **Arquivo:** `evals/resultados/resumo_execucao.json`
- **Casos:** ts-001, ts-006, ts-008
- **Duração:** 21,97s | **Accuracy:** 100%

### Comparativo métricas v1 vs v2
- **Arquivo:** `evals/resultados/comparativo_metricas_v1_v2.md`
- **Melhoria v2:** +87,5pp argument accuracy, +50pp unnecessary calls (mock)

---

## Artefatos adicionais (além da aula base)

| Artefato | Propósito |
|----------|-----------|
| `evals/suites/tool_selection_v2.yaml` | Métricas ampliadas (confusão, repeat, composite) |
| `evals/suites/tool_selection_llm.yaml` | Suite para eval com LLM (histórico simulado) |
| `evals/CHECKLIST_MITIGACAO_VIOLACOES.md` | Mitigação de violações react/plan_execute |
| `runtime/run_tool_eval_local.py` | Runner com `--llm`, `--rapido`, `--timeout` |
| `runtime/comparar_metricas_tool_eval.py` | Comparativo v1 vs v2 automatizado |

---

## Conclusão para próxima aula

O Exemplo 10 está **pronto para fechamento** e serve de base para o **Exemplo 11** (memória do agente — aula13).
