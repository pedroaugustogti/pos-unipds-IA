# Atividade: Por dentro do runtime

Este diretório é o **Módulo 4 — Exemplo 2** (`modulo-4-exemplo-2-runtime`) — explora os **6 módulos Python** do runtime que executam os 9 contratos da aula 3.

Referência UNIPDS: [aula04-runtime](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula04-runtime)

## Objetivo

Entender **como o runtime transforma contratos em execução**: carregar YAML dos `.md`, montar estado, planejar com LLM, executar ferramentas, avaliar qualidade e gerar `trace.json` com telemetria completa.

> O agente da aula 3 não mudou. O que muda é a perspectiva: agora você abre o motor.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime do agente |
| **OpenRouter API** | `OPENROUTER_API_KEY` no `runtime/.env` (reutilize dos exemplos 3+) |
| **pip** | `pip install -r runtime/requirements.txt` |

## Configuração

```bash
cd modulo-4-exemplo-2-runtime/runtime
cp .env.example .env
# Edite .env com OPENROUTER_API_KEY
pip install -r requirements.txt
```

## Passo a passo

### 1. Validar contratos

```bash
python main.py validar --agente ../monitor-agent
```

### 2. Executar o agente e gerar trace

```bash
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de pagamentos"
```

### 3. Inspecionar rastreamento

```bash
python main.py rastreamento
```

---

## Ordem de execução (contratos → runtime)

### Fase 0 — Bootstrap (antes do loop)

| Ordem | Módulo | Contratos lidos | Função |
|-------|--------|-----------------|--------|
| 1 | `contratos.py` | 9 arquivos `.md` | `carregar_contratos` → dict com `agente`, `regras`, `habilidades`, `ganchos`, `memoria`, `ciclo`, `planejador`, `executor`, `caixa_ferramentas` |
| 2 | `contratos.py` | `rules.md` | `criar_estado` → limites (`max_etapas`, `limite_tempo`, tokens) |
| 3 | `ferramentas.py` | `skills.md` + `toolbox.md` | `construir_ferramentas_dos_contratos` → 1 função por skill |
| 4 | `telemetria.py` | — | Inicializa `trace_id` único |

### Fase 1–N — Loop por etapa (`ciclo.py → rodar`)

Cada iteração executa **5 fases** nesta ordem fixa:

```
perceber → planejar → [circuit breaker] → validar_payload → agir → avaliar
```

| Fase | Módulo | Contrato fonte | O que faz |
|------|--------|----------------|-----------|
| 1. **Perceber** | `planejador.py` | `agent.md`, histórico | Monta contexto (alerta, modo, ferramentas usadas, progresso) |
| 2. **Planejar** | `planejador.py` | `planner.md`, `rules.md`, `skills.md` | LLM retorna JSON: `proxima_acao`, `nome_ferramenta`, `argumentos_ferramenta` |
| 3. **Circuit breaker** | `ciclo.py` | `toolbox.md` | Valida plano da LLM; auto-corrige ações inválidas |
| 4. **Validar payload** | `executor.py` | `skills.md` (entrada) | Checa tipos dos argumentos |
| 5. **Agir** | `executor.py` | `executor.md`, `hooks.md` | Executa ferramenta; dispara hooks `antes_da_acao` / `apos_acao` |
| 6. **Avaliar** | `executor.py` | `agent.md` (contrato_saida) | Classifica `qualidade` e `objetivo_alcancado` |

### Ordem das ferramentas (`monitor-agent`)

Definida em `skills.md` e obrigatória via `rules.md → ferramentas_obrigatorias`:

| Etapa | Ferramenta | Contrato |
|-------|------------|----------|
| 1 | `consultar_metricas` | Coleta latência, throughput, taxa de erro |
| 2 | `buscar_logs` | Busca logs de erro |
| 3 | `historico_deploys` | Lista deploys recentes |
| 4 | `relatorio_incidente` | **Obrigatório** antes de `FINALIZAR` |
| 5 | `FINALIZAR` | Entrega diagnóstico com `diagnostico`, `evidencias`, `recomendacao`, `severidade` |

---

## Mapeamento trace → código (execução validada)

