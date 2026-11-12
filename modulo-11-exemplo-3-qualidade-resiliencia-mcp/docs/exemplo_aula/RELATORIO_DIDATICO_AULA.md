# Relatório Didático — Qualidade, Resiliência e MCP

> Aula `modulo-11-exemplo-3-qualidade-resiliencia-mcp`  
> Capstone AI Researcher · aulas 14-17

## Objetivo da unidade

Deixar o grafo production-ready: testes sem rede, circuit breaker/retry, erros padronizados e exposição do agente via servidor MCP.

## Percurso das aulas

| Aula | Arquivo | Síntese |
|------|---------|---------|
| 14 | [`AULA_14_TESTES_SEM_REDE.md`](./AULA_14_TESTES_SEM_REDE.md) | Explicar como testar um sistema não determinístico tratando a LLM como uma API de terceiro, substituída por fakes. |
| 15 | [`AULA_15_CIRCUIT_BREAKER.md`](./AULA_15_CIRCUIT_BREAKER.md) | Explicar o que timeout, retry com backoff e circuit breaker resolvem quando um serviço de terceiro falha. |
| 16 | [`AULA_16_ERROS_PADRONIZADOS.md`](./AULA_16_ERROS_PADRONIZADOS.md) | Explicar por que os erros de uma API devem ser tratados em um ponto central e devolvidos em um contrato padronizado. |
| 17 | [`AULA_17_SERVIDOR_MCP.md`](./AULA_17_SERVIDOR_MCP.md) | Expor o agente a outros agentes por meio de um servidor MCP com uma única tool, mantendo o guardrail do lado de dentro. |

## Caso permanente

O **AI Researcher** busca na base vetorial (CVM), julga se o contexto basta, recorre à web quando não basta e responde com **citação** (fonte + data-base). Nunca recomenda compra ou venda — a restrição vive no **código**, não só no system prompt.

## Como estudar

1. Abrir [`MAPA_AULAS.md`](./MAPA_AULAS.md) e ler a aula na ordem.
2. Conferir slides/roteiro em [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md).
3. Reproduzir no [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) ou no [projeto completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).
4. Anotar a ponte Guardião em [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md).

## Checkpoint da unidade

- [ ] Explicar o objetivo da Unidade 3 em duas frases
- [ ] Completar o checkpoint de cada aula 14-17
- [ ] Relacionar ao menos um conceito ao Guardião Família
