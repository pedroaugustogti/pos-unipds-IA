# Atividade: De Mock para Real — Padrão Adapter

Este diretório é o **Módulo 4 — Exemplo 8** (`modulo-4-exemplo-8-de-mock-para-real`) — o `monitor-agent` passa a consumir **APIs HTTP reais** via padrão Adapter, sem `if/else` por skill no runtime.

Referência UNIPDS: [aula10-de-mock-para-real](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula10-de-mock-para-real)

## Objetivo

Substituir mocks aleatórios por **integrações REST declaradas no contrato** (`tipo_implementacao: rest`), mantendo `relatorio_incidente` em mock e preservando o runtime otimizado do Exemplo 7 (planejador `auto`, trace-analyzer, benchmark).

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime e API local |
| **Exemplo 7** | Runtime com benchmark/evals herdado |
| **FastAPI + requests** | API local (`api_local/`) e REST adapter |

## Configuração

```bash
cd modulo-4-exemplo-8-de-mock-para-real/runtime
pip install -r requirements.txt
# .env copiado do Ex. 7 + API_BASE_URL e API_KEY
```

Variáveis novas no `runtime/.env`:

```
API_BASE_URL=http://localhost:8100
API_KEY=dev-local-key
```

## Passo a passo

**Terminal 1** — API local de monitoramento:

```bash
cd modulo-4-exemplo-8-de-mock-para-real
python api_local/server.py
# Uvicorn em http://localhost:8100
```

**Terminal 2** — agente com tools REST:

```bash
cd modulo-4-exemplo-8-de-mock-para-real/runtime
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de checkout"
```

No log, confirme o despacho:

```
[ferramentas] consultar_metricas → rest
[ferramentas] buscar_logs → rest
[ferramentas] historico_deploys → rest
```

No `trace.json`, resultados REST trazem `"_adapter": "rest"` e `"_latencia_ms"`; `relatorio_incidente` permanece mock (sem `_adapter`).

### Desafios da aula

1. Pare a API e rode de novo — observe `sucesso: false` e o efeito de `retries: 2`.
2. Troque uma skill de `rest` para `mock` em `monitor-agent/skills.md` — as demais continuam reais.
3. Compare latência da fase `agir` no trace: REST tem ms de rede; mock ~0ms.

## Estrutura nova nesta aula

```
api_local/
└── server.py                 # FastAPI: /metrics, /logs, /deploys
runtime/
├── adapters/
│   ├── __init__.py
│   └── rest_adapter.py       # HTTP + retries + auth via header
└── ferramentas.py            # _resolver_adapter despacha por tipo_implementacao
monitor-agent/
└── skills.md                 # 3 skills REST + 1 mock (relatorio_incidente)
```

## Mock vs REST no trace

| Característica | Mock | REST (esta aula) |
|----------------|------|------------------|
| Valores entre execuções | aleatórios | fixos da API local |
| Marca no resultado | sem `_adapter` | `_adapter: "rest"` |
| Latência `agir` | ~0ms | ms de HTTP |
| Auditável contra fonte | não | sim (`localhost:8100/api/v1/...`) |

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-8-*`
- [x] Base UNIPDS baixada (57 arquivos)
- [x] Runtime Ex. 7 mesclado (`llm_config`, `planejador`, `ciclo`, `main`, `benchmark`)
- [x] `rest_adapter.py` + `api_local/server.py` implementados
- [x] `skills.md` com `tipo_implementacao`, `conexao` e `limites`
- [x] API local rodando e agente com `_adapter: "rest"` no trace (validado)
- [x] Com API parada, skills REST retornam `sucesso: false` (validado)

---

## Resultados da validação E2E

**Comando (API ativa):**
```bash
python api_local/server.py   # terminal 1
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de checkout"
```

| Critério | Resultado | Trace ID |
|----------|-----------|----------|
| `[ferramentas] → rest` no log | ✅ 3 skills REST despachadas | `c60e9bc27833` |
| `_adapter: "rest"` no trace | ✅ consultar_metricas, buscar_logs, historico_deploys | etapas 1–3 |
| `_latencia_ms` ~2000ms (HTTP) | ✅ fase `agir` com latência de rede | ~1557ms média |
| `relatorio_incidente` sem `_adapter` | ✅ mock determinístico | etapa 4, ~0ms |
| Dados da API (`taxa_erro: 4.2`, `status: degradado`) | ✅ valores fixos da API local | etapa 1 |
| API offline (`API_BASE_URL` inválida) | ✅ REST `sucesso: false`, retries 2/2 | `b406ae7b10ff` |
| `RUNTIME_PLANEJADOR=auto` com skills REST | ✅ planejador mock (fix em `planejador.py`) | via=mock |

**Trace final:** `runtime/trace.json` (5 etapas, 100% sucesso ferramentas com API ativa)

---

## Próxima aula

**Exemplo 9:** [`modulo-4-exemplo-9-database-e-mcp`](../modulo-4-exemplo-9-database-e-mcp/) — adapters `database` e `mcp`, SQLite local (`seed_logs.py`), MCP server stdio, políticas de segurança em `rules.md`/`hooks.md` ([aula11 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula11-database-e-mcp)).

---

## Material base UNIPDS

O README original da aula está em [aula10-de-mock-para-real](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula10-de-mock-para-real) — explica o padrão Adapter, o resolver em `ferramentas.py` e a convivência mock + real no mesmo agente.
