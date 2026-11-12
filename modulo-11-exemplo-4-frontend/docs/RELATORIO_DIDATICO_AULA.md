# Relatório Didático — Frontend

> Aula `modulo-11-exemplo-4-frontend`  
> Capstone AI Researcher · aulas 18-21

## Objetivo da unidade

Dar cara ao produto: protótipo, chat com streaming e citações, painel do grafo em tempo real, disclaimer regulatório e E2E no CI.

## Percurso das aulas

| Aula | Arquivo | Síntese |
|------|---------|---------|
| 18 | [`AULA_18_PROTOTIPO_DESIGN.md`](./AULA_18_PROTOTIPO_DESIGN.md) | Prototipar a tela do chat com um prompt no Claude Design e refiná-la por iteração. |
| 19 | [`AULA_19_CHAT_STREAMING.md`](./AULA_19_CHAT_STREAMING.md) | Conectar a casca estática do chat ao backend, com roteamento, um serviço que lê o stream de eventos e um store que guarda as mensagens. |
| 20 | [`AULA_20_PAINEL_GRAFO.md`](./AULA_20_PAINEL_GRAFO.md) | Explicar como o frontend deduz o andamento do grafo a partir dos eventos do stream e prevê a próxima etapa. |
| 21 | [`AULA_21_DISCLAIMER_E2E.md`](./AULA_21_DISCLAIMER_E2E.md) | Adicionar o disclaimer fixo que deixa claro ao usuário que a ferramenta informa e não recomenda. |

## Caso permanente

O **AI Researcher** busca na base vetorial (CVM), julga se o contexto basta, recorre à web quando não basta e responde com **citação** (fonte + data-base). Nunca recomenda compra ou venda — a restrição vive no **código**, não só no system prompt.

## Como estudar

1. Abrir [`MAPA_AULAS.md`](./MAPA_AULAS.md) e ler a aula na ordem.
2. Conferir slides/roteiro em [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md).
3. Reproduzir no [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) ou no [projeto completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).
4. Anotar a ponte Guardião em [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md).

## Checkpoint da unidade

- [ ] Explicar o objetivo da Unidade 4 em duas frases
- [ ] Completar o checkpoint de cada aula 18-21
- [ ] Relacionar ao menos um conceito ao Guardião Família
