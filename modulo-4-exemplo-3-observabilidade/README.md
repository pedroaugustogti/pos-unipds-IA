# Atividade: Observabilidade

Este diretório é o **Módulo 4 — Exemplo 3** (`modulo-4-exemplo-3-observabilidade`) — segundo agente (`trace-analyzer`), comando `analisar` e os **4 níveis de observabilidade** da aula UNIPDS.

Referência UNIPDS: [aula05-observabilidade](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula05-observabilidade)

## Objetivo

Rodar o `monitor-agent`, gerar `trace.json`, analisar a execução com o `trace-analyzer` e produzir `analise-agente.md` com diagnóstico automático (saúde, performance, conformidade, anomalias e veredito).

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime do agente |
| **OpenRouter API** | `OPENROUTER_API_KEY` no `runtime/.env` (reutilize do exemplo 9) |
| **pip** | `pip install -r runtime/requirements.txt` |

## Configuração

```bash
cd modulo-4-exemplo-3-observabilidade/runtime
cp .env.example .env
# Edite .env com OPENROUTER_API_KEY (opcional no modo auto — ver abaixo)
pip install -r requirements.txt
```

### Modo rápido (padrão): `RUNTIME_PLANEJADOR=auto`

Quando todas as ferramentas do agente têm implementação determinística em `runtime/`, o planejador **não chama LLM** — execução completa em **< 1 segundo**, com dados exatos lidos de `trace.json`.

| Valor | Comportamento |
|-------|---------------|
| `auto` (padrão) | Mock se ferramentas são determinísticas; LLM caso contrário |
| `mock` | Sempre planejador determinístico |
| `llm` | Sempre OpenRouter (demonstra latência da aula, ~70s+) |

Arquivos de implementação real:

- `ferramentas_monitor_reais.py` — `consultar_metricas`, `buscar_logs`, `historico_deploys`, `relatorio_incidente`
- `ferramentas_analise_reais.py` — 5 skills do `trace-analyzer`

## Passo a passo

### 1. Validar contratos

```bash
python main.py validar --agente ../monitor-agent
python main.py validar --agente ../trace-analyzer
```

### 2. Executar monitor-agent (gera trace)

```bash
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de pagamentos"
```

### 3. Analisar trace (gera relatório)

```bash
python main.py analisar --agente ../trace-analyzer
```

Artefatos gerados em `runtime/`:

| Arquivo | Conteúdo |
|---------|----------|
| `trace.json` | Post-mortem do `monitor-agent` (nível 3) |
| `analise.json` | Trace da análise (rastreabilidade da rastreabilidade) |
| `analise-agente.md` | Relatório legível (nível 4) |

---

## Execução validada (critérios de aceite)

**Data:** 2026-07-29

### Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| Validação sem erros | ✅ | `monitor-agent` e `trace-analyzer`: **VALIDO (0 avisos)** |
| `monitor-agent` completa ciclo | ✅ | 4 ferramentas + `FINALIZAR`, `objetivo_alcancado=True` |
| `trace.json` com telemetria | ✅ | `health_metrics`, `performance_data`, `telemetry_stream` |
| `trace-analyzer` executa 5 skills | ✅ | saúde → performance → conformidade → anomalias → veredito |
| Taxa de sucesso correta no relatório | ✅ | **100%** (lido de `trace.json`, não inventado) |
| Circuit breaker | ✅ | **0** ativações |
| Payload inválido | ✅ | **0** falhas |
| Ferramentas obrigatórias do monitor | ✅ | `relatorio_incidente` chamado antes de `FINALIZAR` |
| Compatibilidade trace ↔ análise | ✅ | `analise.json` referencia o `trace_id` do monitor |
| Relatório `analise-agente.md` | ✅ | Gerado automaticamente pelo comando `analisar` |
| `.env` não commitado | ✅ | Apenas `.env.example` no repositório |

### Métricas — modo `auto` (padrão)

| Agente | Trace ID | Etapas | Tempo | Tokens LLM | Taxa sucesso |
|--------|----------|--------|-------|------------|--------------|
| `monitor-agent` | `39ebfde63c7a` | 5 | **0,0 s** | 0 | 100% |
| `trace-analyzer` | `4d5e5b87e215` | 6 | **0,01 s** | 0 | 100% |

### Métricas — modo `llm` (`RUNTIME_PLANEJADOR=llm`)

