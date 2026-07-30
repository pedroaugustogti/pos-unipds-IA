# Atividade: Database, Segurança e MCP — Adapters Completos

Este diretório é o **Módulo 4 — Exemplo 9** (`modulo-4-exemplo-9-database-e-mcp`) — o `monitor-agent` passa a usar **4 tipos de adapter** no mesmo ciclo: REST, database, MCP e mock determinístico.

Referência UNIPDS: [aula11-database-e-mcp](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula11-database-e-mcp)

## Objetivo

Preencher os slots `database` e `mcp` do resolver em `ferramentas.py`, adicionar **segurança declarativa** no contrato (`rules.md`, `hooks.md`) e rodar o agente com **6 ferramentas** e **4 adapters** simultâneos — herdando o runtime otimizado do Exemplo 8 (planejador `auto`, trace-analyzer, benchmark).

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime, API local, MCP server, seed SQLite |
| **Exemplo 8** | REST adapter, `api_local/`, runtime com OpenRouter |
| **FastAPI + requests + mcp** | API local, REST adapter, MCP SDK (`requirements.txt`) |

## Configuração

```bash
cd modulo-4-exemplo-9-database-e-mcp/runtime
pip install -r requirements.txt
# .env copiado do Ex. 8 + DB_CONNECTION_STRING
```

Variáveis novas no `runtime/.env` e na raiz do exemplo (`.env` — lido pelo `db_adapter.py`):

```
DB_CONNECTION_STRING=monitor.db
```

> O adapter SQLite resolve o caminho relativo à raiz do exemplo. Sem connection string, `buscar_logs_historico` cai em simulação (`_simulado: true` no trace).

## Passo a passo

**Terminal 1** — API local de monitoramento (herdada do Ex. 8):

```bash
cd modulo-4-exemplo-9-database-e-mcp
python api_local/server.py
# Uvicorn em http://localhost:8100
```

**Terminal 2** — semear banco e rodar agente:

```bash
cd modulo-4-exemplo-9-database-e-mcp
python seed_logs.py

cd runtime
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de checkout"
```

No log, confirme os 4 tipos de adapter:

```
[ferramentas] consultar_metricas → rest
[ferramentas] buscar_logs → rest
[ferramentas] historico_deploys → rest
[ferramentas] buscar_logs_historico → database
[ferramentas] buscar_issues → mcp
```

No `trace.json`, cada tool traz marca de proveniência (`_adapter`, `_simulado`, `_via_mcp_real`).

### Desafios da aula

Cada desafio tem um **trace de referência** em `runtime/traces/` (gerado por `gerar_traces_desafios.py`):

| # | Desafio | Arquivo | Marcador no trace |
|---|---------|---------|-------------------|
| 1 | 4 adapters ativos | `traces/desafio-01-quatro-adapters.json` | `_adapter`: rest / database / mcp + mock sem adapter |
| 2 | Read-only bloqueia INSERT | `traces/desafio-02-read-only-bloqueado.json` | `violacao de read_only` |
| 3 | Sem `DB_CONNECTION_STRING` | `traces/desafio-03-database-simulado.json` | `_simulado: true` |
| 4 | Fallback MCP | `traces/desafio-04-mcp-fallback.json` | `_via_mcp_real: false` |

Para regenerar após rodar o agente:

```bash
cd runtime
python gerar_traces_desafios.py
```

1. Rode com os 4 adapters ativos e confirme as marcas no `trace.json` (ou abra `desafio-01-quatro-adapters.json`).
2. Tente quebrar o read-only do `db_adapter` — com `modo: read_only` e `INSERT` no `query_template`, o adapter bloqueia antes de tocar no banco (`violacao de read_only`). Com `modo: write`, a validação é pulada (armadilha didática).
3. Renomeie o `.env` (ou remova `DB_CONNECTION_STRING`) e rode de novo — `buscar_logs_historico` deve vir com `_simulado: true`.
4. Sem o SDK `mcp` instalado (ou com MCP server parado), observe fallback em `buscar_issues` (`_via_mcp_real: false`).

## Estrutura nova nesta aula

