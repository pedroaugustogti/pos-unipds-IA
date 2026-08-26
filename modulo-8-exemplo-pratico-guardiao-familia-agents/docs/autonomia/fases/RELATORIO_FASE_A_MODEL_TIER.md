# Relatório — Fase A: Modelo LLM / `select_model`

> Data: 2026-08-25  
> Status: **Concluída**  
> Base: [GUIA_LANGGRAPH_MCP_LLM.md](../GUIA_LANGGRAPH_MCP_LLM.md) §2  
> Próxima: [RELATORIO_FASE_B_MCP.md](RELATORIO_FASE_B_MCP.md)

---

## 1. Objetivo

Configurar política de modelos de orquestração (OpenRouter) separada do modelo Cursor de código, com purposes tipados, budget alinhado ao ReAct e aliases `GUARDIAO_LLM_*`.

**Não foi objetivo da A:** chamar OpenRouter no loop de autonomia, MCP nem LangGraph.

---

## 2. O que foi implementado

| Entregável | Descrição |
|------------|-----------|
| `lib/model_tier.py` | `select_model` com purposes + budget + HIGH_HINTS |
| `scripts/model_tier_cli.py` | Inspeciona seleção; `--smoke` / `--smoke-high` opcional |
| `tests/test_model_tier.py` | 7 testes unitários de aceite |
| `crew/.env.example` | `GUARDIAO_LLM_*`, `GUARDIAO_CURSOR_MODEL` |
| `crew/.env` (local) | Chaves Fase A adicionadas (gitignored) |
| `crew/crew.py` | `_llm()` via `select_model` (fixo na montagem do Agent) |
| `lib/dispatch_adapter.py` | Prefere `GUARDIAO_CURSOR_MODEL`, fallback `GUARDAO_*` |
| `lib/env_load.py` | Leitura `.env` com fallback de encoding |
| `crew/requirements.txt` | `openai>=1.40.0` para smoke |
| Docs | `CONFIGURACAO_E_TECNOLOGIA.md` + aceite no guia |

### Purposes disponíveis

| Purpose | Comportamento |
|---------|----------------|
| `route` | Default `deterministic` (sem LLM) |
| `implement_low` | `GUARDIAO_LLM_DEFAULT`; sobe a high se HIGH_HINTS |
| `implement_high` | `GUARDIAO_LLM_HIGH` |
| `review` | Low/high conforme risco da task |
| `summarize` | Modelo low, budget curto |
| `cursor` | `GUARDIAO_CURSOR_MODEL` (Cursor SDK, não OpenRouter) |

---

## 3. Impacto

| Área | Impacto |
|------|---------|
| Autonomia / gateway / demo | **Nenhum** no caminho crítico — Status e demo inalterados |
| LangGraph | Consome `select_model` em `langgraph_app/llm.py` por purpose |
| Dispatch código | Continua Cursor; alias `GUARDIAO_CURSOR_MODEL` |
| OpenRouter | Usado no loop LangGraph (decide/implement/review) |
| Operador | CLI `model_tier_cli` para auditar low vs high |

---

## 4. Como foi validado

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python -m unittest tests.test_model_tier -v
python scripts/model_tier_cli.py --title "Ajuste layout" --json
python scripts/model_tier_cli.py --title "pagamento Stripe" --json
python scripts/model_tier_cli.py --smoke --smoke-high --json
```

| Critério do guia | Resultado |
|------------------|-----------|
| Low-risk → default | OK (testes + CLI) |
| HIGH_HINTS → high | OK |
| `route` sem LLM | OK (`deterministic`) |
| Orquestração ≠ Cursor | OK (`cursor_model` separado) |
| Smoke OpenRouter | Falhou neste ambiente por SSL (`CERTIFICATE_VERIFY_FAILED`); política local OK |

---

## 5. Limitações conhecidas

- Alias legado `CREWAI_MODEL*` ainda aceito se `GUARDIAO_LLM_*` ausente.  
- Smoke de rede depende de certificados/proxy da máquina.

---

## 6. Resumo

**Fase A = política e wiring de modelo.** Pronto para a Fase B (MCP) expor `select_model` e o gateway como tools; decisão LLM de verdade fica para a Fase C.
