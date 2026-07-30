# Atividade: Evals e Frameworks de Mercado

Este diretório é o **Módulo 4 — Exemplo 7** (`modulo-4-exemplo-7-evals-e-frameworks-mercado`) — transforma a comparação de arquiteturas em **evidência mensurável**.

Referência UNIPDS: [aula09-evals-e-frameworks-mercado](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula09-evals-e-frameworks-mercado)

## Objetivo

Rodar o `monitor-agent` contra um **dataset de 5 incidentes** com gabarito (`ferramentas_esperadas`), fiscalizar **limiares de qualidade** via eval suite YAML e gerar **relatório comparativo** entre as 4 arquiteturas — com e sem framework cognitivo.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime |
| **Exemplo 6** | Arquiteturas `react`, `plan_execute`, `reflect` |
| **PyYAML** | Parse da eval suite (`requirements.txt`) |

## Configuração

```bash
cd modulo-4-exemplo-7-evals-e-frameworks-mercado/runtime
pip install -r requirements.txt
# .env já copiado do Ex. 6 (RUNTIME_PLANEJADOR=auto)
```

## Passo a passo

```bash
# Benchmark de uma arquitetura
python main.py benchmark --agente ../monitor-agent --suite ../evals/suites/monitor-agent.yaml --arquitetura react

# Comparativo completo (4 arquiteturas × 5 cenários = 20 execuções)
python main.py comparar --agente ../monitor-agent --suite ../evals/suites/monitor-agent.yaml

# Relatórios gerados
cat ../benchmarks/report.md
cat ../benchmarks/report-framework.md
```

## Estrutura nova nesta aula

```
evals/
├── datasets/incidentes.json      # 5 cenários com ferramentas_esperadas
└── suites/monitor-agent.yaml     # métricas + limiares
equivalencias/
├── 01_nosso_framework.py
├── 02_langchain_react.py
├── 03_langgraph_plan_execute.py
└── MAPEAMENTO.md
runtime/
├── benchmark.py                  # engine de eval
└── main.py                       # +subcomandos benchmark e comparar
benchmarks/                       # saída dos relatórios
├── bench_*.json
├── report.md
└── report-framework.md
```

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-7-*`
- [x] Dataset com 5 cenários e suite YAML com limiares
- [x] `benchmark.py` extrai métricas do `trace.json` (sem interpretar LLM)
- [x] CLI `benchmark` e `comparar` funcionando
- [x] `comparar` executado — 20 execuções, 4 JSONs + 2 relatórios Markdown
- [x] Equivalências LangChain/LangGraph documentadas
- [x] README com resultados validados

---

## Resultados da execução (validados)

Comando: `python main.py comparar --agente ../monitor-agent --suite ../evals/suites/monitor-agent.yaml`

### Tabela comparativa (`benchmarks/report.md`)

| Métrica | padrão | react | plan_execute | reflect |
|---------|--------|-------|--------------|---------|
| taxa_conclusao | **100%** | 100% | 100% | 100% |
| media_etapas | **5** | 5 | 5 | 6 |
| media_tokens | 0 | 0 | 0 | 0 |
| cobertura_ferramentas | **100%** | 100% | 100% | 100% |
| reflexoes_total | 0 | 0 | 0 | **10** |
| violacoes de limiar | 0 | 0 | 0 | 0 |

> Tokens = 0 porque `RUNTIME_PLANEJADOR=auto` usa planejador determinístico (ferramentas mock). Com `RUNTIME_PLANEJADOR=llm`, a diferença de tokens entre `plan_execute` e `react` fica visível.

### Com framework vs sem framework (`benchmarks/report-framework.md`)

| Aspecto | Sem framework (padrão) | Com framework (média react/plan/reflect) |
|---------|------------------------|-------------------------------------------|
| Conclusão | 100% | 100% |
| Cobertura | 100% | 100% |
| Etapas médias | 5 | 5,33 (+0,33) |
| Reflexões | 0 | 3,33 (só reflect gera) |
| Raciocínio no trace | não | sim (react/reflect) |
| Plano upfront | não | sim (plan_execute) |
| Autocrítica | não | sim (reflect: 2 reflexões/cenário) |

### O que muda na prática

**Sem framework (`padrão`):**
- Planejador genérico da Unidade 1
- Executa o pipeline, mas sem raciocínio explícito no trace
- 5 etapas por cenário, 0 violações

**Com framework (`react`):**
- Campo `raciocinio` e `nivel_confianca` em cada etapa do trace
- Mesma cobertura, mesmas etapas — ganho é **auditabilidade**

**Com framework (`plan_execute`):**
- Plano completo na etapa 1; etapas seguintes com `tokens=0` no planejador
- Com LLM real: economia significativa de tokens de planejamento

**Com framework (`reflect`):**
- +1 etapa por cenário (6 vs 5) — crítica rejeita 1º FINALIZAR, agente corrige
- 10 reflexões no total (2 por cenário × 5 cenários)
- Garante completude antes de encerrar

**Com eval framework (esta aula):**
- Mede cobertura objetiva (`ferramentas_esperadas` vs `ferramentas_chamadas`)
- Fiscaliza limiares automaticamente (`taxa_conclusao ≥ 80%`, `cobertura ≥ 75%`)
- Gera evidência comparável — não depende de opinião

### Traces de referência (amostra)

| Arquitetura | Cenário | Trace ID | Etapas | Reflexões |
|-------------|---------|----------|--------|-----------|
| padrao | inc-001 | `bc177e0e13ce` | 5 | 0 |
| react | inc-001 | (ver bench_react.json) | 5 | 0 |
| plan_execute | inc-001 | (ver bench_plan_execute.json) | 5 | 0 |
| reflect | inc-001 | `c04b7c0cb65e` | 6 | 2 |

---

## Desafios da aula

1. Abra `benchmarks/report.md` — qual arquitetura tem mais reflexões? Por quê?
2. Adicione um 6º cenário em `evals/datasets/incidentes.json` (ex.: "vazamento de memória") e rode `comparar` de novo.
3. Suba `limiares.cobertura_ferramentas` para `90` no YAML — alguma arquitetura viola?

## Equivalências de mercado

Veja `equivalencias/MAPEAMENTO.md` para o tradutor de conceitos entre nosso framework (contratos Markdown), LangChain (`create_react_agent`) e LangGraph (`StateGraph`).

---

## Próxima aula

**Exemplo 8:** [`modulo-4-exemplo-8-de-mock-para-real`](../modulo-4-exemplo-8-de-mock-para-real/) — **De mock para real** com padrão Adapter: `tipo_implementacao: rest` no `skills.md`, `rest_adapter.py` e API local FastAPI ([aula10 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula10-de-mock-para-real)).
