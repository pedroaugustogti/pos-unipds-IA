# Relatório didático — Exemplo 6 (RAG corretivo)

## Síntese

O AI Researcher implementa **RAG corretivo**: a qualidade da resposta depende de um juiz (`grade`) que decide se o contexto local basta; se não, complementa com web (Serper), reindexa com TTL e tenta de novo — sem loop infinito.

## Ligação com as unidades

| Unidade | Contribuição ao RAG |
|---------|---------------------|
| U1 | Corpus CVM, GCP, walking skeleton |
| U2 | Nós + grafo + SSE |
| U3 | Testes, circuit breaker, MCP |
| U4 | Pipeline visual + citações |
| U5 | Langfuse + custo por nó |

## Resultado prático (Pedro / 2026-11-12)

- Seed ~80 docs via Vertex  
- Produção: chat ABEV com retrieve/grade/answer  
- Guardrail e `capstone:check` 11/11  

Detalhe operacional: [`../exemplo_real/README.md`](../exemplo_real/README.md)
