# U2 — RAG / pipeline do grafo (produção)

- **Status:** ok
- **Timestamp:** 2026-11-12
- **Ferramenta:** Browser MCP no app de produção

## Passo a passo

1. No chat de produção, perguntar sobre indicadores/resultados da **Ambev (ABEV)**
2. Observar painel **Pipeline de raciocínio** na etapa **Retrieve** (busca vetorial CVM)
3. Aguardar grade + answer com streaming
4. Confirmar chips de citação (ex.: ABEV 3T25 / 4T25 / 1T26 ou fontes web complementares)

## Evidências

| Arquivo | Conteúdo |
|---------|----------|
| `01-pipeline-retrieve.png` | Retrieve em execução |
| `02-chat-abev-resposta.png` | Resposta final com citações |

## Resultado

Grafo retrieve → grade → (search se necessário) → answer funcional em produção com contexto CVM/web.