| Agente | Trace ID | Etapas | Tempo | Tokens LLM | Taxa sucesso |
|--------|----------|--------|-------|------------|--------------|
| `monitor-agent` | `a8b577a11467` | 6 | **160,7 s** | 11.790 | 100% |
| `trace-analyzer` | `5058fbf1b795` | 6 | **142,2 s** | 13.226 | 100% |

Gargalo no modo LLM: fase `planejar` (~27 s/etapa no monitor). Anomalia detectada: `PERGUNTAR_USUARIO` na etapa 1 em modo `task_based`.

### Respostas ao desafio da aula

1. **Taxa de sucesso?** → **100%** (4/4 ferramentas com qualidade `completa`)
2. **Circuit breaker ativou?** → **Não** (0 ativações)
3. **Gargalo de performance?** → No modo `auto`, `planejar` ≈ **0,6 ms** (determinístico). Com `RUNTIME_PLANEJADOR=llm`, o gargalo é `planejar` via OpenRouter (~15 s/etapa)
4. **Ferramentas obrigatórias chamadas?** → **Sim** — `consultar_metricas`, `buscar_logs`, `historico_deploys`, `relatorio_incidente`

### Veredito do `trace-analyzer`

> execucao saudavel — pipeline completo, taxa de sucesso 100%, zero circuit breaker e zero falhas de payload

---

## Os 4 níveis de observabilidade

```
Nível 1 — Hooks          → terminal em tempo real (gancho:antes_da_etapa, etc.)
Nível 2 — KPIs           → painel a cada etapa (progresso, tokens, ferramentas)
Nível 3 — trace.json     → post-mortem detalhado (percepção, plano, resultado, avaliação)
Nível 4 — trace-analyzer → diagnóstico automático → analise-agente.md
```

## Estrutura

```
modulo-4-exemplo-3-observabilidade/
├── monitor-agent/          # agente monitorado (inalterado da aula 3)
├── trace-analyzer/         # agente que analisa traces
└── runtime/
    ├── main.py             # rodar | validar | analisar | rastreamento | replay
    ├── planejador.py       # auto/mock/llm
    ├── ferramentas_monitor_reais.py
    ├── ferramentas_analise_reais.py
    ├── trace.json          # (gerado)
    ├── analise.json        # (gerado)
    └── analise-agente.md   # (gerado)
```

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **Módulo 4 Ex. 2** | Mesmo runtime; aqui adiciona `trace-analyzer` + comando `analisar` |
| **Módulo 4 Ex. 1** | Contratos e OpenRouter; aqui foco em observabilidade em 4 níveis |

---

## Próxima aula (Exemplo 4)

**UNIPDS:** [aula06-tipos-agentes-e-projetos](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula06-tipos-agentes-e-projetos)

| Item | Conteúdo |
|------|----------|
| Pasta local prevista | `modulo-4-exemplo-4-tipos-agentes-e-projetos` |
| Novo agente | `backlog-decomposer` (`goal_oriented`) |
| Novidades na CLI | `--modo interactive \| goal_oriented \| autonomous` e `--evento` |
| Runtime | Mesmo motor deste exemplo — reutilizar `runtime/` com adaptações mínimas |
| Foco | 4 tipos de agente + contract-driven development + projeto de portfólio |

Comandos esperados na próxima aula:

```bash
python main.py rodar --agente ../backlog-decomposer \
  --entrada "permitir que novos usuarios completem cadastro sem suporte humano"

python main.py rodar --agente ../monitor-agent \
  --entrada "cpu em 95 por cento no servico de pagamentos" \
  --modo autonomous --evento alerta_cpu
```

---

## Critérios de sucesso (repositório)

- [x] Pasta no padrão `modulo-4-exemplo-3-*`
- [x] README com objetivo, passo a passo e critérios validados
- [x] Atividade executada conforme material UNIPDS
- [x] README raiz do `pos-unipds-IA` atualizado
- [x] `.env` não commitado (apenas `.env.example`)

---

## Material base UNIPDS

<details>
<summary>Expandir conteúdo original da aula05-observabilidade</summary>

# Aula 5 — Observabilidade

> Não basta o agente rodar. Você precisa saber se ele decidiu bem.

Em software tradicional, log resolve. Em agente, **log não basta** — porque agente toma decisões, e decisão precisa de rastreabilidade.

Esta aula entrega um segundo agente (`trace-analyzer`) e o comando `analisar`, completando o quadro de observabilidade em **4 níveis**.

Consulte o material completo em: [aula05-observabilidade no GitHub UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula05-observabilidade)

</details>
