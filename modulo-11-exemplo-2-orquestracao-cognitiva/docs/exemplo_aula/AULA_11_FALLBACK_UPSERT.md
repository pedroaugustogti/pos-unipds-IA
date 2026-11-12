# Aula 11: Fallback pra busca web, upsert retroativo

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Construir o nó de busca na web, que pesquisa apenas os aspectos que faltam, extrai o texto das páginas e grava os chunks com embedding.
- Explicar por que a informação vinda da web recebe um prazo de validade (TTL) e a informação da CVM não.
- Descrever como o retrieve passa a combinar os documentos da CVM e os da web, fazendo o agente se retroalimentar.

## Desenvolvimento

### Contexto da aula

Com o provedor de busca pronto, falta o nó que o utiliza. Esta aula cria o nó web search, que busca na internet o que o grade apontou como faltante e agrega o resultado ao contexto do agente. O nó faz mais do que buscar. Ele grava no banco de dados o embedding do que encontrou, para que uma pergunta parecida, feita depois, já encontre essa informação no RAG. Ao final, você saberá descrever o que o nó faz passo a passo, por que a informação da web tem prazo de validade e como o agente passa a se retroalimentar.

- Explicar por que a informação vinda da web recebe um prazo de validade (TTL) e a informação da CVM não.
- Descrever como o retrieve passa a combinar os documentos da CVM e os da web, fazendo o agente se

### O nó web search: buscar só o que falta

O nó é criado com um único prompt, que descreve tudo de que o Claude Code precisa: o comportamento do nó, a tabela nova, a mudança no retrieve e os testes.

### Prompt enviado ao Claude Code

Crie o nó web_search (packages/agent/src/nodes/web-search.ts). Recebe question e missingAspects do estado. Monta uma query por aspecto faltante (${question} ${aspecto}), ou só a pergunta se a lista estiver vazia. Para cada query, chama searchProvider.search(), pega os 3 primeiros resultados, busca o HTML de cada URL (fetch nativo, timeout de 10s), extrai texto legível (sem tags), divide em chunks de ~1000 caracteres com sobreposição de 100, gera embedding de cada chunk e insere um documento por chunk numa tabela nova documentos_web — com query, title, content, sourceUrl, fetchedAt e expiresAt calculado a partir de um TTL em dias (default 7). Se uma página falhar (fora do ar, timeout), ignora esse resultado e segue pros outros, sem derrubar o nó inteiro. Estenda buscarDocumentosSimilares (o mesmo usado pelo nó retrieve da aula passada) pra também consultar documentos_web — filtrando expirados — e combinar os resultados dos dois com o do corpus CVM, ordenado só pela distância. Tudo testável com fakes, sem rede nem Postgres real.

O nó recebe do estado a pergunta e o missingAspects. A pergunta está no estado desde o primeiro nó do grafo. O missingAspects vem do grade, que avalia o contexto e diz o que falta para responder de forma satisfatória. No LangGraph, o agente é um grafo com vários nós. O state é o estado que vai sendo atualizado conforme a execução passa pelos nós. O centro do nó é a função makeWebSearchNode. O trabalho dela segue estas etapas: 1. Montar as queries: uma por aspecto faltante, juntando a pergunta e o aspecto. Se a lista de aspectos estiver vazia, a query é só a pergunta. 2. Buscar: para cada query, o nó chama o provedor de busca criado na Aula 10 e fica com os três primeiros resultados. 3. Ler as páginas: o nó busca o HTML de cada URL com fetch nativo e timeout de 10 segundos. 4. Extrair e dividir: o texto legível é extraído, sem as tags, e dividido em chunks de cerca de 1.000 caracteres, com sobreposição de 100. A divisão é necessária porque uma notícia pode ter muito texto. 5. Gerar os embeddings: cada chunk recebe o seu embedding pelo Vertex AI, com o mesmo cliente de embeddings usado no retrieve. 6. Gravar: o nó insere um documento por chunk na tabela nova de documentos da web, com a query, o título, o conteúdo, a URL, a data da busca e a data de expiração.

Fluxo editorial com as etapas do nó descritas na aula.

### ATENÇÃO — Por que não enviar a pergunta inteira à busca

Se o nó simplesmente jogasse a pergunta na internet, a avaliação feita pelo grade ficaria inútil. A busca traz somente o que falta para responder.

### Dois cuidados do prompt tratam de falhas das páginas:

segue para os outros, sem derrubar o nó inteiro. TTL: a informação da web tem prazo de validade Cada registro vindo da web guarda quando a informação foi buscada e quando ela expira.

- Timeout: se a página demorar, o processo inteiro não trava.
- Página com falha: se a página estiver fora do ar ou estourar o timeout, o nó ignora aquele resultado e

### TTL

TTL é time to live, o tempo de vida: a data de validade da informação. No projeto, ele é definido em dias, com sete como padrão.

O prazo existe porque as duas fontes têm naturezas diferentes. A informação da CVM é estática: é a informação daquela época. Correções são bem raras, e o que acontece é a agregação dos resultados da empresa nos trimestres seguintes. Uma notícia ou o resultado de uma busca, ao contrário, pode deixar de ser válido. Sem o prazo, o agente recuperaria sempre a notícia antiga, porque na vez seguinte ele a encontraria no RAG, e o usuário ficaria com uma informação imprecisa. A informação da web também é menos confiável. Isso não quer dizer que ela não é confiável: ela é menos confiável do que a informação oficial da CVM.

### Critério Corpus da CVM Documentos da web

Natureza Estática e perene: é a informação daquela época, e correções são raras. Notícias e buscas, que podem deixar de ser válidas.

### Confiabilidade Informação oficial. Menos confiável do que a informação oficial da

CVM. Validade no banco Não expira. Recebe data de busca e data de expiração, calculada por um TTL em dias.

### Na busca do retrieve Sempre consultado. Consultado com filtro no WHERE: só entram os

O TTL é aplicado na consulta: quando o Postgres é consultado, a query só traz os registros que não expiraram. Um serviço agendado, um cron, poderia limpar as informações antigas para a base não acumular registros, mas a validade em si é garantida pelo filtro.

## Pontos de atenção

- ATENÇÃO  ·  Por que não enviar a pergunta inteira à busca
- Dois cuidados do prompt tratam de falhas das páginas:
- Timeout: se a página demorar, o processo inteiro não trava.
- A informação da web também é menos confiável. Isso não quer dizer que ela não é confiável: ela é menos
- Validade no banco Não expira. Recebe data de busca e data de expiração,
- O TTL é aplicado na consulta: quando o Postgres é consultado, a query só traz os registros que não expiraram.
- Um serviço agendado, um cron, poderia limpar as informações antigas para a base não acumular registros, mas

## Checkpoint

- [ ] Você consegue explicar o que o nó de busca na web faz, da montagem das queries à gravação dos chunks, sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
