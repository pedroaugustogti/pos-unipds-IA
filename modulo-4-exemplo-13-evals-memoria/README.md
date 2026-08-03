# Atividade: Evals de Memória

Este diretório é o **Módulo 4 — Exemplo 13** (`modulo-4-exemplo-13-evals-memoria`) — **fechamento da Unidade 4** — adaptação local da atividade da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [aula15-evals-memoria](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula15-evals-memoria)

## Objetivo

Medir o impacto da memória nas decisões do agente com dataset de casos, suite de 6 métricas e comparação **com vs sem memória** (`MEMORY_DISABLED=1`).

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Exemplo 12 concluído | `embedding_adapter`, `reflection_store/licoes/` populado |
| `.env` | Copie de `modulo-4-exemplo-12/.../runtime/.env` ou `.env.example` |
| Python 3.10+ | Runtime do agente |

## Configuração

```bash
cd modulo-4-exemplo-13-evals-memoria
# copie runtime/.env do ex12 se necessario
python setup_sqlite_local.py
```

## Como executar

```bash
# eval completo (5 casos x 2 modos = 10 execucoes)
cd runtime
python main.py memory-eval --agente ../monitor-agent --suite ../evals/suites/memory_impact_eval.yaml

# demo rapida (2 casos)
python main.py memory-eval --agente ../monitor-agent --suite ../evals/suites/memory_impact_eval.yaml --max-casos 2

# validacao automatizada local
cd ..
python validar_execucao_memory.py
```

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-13-*`
- [x] README local com objetivo, passo a passo e critérios de sucesso
- [x] `memory_eval.py` + subcomando `memory-eval` no `main.py`
- [x] `MEMORY_DISABLED=1` em `_recuperar_contexto`, `_persistir_memoria`, `_extrair_licoes`
- [x] Dataset `memory_impact_cases.json` (5 casos)
- [x] Suite `memory_impact_eval.yaml` (6 métricas)
- [x] Eval executado com relatório em `evals/resultados/memory_impact_report_*.md`
- [x] `lesson_quality` >= 0.4 (requer lições em `reflection_store/licoes/`)
- [x] README raiz do `pos-unipds-IA` atualizado

## Evidências de execução

Validação local em **2026-08-03** — relatório em [`evals/resultados/`](./evals/resultados/).

| Verificação | Resultado |
|-------------|-----------|
| `memory_eval.py` + CLI `memory-eval` | ✅ |
| `MEMORY_DISABLED=1` no ciclo | ✅ |
| Dataset 5 casos + suite 6 métricas | ✅ |
| `decision_improvement` | ✅ 0,571 |
| `lesson_quality` | ✅ 1,0 |
| **Sucesso validação** | **SIM** |

```bash
python validar_execucao_memory.py
# eval completo: MEMORY_EVAL_MAX_CASOS=5 python validar_execucao_memory.py
```

Detalhamento: [`evals/EVIDENCIAS_ACEITE.md`](./evals/EVIDENCIAS_ACEITE.md)

## Material base UNIPDS

# Aula 15 — Evals de memória e fechamento da Unidade 4

A pergunta que o eval responde: **a memória, instalada e funcionando, está realmente melhorando as decisões do agente?**

### Componentes novos

| Componente | Descrição |
|------------|-----------|
| `memory_eval.py` | Harness: cada caso roda com e sem memória |
| `memory_impact_cases.json` | 5 casos (ajuda, ruído, desatualizado, frio, lições) |
| `memory_impact_eval.yaml` | 6 métricas + limiares |
| `MEMORY_DISABLED=1` | Baseline sem memória no `ciclo.py` |

### Métricas

| Métrica | Limiar |
|---------|--------|
| `retrieval_precision` | 0.8 |
| `retrieval_recall` | 0.6 |
| `memory_utilization` | 0.5 |
| `hallucination_from_memory` | max 0.02 |
| `decision_improvement` | min 0.15 |
| `lesson_quality` | 0.4 |

> `decision_improvement` é a métrica-chefe: redução de etapas com memória vs sem memória no mesmo caso.

---

## Fechamento da Unidade 4

Com este exemplo, o Módulo 4 está completo:

| Exemplo | Tema |
|---------|------|
| 1–11 | Contratos, runtime, observabilidade, adapters, memória |
| 12 | Embeddings + reflexão evolutiva |
| **13** | **Evals de impacto de memória** |

**Próximo módulo:** [`modulo-5-exemplo-1-discovery-refinement`](../modulo-5-exemplo-1-discovery-refinement/) — Ferramentas de IA para UI/UX (UNIPDS módulo 05).
