# Aula 9: Os nós retrieve e grade

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Construir o nó retrieve, que transforma a pergunta em embedding e busca no Postgres os documentos mais similares.
- Justificar por que padrões de projeto, como a inversão de dependência, continuam importantes quando quem escreve o código é um agente.
- Construir o nó grade, que usa saída estruturada da LLM e uma regra explícita para julgar se o contexto recuperado é suficiente.

## Desenvolvimento

### Contexto da aula

Com o banco vetorial criado e carregado, começa a construção do backend do agente. De forma bem simples, o agente é formado por partes chamadas nós, como os nós de uma rede. Esta aula constrói os dois primeiros. O nó retrieve faz a busca: pega a pergunta, transforma em embedding e consulta o banco de dados para achar os conteúdos que a respondem. O nó grade julga se o que voltou dessa busca é suficiente para responder. Ao final, você saberá ler o código dos dois nós, explicar por que eles recebem as suas dependências por parâmetro e descrever a regra que decide quando o agente precisa buscar informação fora da base.

- Justificar por que padrões de projeto, como a inversão de dependência, continuam importantes quando quem
- Construir o nó grade, que usa saída estruturada da LLM e uma regra explícita para julgar se o contexto

### O nó retrieve: da pergunta aos documentos mais próximos

O nó retrieve recebe a pergunta do estado, gera o embedding dela e busca no Postgres os documentos mais próximos. Ele devolve o top-k, que por padrão são os cinco mais similares.

### Prompt enviado ao Claude Code

Crie o nó retrieve do grafo em packages/agent/src/nodes/retrieve.ts. Ele recebe a pergunta do estado, gera o embedding dela e busca os documentos mais próximos no Postgres, top-k com default 5. Siga a convenção do projeto: o nó não importa nenhum cliente global — ele é uma factory que recebe um cliente de embeddings e uma função de busca por parâmetro, pra ser testável com fake, sem chamada real de rede ou banco. Crie também a função de busca em packages/agent/src/db/retrieve-similar.ts, usando o operador de distância de cosseno do Drizzle.

### Além do comportamento do nó, o prompt pede duas coisas de design de código:

parâmetro um cliente de embeddings e uma função de busca.

cosseno do Drizzle. No código gerado, o top_k é uma constante com valor 5, e o nó faz algo muito simples: gera o embedding da pergunta e o envia à função de busca. A função de busca usa o Drizzle, que tem suporte a busca vetorial, para calcular a distância entre o embedding da pergunta e os dos documentos. Para o entendimento, pense na distância em um plano cartesiano, embora os embeddings tenham muito mais dimensões.

- Convenção do projeto: o nó não importa nenhum cliente global. Ele é uma factory que recebe por
- Função de busca separada: ela fica no arquivo retrieve-similar.ts e usa o operador de distância de

### Similaridade

A consulta calcula a distância com uma função do Drizzle ORM e, por convenção, obtém a similaridade como 1 menos a distância. Em SQL puro no Postgres, a mesma consulta usaria os operadores de distância apresentados na Aula 8.

Inversão de dependência: o nó recebe o cliente por parâmetro Receber o cliente de embeddings e a função de busca por parâmetro é a inversão de dependência aplicada ao código do agente. Ela resolve dois problemas:

manual, a aplicação usa o embedding do Gemini. No teste unitário, o nó recebe um fake. O teste unitário do retrieve cria um embedding falso, que já devolve os valores, e monta o cenário para testar a lógica. Ele roda sem o banco de dados e sem o Vertex AI no ar. No Claude Code, um comando iniciado por ponto de exclamação roda ali mesmo, sem trocar de aba. Na demonstração, o teste foi filtrado para rodar só o retrieve, e não os testes unitários de todo o projeto.

- Troca de fornecedor: para deixar de usar o embedding do Gemini e passar a usar o da OpenAI, por
- Teste independente: o teste unitário não pode depender do Vertex AI. Em um teste de QA ou em um teste

### Por que padrões de projeto importam mais com agentes

É um erro pensar que, como o agente escreve o código, o padrão de projeto deixou de importar. Hoje os padrões de projeto são mais importantes do que nunca, por dois motivos. O primeiro é o custo. Quanto menos o agente tiver de mudar no projeto, mais barato sai. Antes, os bons padrões reduziam um custo de tempo e um custo de comunicação. Com a IA, o custo é financeiro. O segundo é a revisão. O grande problema hoje é a análise de PR, ou seja, a análise do que o agente cria. Uma refatoração, feita por um agente ou por uma pessoa, tem de ser cirúrgica. Reescrever todo o código não é uma opção.

### EM SÍNTESE

Vale pensar em padrões de código para o projeto e vale estudá-los. Não é verdade que basta fazer um bom prompt.

Há ainda a questão do modelo. O projeto foi desenvolvido com o Claude e o modelo Sonnet, mas você pode estar usando um modelo mais fraco ou um modelo local. Quanto mais padrões de projeto forem descritos, melhor fica o código. Skills e a responsabilidade de ler o código Ao executar o prompt do retrieve, o Claude Code chama a skill langgraph-node. Criei essa skill antes, para explicar o padrão que quero no uso do LangGraph na construção do agente. Sem uma skill para o Drizzle, o agente lê o código da biblioteca para montar a busca. Criar ou buscar uma skill para o Drizzle pouparia esse trabalho.

### ATENÇÃO — Ler o código é responsabilidade sua

O agente pode criar o código e pode ajudar a debugar. Ler o código continua sendo responsabilidade de quem desenvolve. Por isso ferramentas como o Prettier seguem necessárias: o código não é lido só pelo agente.

### Por que o agente precisa julgar o contexto

O retrieve traz o contexto, mas ter o contexto não basta. Nem sempre a informação que está no RAG é suficiente para a pergunta. A base foi montada com os dados da CVM, normalizados e carregados no banco. Se a pergunta do usuário é respondida por esses dados, o agente responde sem buscar na internet. Se a pergunta é mais aberta, o agente precisa avaliar se o contexto é suficiente e, quando não for, buscar na internet. Essa avaliação é um processamento próprio do agente: o nó grade. Pedir a uma LLM que responda em texto livre se o contexto é suficiente pode trazer problemas, e por isso o nó usa saída estruturada.

## Pontos de atenção

- Justificar por que padrões de projeto, como a inversão de dependência, continuam importantes quando quem
- convenção do projeto: o nó não importa nenhum cliente global — ele é uma factory que recebe um cliente
- Convenção do projeto: o nó não importa nenhum cliente global. Ele é uma factory que recebe por
- Teste independente: o teste unitário não pode depender do Vertex AI. Em um teste de QA ou em um teste
- demonstração, o teste foi filtrado para rodar só o retrieve, e não os testes unitários de todo o projeto.
- padrões de projeto são mais importantes do que nunca, por dois motivos.
- Uma refatoração, feita por um agente ou por uma pessoa, tem de ser cirúrgica. Reescrever todo o código não é

## Checkpoint

- [ ] Você consegue explicar o que o nó retrieve faz com a pergunta do usuário e como a similaridade é calculada

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
