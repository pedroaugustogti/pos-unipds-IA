# Atividade: Tool Selection Eval — Precisão de Escolha de Ferramentas

Este diretório é o **Módulo 4 — Exemplo 10** (`modulo-4-exemplo-10-tool-selection-eval`) — o `monitor-agent` com 6 ferramentas ganha um **eval dedicado a tool selection**: dataset com gabarito, 4 métricas e CLI `tool-eval` / `tool-eval-comparar`.

Referência UNIPDS: [aula12-tool-selection-eval](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula12-tool-selection-eval)

## Objetivo

Medir se o planejador escolhe **a tool certa, na etapa certa, com os argumentos certos** — algo que o `benchmark` da aula 9 (taxa de conclusão) não cobre. Herda o runtime completo do Exemplo 9 (4 adapters, `db_adapter`, `mcp_adapter`, segurança) e adiciona `runtime/tool_eval.py`.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Exemplo 9** | 6 tools, 4 adapters, `evals/` base |
| **Python 3.10+** | `tool_eval.py`, CLI |
| **OpenRouter** (opcional) | Planejador LLM para eval real; mock para smoke test |

## Configuração

```bash
cd modulo-4-exemplo-10-tool-selection-eval/runtime
pip install -r requirements.txt
# .env herdado do Ex. 9 (OPENROUTER + DB_CONNECTION_STRING)
```

## Passo a passo

**Terminal 1** — API local (herdada do Ex. 8/9):

```bash
cd modulo-4-exemplo-10-tool-selection-eval
python api_local/server.py
```

**Terminal 2** — tool selection eval:

```bash
cd modulo-4-exemplo-10-tool-selection-eval/runtime

# uma arquitetura
python main.py tool-eval --agente ../monitor-agent \
  --suite ../evals/suites/tool_selection.yaml

# comparativo (padrao, react, plan_execute, reflect)
python main.py tool-eval-comparar --agente ../monitor-agent \
  --suite ../evals/suites/tool_selection.yaml
```

Resultados em `evals/resultados/tool_eval_<arquitetura>.json` e `tool_selection_report.md`.

### Desafios da aula

1. Rode `tool-eval` na arquitetura padrão e anote `tool_selection_accuracy`.
2. Identifique casos com tool errada — `buscar_logs` vs `buscar_logs_historico` se confundem?
3. Refine `descricao` em `monitor-agent/skills.md` e rode de novo (sem mudar Python).
4. Rode `tool-eval-comparar` e compare arquiteturas no relatório.

## Estrutura nova nesta aula

```
evals/
├── datasets/
│   ├── incidentes.json              # Ex. 7/9
│   └── tool_selection_cases.json    # NOVO — gabarito por caso
├── suites/
│   ├── monitor-agent.yaml           # Ex. 7/9
│   └── tool_selection.yaml          # NOVO — 4 métricas + limiares
└── resultados/                      # gerado pelo tool-eval
runtime/
├── tool_eval.py                     # runner + relatório
└── main.py                          # +tool-eval, +tool-eval-comparar
```

## Métricas

| Métrica | Significado | Limiar |
|---------|-------------|--------|
| `tool_selection_accuracy` | % tool correta | ≥ 80% |
| `argument_accuracy` | % argumentos corretos | — |
| `unnecessary_calls_rate` | % tools proibidas chamadas | ≤ 10% |
| `wrong_tool_rate` | % tool errada | ≤ 15% |

> O eval chama **só o planejador** por caso (não o ciclo inteiro) — barato e focado na decisão de tool.

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-10-*`
- [x] Base UNIPDS baixada (`aula12-tool-selection-eval`)
- [x] Runtime Ex. 9 mesclado + `tool_eval.py` e subcomandos CLI
- [x] `tool_selection_cases.json` (8 casos) e `tool_selection.yaml`
- [x] `tool-eval` gera JSON em `evals/resultados/`
- [x] `tool-eval-comparar` gera `tool_selection_report.md`
- [x] Refino de `descricao` em skills melhora accuracy (desafio 3 — ver `comparativo_metricas_v1_v2.md`)
- [x] README local e README raiz atualizados

### Evidências de aceite

Relatório completo: [`evals/EVIDENCIAS_ACEITE.md`](evals/EVIDENCIAS_ACEITE.md)

| Execução | Resultado | Arquivo |
|----------|-----------|---------|
| LLM comparativo (4 arq.) | padrao/reflect **87,5%** — limiares OK | `evals/resultados/tool_selection_report.md` |
| LLM rápido (30s) | 3 casos, **100%**, 21,97s | `evals/resultados/resumo_execucao.json` |
| Métricas v1 vs v2 | +12,5pp accuracy com suite v2 | `evals/resultados/comparativo_metricas_v1_v2.md` |

**Ressalva:** `react` e `plan_execute` ficam em 75% no comparativo LLM — ver [`evals/CHECKLIST_MITIGACAO_VIOLACOES.md`](evals/CHECKLIST_MITIGACAO_VIOLACOES.md).

---

## Material base UNIPDS

O README original da aula está em [aula12-tool-selection-eval](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula12-tool-selection-eval) — detalha o dataset campo a campo, o runner `tool_eval.py`, o ciclo de refinamento de descrições e o checklist de fechamento da Unidade 3.

---

## Próxima aula

**Exemplo seguinte:** [`modulo-4-exemplo-11-agente-que-lembra`](../modulo-4-exemplo-11-agente-que-lembra/) ([aula13-agente-que-lembra](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula13-agente-que-lembra)).