**Trace ID:** `9eb9d4793b31` | **Tempo:** 70s | **Tokens:** 8.852 | **Taxa sucesso:** 100%

| Etapa trace | `proxima_acao` | Ferramenta | Código que gerou | `objetivo_alcancado` |
|-------------|----------------|------------|------------------|----------------------|
| 1 | `CHAMAR_FERRAMENTA` | `consultar_metricas` | `ciclo.py:246` perceber → `planejador.py:151` chamar_llm → `executor.py` executar | false |
| 2 | `CHAMAR_FERRAMENTA` | `buscar_logs` | Mesmo loop; percepção inclui resultado da etapa 1 | false |
| 3 | `CHAMAR_FERRAMENTA` | `historico_deploys` | Mesmo loop; percepção acumula etapas 1–2 | false |
| 4 | `CHAMAR_FERRAMENTA` | `relatorio_incidente` | Enforcement de `rules.md → ferramentas_obrigatorias` | false |
| 5 | `FINALIZAR` | — | `executor.py` avaliar → `objetivo_alcancado=True` | **true** |

### Saída da execução (etapa 5)

| Campo contrato | Valor observado |
|----------------|-----------------|
| `diagnostico` | API key ausente causando alta taxa de erro (88,33%) |
| `evidencias` | métricas + logs + deploys coletados nas etapas 1–3 |
| `recomendacao` | Verificar API key, rollback se necessário, validação em CI/CD |
| `severidade` | alta (taxa_erro elevada) |

### Health metrics (`trace.json`)

| Métrica | Valor |
|---------|-------|
| Taxa sucesso ferramentas | 100% |
| Circuit breaker ativações | 0 |
| Validação payload falhas | 0 |
| Chamadas LLM | 9 |
| Qualidade por etapa | 4/4 `completa` |

---

## Os 6 módulos do runtime

```
runtime/
├── contratos.py     → carrega os 9 .md, monta o estado inicial
├── ciclo.py         → orquestra o loop e o circuit breaker
├── planejador.py    → percepção e chamada à LLM
├── ferramentas.py   → constrói as tools a partir dos skills
├── executor.py      → valida payload, executa, dispara hooks, avalia
├── telemetria.py    → registra eventos, mede tempo, conta tokens
├── llm_config.py    → OpenRouter / OpenAI (adaptação local)
├── main.py          → CLI (rodar, validar, rastreamento, replay, analisar)
└── validador.py     → valida cruzamento entre os 9 contratos
```

---

## Critérios de sucesso

- [x] `python main.py validar --agente ../monitor-agent` passa sem erros
- [x] Agente executa ciclo completo (5 etapas) e finaliza com `objetivo_alcancado=True`
- [x] Todas as 4 ferramentas obrigatórias chamadas na ordem correta
- [x] `trace.json` gerado com `telemetry_stream`, `health_metrics`, `performance_data`
- [x] Mapeamento trace → código documentado (tabela acima)
- [x] Taxa de sucesso 100%, 0 circuit breaker, 0 falhas de payload
- [x] `.env` não commitado (apenas `.env.example`)
- [x] README raiz do `pos-unipds-IA` atualizado

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **Módulo 4 Ex. 1** | Aula 3 — contratos e `delivery-agent`; aqui você abre o motor |
| **Módulo 3 — LangGraph** | Orquestração em código; aqui é **declarativa** via contratos |

---

## Material base UNIPDS

<details>
<summary>Expandir conteúdo original da aula04-runtime</summary>

# Aula 4 — Por dentro do runtime

> O agente da aula 3 não mudou. O que muda é a perspectiva: agora você abre o motor.

A aula 3 entregou nove contratos Markdown e o agente rodou. Esta aula explica **como**: cada módulo Python do `runtime/` lê um pedaço dos contratos e executa o ciclo. **Cada linha de YAML que você escreveu tem uma linha de Python que a lê.**

> O runtime não sabe nada sobre o agente. Ele só sabe ler contratos e executar.

Consulte o material completo em: [aula04-runtime no GitHub UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula04-runtime)

</details>

## Autor / contexto

Modelo: material **UNIPDS** — [aula04-runtime](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula04-runtime). Adaptação local: OpenRouter, SSL Windows (`truststore`), documentação de trace.