```
mcp/
├── config.json              # formato padrão MCP (Cursor/Claude Code)
└── server.py                # buscar_issues, verificar_ci_status
seed_logs.py                 # popula monitor.db (20 linhas)
monitor-agent/
├── skills.md                # +buscar_logs_historico (database), +buscar_issues (mcp)
├── rules.md                 # +rate_limit_global, políticas de segurança
└── hooks.md                 # listas: validar_rate_limit, registrar_latencia, ...
runtime/
├── traces/                  # traces de referência por desafio (desafio-01..04)
├── gerar_traces_desafios.py # regenera traces/desafio-*.json
└── adapters/
    ├── db_adapter.py        # read_only, parametrização, LIMIT
    └── mcp_adapter.py       # SDK oficial MCP via stdio
```

## Tools por tipo

| Tool | Adapter | Origem |
|------|---------|--------|
| `consultar_metricas` | rest | Ex. 8 |
| `buscar_logs` | rest | Ex. 8 |
| `historico_deploys` | rest | Ex. 8 |
| `buscar_logs_historico` | **database** | aula11 |
| `buscar_issues` | **mcp** | aula11 |
| `relatorio_incidente` | mock (determinístico) | Ex. 7/8 |

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-9-*`
- [x] Base UNIPDS baixada (63 arquivos de `aula11-database-e-mcp`)
- [x] Runtime Ex. 8 mesclado (`llm_config`, `planejador` com `_agente_precisa_planejador_llm`, `ciclo`, `main`, `benchmark`, ferramentas determinísticas)
- [x] `db_adapter.py` + `mcp_adapter.py` + `mcp/` + `seed_logs.py` preservados da aula11
- [x] `skills.md` com 6 tools (3 REST + 1 database + 1 MCP + 1 mock)
- [x] `seed_logs.py` executado e `DB_CONNECTION_STRING=monitor.db` configurado
- [x] API local rodando; agente com `_adapter: "rest"` / `"database"` / `"mcp"` no trace (validado)
- [x] Teste read-only: adapter bloqueia `INSERT` com `modo: read_only` (validado)
- [x] Sem `DB_CONNECTION_STRING`: `buscar_logs_historico` retorna `_simulado: true` (validado)

---

## Resultados da validação E2E

**Comandos:**
```bash
# terminal 1
python api_local/server.py

# terminal 2
python seed_logs.py
cd runtime
python main.py validar --agente ../monitor-agent
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de checkout"
```

| Critério | Resultado | Trace ID |
|----------|-----------|----------|
| `validar` sem avisos | ✅ contratos OK (agent, rules, skills, hooks, memory) | — |
| `[ferramentas] → rest/database/mcp` no log | ✅ 3 REST + database + MCP despachados | `97117d352739` |
| `_adapter: "rest"` (3 tools) | ✅ consultar_metricas, buscar_logs, historico_deploys | etapas 1–3 |
| `_adapter: "database"`, `_simulado: false` | ✅ 5 eventos do SQLite (`monitor.db`, seed 20 linhas) | etapa 4, ~10ms |
| `_adapter: "mcp"`, `_via_mcp_real: false` | ✅ fallback simulado (SDK `mcp` não instalado) | etapa 5, ~1ms |
| `relatorio_incidente` sem `_adapter` | ✅ mock determinístico | etapa 6 |
| Diagnóstico final | ✅ taxa de erro 4.2% (degradado) | etapa 7 |
| Read-only bloqueia `INSERT` | ✅ `violacao de read_only` antes do banco | teste unitário adapter |
| Sem `DB_CONNECTION_STRING` | ✅ `_simulado: true` (degradação graciosa) | teste adapter |

**Métricas do trace:** 7 etapas, 6 ferramentas, 6,26s total, 0 tokens LLM (planejador mock).

**Trace final:** `runtime/trace.json` — abra após `rodar` para auditar `_adapter`, `_simulado` e `_via_mcp_real` em cada tool.

> **MCP real:** instale `pip install mcp` e rode novamente para obter `_via_mcp_real: true` com handshake stdio em `mcp/server.py`.

---

## Material base UNIPDS

O README original da aula está em [aula11-database-e-mcp](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula11-database-e-mcp) — detalha `db_adapter.py`, handshake MCP, `rules.md`/`hooks.md` e os três vetores de defesa auditáveis no trace.

---

## Próxima aula

**Exemplo seguinte:** [`modulo-4-exemplo-10-tool-selection-eval`](../modulo-4-exemplo-10-tool-selection-eval/) ([aula12-tool-selection-eval](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula12-tool-selection-eval)).
