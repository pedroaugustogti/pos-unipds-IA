# Checklist — mitigar violações do tool-eval

Use antes de cada execução com LLM e após mudanças em contratos/skills.

## 1. Configuração do eval (processo)

- [ ] **Usar suite LLM** (`tool_selection_llm.yaml`) quando `RUNTIME_PLANEJADOR=llm`
  - `historico_simulado: true` — mock fallback respeita tools já usadas
  - `passar_entrada_ao_planejador: true` — argumentos extraem serviço/repositório
  - `argumentos.modo: normalizado` — evita falso positivo em args
- [ ] **Não misturar suites**: `tool_selection.yaml` (mock) vs `tool_selection_llm.yaml` (LLM)
- [ ] Confirmar `.env` com `OPENROUTER_API_KEY` antes de comparar arquiteturas
- [ ] Rodar com: `python run_tool_eval_local.py --comparar --llm`

## 2. Caso ts-008 — ambiguidade issues vs deploy

**Sintoma:** LLM escolhe `historico_deploys` ou `consultar_metricas` em vez de `buscar_issues`.

- [ ] **Regra em `rules.md`**: pedido explícito de "issues" tem prioridade sobre "deploy"
- [ ] **`skills.md`**: `buscar_issues` descreve uso direto quando usuário pede issues/tickets
- [ ] **`historico_deploys`**: deixar claro que NÃO substitui busca de issues
- [ ] **Dataset** (opcional): entrada sem palavra "deploy" se quiser caso menos ambíguo
- [ ] **Validar** no relatório: ts-008 com `buscar_issues` e args `repositorio=gateway`

## 3. Caso ts-006 — fechar ciclo com `relatorio_incidente`

**Sintoma:** `plan_execute` retorna `FINALIZAR`; `react` cai no mock e re-chama `consultar_metricas`.

- [ ] **Política em `rules.md`**: proibir `FINALIZAR` se `relatorio_incidente` não foi usada
- [ ] **`plan_execute/planner.md`**: último passo do plano deve ser `relatorio_incidente` quando coleta completa
- [ ] **`react/planner.md`**: reforçar JSON válido + não finalizar sem relatório
- [ ] **Mock fallback** (`planejador.py`): se coleta completa → `relatorio_incidente` (não primeira tool)
- [ ] **Eval**: `historico_simulado` inclui as 4 tools de coleta no ts-006

## 4. Fallback JSON inválido (react / plan_execute)

**Sintoma:** `[planejador] resposta JSON invalida, usando mock` → accuracy cai.

- [ ] **Reparo de JSON** ativo em `planejador.py` (strip markdown + extrair `{...}`)
- [ ] **Mock contextual**: ler `Ferramentas ja utilizadas` da percepção se histórico vazio
- [ ] **Arquiteturas ReAct/Plan-Execute**: `response_format: json_object` + regras "nunca texto fora do JSON"
- [ ] **Monitorar** no log quantos casos caíram em `_modo: mock` após LLM
- [ ] Se > 1 caso: revisar `formato_saida` da arquitetura (campos extras quebram parse)

## 5. Chamadas proibidas (`unnecessary_calls_rate`)

**Sintoma:** `consultar_metricas` chamada quando já está em `tools_nao_esperadas`.

- [ ] Histórico simulado alinhado com `ferramentas_ja_usadas` do dataset
- [ ] Mock não reinicia pipeline quando percepção lista tools já usadas
- [ ] Revisar `tools_nao_esperadas` no dataset — só tools realmente proibidas na etapa

## 6. Limiares e regressão

| Métrica | Limiar | Ação se violar |
|---------|--------|----------------|
| `tool_selection_accuracy` | ≥ 80% | Ver casos X no log; aplicar itens 2–4 |
| `unnecessary_calls_rate` | ≤ 10% | Item 5 + histórico simulado |
| `wrong_tool_rate` | ≤ 15% | Itens 2–3 (disambiguation + fechamento) |

- [ ] Comparar `evals/resultados/tool_selection_report.md` após cada mudança
- [ ] Registrar delta em `comparativo_metricas_v1_v2.md` se alterou métricas
- [ ] Meta pós-mitigação: **4/4 arquiteturas** sem violação de limiar

## 7. Ciclo de refinamento (ordem sugerida)

```
1. Ajustar rules.md + skills.md (sem Python)
2. Rodar tool-eval --llm uma arquitetura (padrao)
3. Se ts-008 ainda falha → ajustar descrições / dataset
4. Se react/plan_execute falham → planner.md da arquitetura
5. Se ainda há fallback mock → planejador.py (reparo JSON + mock contextual)
6. tool-eval-comparar --llm nas 4 arquiteturas
7. Arquivar resultados em evals/resultados/
```

## 8. Comandos rápidos

```bash
cd modulo-4-exemplo-10-tool-selection-eval/runtime

# smoke (mock, suite v1)
python run_tool_eval_local.py

# LLM — uma arquitetura
$env:RUNTIME_PLANEJADOR='llm'
python run_tool_eval_local.py --llm --arquitetura padrao

# LLM — comparativo completo
python run_tool_eval_local.py --comparar --llm
```
