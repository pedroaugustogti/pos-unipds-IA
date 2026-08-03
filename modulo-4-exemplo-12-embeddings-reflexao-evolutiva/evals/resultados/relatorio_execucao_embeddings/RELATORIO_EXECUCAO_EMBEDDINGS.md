# Relatorio de execucao — Embeddings + PostgreSQL

- **Data:** 2026-08-03T10:23:59.123669
- **Storage:** sqlite
- **OpenRouter:** True
- **Duracao:** 7.19s
- **Sucesso:** SIM

## Busca semantica direta

### `erro 500 no servico de pedidos`
- Hits (limiar 0.7): **1**
  - sim=0.7507 | servico de pedidos com erro HTTP 500 apos deploy...

### `timeout no banco do servico de pedidos`
- Hits (limiar 0.7): **1**
  - sim=0.7009 | timeout no banco de dados durante pico de trafego...

### `falha de conexao PostgreSQL payments`
- Hits (limiar 0.7): **0**

## Recuperacao no ciclo (_recuperar_contexto)

- Fatos longa: 0
- Episodios: 5
- **Conhecimento relevante (embeddings):** 1
- Licoes: 3

- sim=0.7009 — timeout no banco de dados durante pico de trafego

## Execucoes do agente

- **exec1** (erro 500 no servico de pedidos): 3 etapas, tools={'relatorio_incidente': 1, 'buscar_issues': 1}
- **exec2** (timeout no banco do servico de pedidos): 3 etapas, tools={'relatorio_incidente': 1, 'buscar_issues': 1}