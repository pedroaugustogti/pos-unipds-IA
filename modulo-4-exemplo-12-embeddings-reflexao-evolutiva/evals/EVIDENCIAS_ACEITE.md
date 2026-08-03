# Evidências de aceite — Exemplo 12 (Embeddings + Reflexão Evolutiva)

**Data:** 2026-08-03 (revalidação) · primeira validação 2026-07-31  
**Referência UNIPDS:** [aula14-embeddings-reflexao-evolutiva](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula14-embeddings-reflexao-evolutiva)

## Veredito

| Status | Critério geral |
|--------|----------------|
| **APROVADO** | Scaffold UNIPDS, embeddings, reflexão evolutiva e validação local atendem os critérios da aula |
| **RESSALVA** | PostgreSQL requer Docker; ambiente validado com SQLite (`monitor_local.db`) como fallback |

---

## Critérios de sucesso (README)

| # | Critério | Status | Evidência |
|---|----------|--------|-----------|
| 1 | Pasta `modulo-4-exemplo-12-*` | ✅ | `modulo-4-exemplo-12-embeddings-reflexao-evolutiva/` |
| 2 | README local completo | ✅ | `README.md` + seção UNIPDS + evidências |
| 3 | Atividade conforme UNIPDS aula14 | ✅ | Ver tabela técnica abaixo |
| 4 | README raiz atualizado | ✅ | Entrada ex12 + preview ex13 no `README.md` raiz |
| 5 | `.env` não commitado | ✅ | `runtime/.env` no `.gitignore`; apenas `.env.example` versionado |

---

## Critérios técnicos da aula 14

| Componente | Esperado | Status | Evidência |
|--------------|----------|--------|-----------|
| `embedding_adapter.py` | indexar, buscar, reindexar | ✅ | `runtime/adapters/embedding_adapter.py` |
| Storage embeddings | JSON / PostgreSQL / SQLite | ✅ | `EMBEDDING_STORAGE=sqlite`; scripts `setup_*_local.py` |
| OpenRouter embeddings | `text-embedding-3-small` | ✅ | `runtime/llm_config.py` + `.env.example` |
| Lazy reindex | `_recuperar_contexto` se índice vazio | ✅ | `runtime/ciclo.py` L375–391 |
| `conhecimento_relevante` | injetado no contexto | ✅ | relatório: 1 item, sim=0,7009 |
| `reflection.md` | crítica + aprendizado | ✅ | `monitor-agent/reflection.md` |
| `_extrair_licoes` | ao final do ciclo | ✅ | `runtime/ciclo.py` L607+ |
| `_detectar_padroes` | contador MVP a cada 10 exec | ✅ | `reflection_store/meta.yaml` → 8 execuções |
| `licoes_relevantes` | até 5 no planner | ✅ | 3 YAMLs em `reflection_store/licoes/` |
| `planner.md` | `contexto_enriquecido` + regras | ✅ | `monitor-agent/contracts/planner.md` |
| `memory_store/contextual/` | índice de embeddings | ✅ | `indice.json` + 4 fragmentos no SQLite |

---

## Validação automatizada

Script: `validar_execucao_embeddings.py`  
Saída: [`resultados/relatorio_execucao_embeddings/`](./resultados/relatorio_execucao_embeddings/)

| Métrica | Resultado |
|---------|-----------|
| `embeddings_consultados_ok` | **true** |
| Fragmentos indexados | 4 |
| Busca `erro 500 no servico de pedidos` | 1 hit, sim=0,7507 |
| Busca `timeout no banco do servico de pedidos` | 1 hit, sim=0,7009 |
| `_recuperar_contexto` | 1 `conhecimento_relevante` |
| Execuções agente | 2 (3 etapas cada) |
| Duração total | 7,19s |
| **Sucesso geral** | **SIM** |

---

## Hands-on UNIPDS (checklist qualitativo)

| Passo | Observação esperada | Status |
|-------|---------------------|--------|
| 1ª execução com reindex | `[memoria] contextual: N fragmentos indexados` | ✅ (lazy reindex no scaffold) |
| `conhecimento_relevante: N itens` | similaridade no log | ✅ |
| Extração de lição (max_etapas baixo) | `[reflection] extraindo licoes...` | ⚠️ não forçado nesta validação; 3 lições já existem no scaffold |
| Resultado esperado sem surpresa | `[reflection] resultado esperado, sem licao extraida` | ✅ nas 2 execuções de validação |
| `licoes_relevantes: N itens` | injetadas no contexto | ✅ 3 itens |

---

## Próxima aula (preparação)

| Item | Status | Nota |
|------|--------|------|
| `reflection_store/licoes/` populado | ✅ | mínimo 1 lição para `lesson_quality` na aula 15 |
| Embeddings funcionando | ✅ | validado com OpenRouter |
| `MEMORY_DISABLED=1` no ciclo | ✅ | implementado no ex13 |
| `memory_eval.py` + dataset | ✅ | `modulo-4-exemplo-13-evals-memoria` |

**Referência:** [aula15-evals-memoria](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula15-evals-memoria)
