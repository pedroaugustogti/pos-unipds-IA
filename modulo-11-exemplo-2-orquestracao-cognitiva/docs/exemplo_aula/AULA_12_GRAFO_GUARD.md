# Aula 12: O grafo real: aresta condicional e o guard do

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Montar o grafo do agente com LangGraph, ligando os nós retrieve, grade e web search.
- Explicar a aresta condicional que sai do grade e o limite de iterações que impede o loop infinito.
- Relacionar a simplicidade do grafo ao princípio de responsabilidade única aplicado a cada nó.

## Desenvolvimento

### Contexto da aula

Os nós retrieve, grade e web search existem, mas ainda estão soltos. Esta aula liga os três em um grafo de fim a fim, com o StateGraph do LangGraph, e fecha o loop entre eles com uma trava que o impede de rodar para sempre. Sem a trava, o agente ficaria pensando e gastando tokens. Ao final, você saberá descrever o caminho do grafo, explicar como o limite de iterações funciona dentro do próprio estado e relacionar a simplicidade do código ao modo como os nós foram desenhados.

### O caminho do grafo e a aresta condicional

Um grafo é feito de nós interligados, como os que se estudam para calcular a rota mais simples. No agente, a regra de negócio é o caminho de um nó para o outro, definido pelas arestas. O caminho é este: do início, o START, a execução vai para o retrieve e, dele, para o grade. Do grade sai uma aresta condicional, com três resultados possíveis:

O web search não termina o grafo nem avalia nada. Ele volta para o retrieve, que busca de novo as informações, e o grade verifica outra vez se o contexto é suficiente.

- se sufficient for verdadeiro, o grafo termina;
- se iterations já atingiu MAX_ITERATIONS, que é 2, o grafo também termina;
- caso contrário, a execução vai para o web search, que sempre volta para o retrieve.

### A tabela a seguir resume as arestas:

De Para Quando START retrieve Sempre: é o início do grafo. retrieve grade Sempre: o contexto recuperado é avaliado. grade END Se sufficient for verdadeiro, ou se iterations já atingiu MAX_ITERATIONS, que é 2. grade web search Caso contrário: o contexto é insuficiente e ainda há iterações disponíveis. web search retrieve Sempre: o web search não termina o grafo nem avalia, ele volta para a busca.

### O guard do loop: um contador dentro do estado

O limite de iterações é o que impede o grafo de rodar o loop indefinidamente. Se o contexto continua insuficiente, o agente passa pela busca uma segunda vez. Na terceira, o guard impede, e o agente fica com a informação que tem.

### Contador no estado

O campo iterations faz parte do estado e soma 1 a cada passada pelo grade, por meio de um reducer. Não há contador externo: o valor viaja com o estado, que passa de um nó para outro, como a pergunta e o campo que diz o que falta para a resposta.

### O prompt que monta o grafo

O grafo é montado com um prompt um pouco grande. As instruções poderiam estar em uma skill, para serem reaproveitadas, mas vale vê-las completas:

### Prompt enviado ao Claude Code

Monte o grafo de verdade com @langchain/langgraph (StateGraph) em src/graph.ts, ligando os nós retrieve, grade e webSearch que já existem: START → retrieve → grade, e uma aresta condicional a partir de grade — se sufficient for true, termina (END); senão, se iterations já bateu MAX_ITERATIONS = 2, também termina; caso contrário, vai pro webSearch, que sempre volta pro retrieve. iterations é um campo do estado que soma 1 a cada passada por grade via reducer, sem contador externo. GraphDeps recebe as dependências de nó por função (buscar, inserirDocumentoWeb, etc.), não o cliente de banco direto, pra o grafo inteiro ser testável com fakes. Teste com app.stream(), coletando a sequência de nós visitados: caminho direto quando suficiente na primeira rodada, o loop completo quando insuficiente, e o guard cortando exatamente em MAX_ITERATIONS rodadas de grade mesmo que o LLM fake sempre devolva insuficiente.

### Além do caminho e do contador, o prompt define dois pontos:

inserir documento da web, e não o cliente de banco direto. É a inversão de dependência de novo, para deixar o grafo o mais fracamente acoplado possível e testável com fakes.

direto, quando o contexto é suficiente na primeira rodada; o loop completo, quando é insuficiente; e o guard cortando exatamente em MAX_ITERATIONS rodadas de grade, mesmo que a LLM fake devolva sempre insuficiente. Na execução, o Claude Code usa a skill langgraph-node, pede autorização para adicionar a dependência do LangChain, cria e executa os testes unitários e passa o lint.

- Dependências por função: o GraphDeps recebe as dependências dos nós por função, como buscar e
- Testes: feitos com app.stream(), coletando a sequência de nós visitados, em três cenários: o caminho

### O arquivo graph.ts define o grafo em cerca de 60 linhas, com estas partes:

iterations. O estado passa de nó em nó e é incrementado a cada um.

registra os três com addNode e adiciona as arestas. Do START para o retrieve, do retrieve para o grade, do grade para a função condicional e do web search para o retrieve.

Para rodar os testes, o ponto de exclamação executa o comando sem consumo de tokens. É como abrir uma nova aba no terminal e rodar o comando ali.

- A constante de máximo de iterações.
- O objeto de estado: a pergunta, os documentos, a indicação de contexto suficiente, o missingAspects e o
- A interface das dependências.
- A função condicional: executada depois do grade, ela termina o grafo se o estado está suficiente ou se as
- A função que constrói o grafo: cria o retrieve, o grade e o web search, cada um com os seus parâmetros,
- O compile, no final, que fecha a definição do grafo.

## Pontos de atenção

- O web search não termina o grafo nem avalia nada. Ele volta para o retrieve, que busca de novo as
- web search retrieve Sempre: o web search não termina o grafo nem avalia, ele
- O campo iterations faz parte do estado e soma 1 a cada passada pelo grade, por meio de um reducer. Não há
- nó por função (buscar, inserirDocumentoWeb, etc.), não o cliente de banco direto, pra o grafo inteiro
- inserir documento da web, e não o cliente de banco direto. É a inversão de dependência de novo, para
- o web search só faz a busca na web e adiciona informações ao RAG. Ele não avalia: volta para o retrieve.
- O fundamento não muda com a ferramenta

## Checkpoint

- [ ] Você consegue explicar o caminho que o grafo percorre do START até o END sem consultar o material?
- [ ] Você consegue explicar como a aresta condicional e o campo iterations impedem que o agente rode para

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
