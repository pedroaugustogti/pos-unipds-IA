# Aula 17: O servidor MCP

> Unidade 3 — Qualidade, Resiliência e MCP · Capstone AI Researcher

## Objetivos de aprendizagem

- Expor o agente a outros agentes por meio de um servidor MCP com uma única tool, mantendo o guardrail do lado de dentro.
- Explicar o papel da descrição da tool, que é lida pelo cliente MCP para decidir quando chamá-la.
- Diferenciar o transporte stdio, usado localmente, do Streamable HTTP, usado em um servidor, e compartilhar a mesma instância do grafo entre as rotas.

## Desenvolvimento

### Contexto da aula

O chat não é a única forma de interagir com o agente. Outra forma, hoje muito comum, é o protocolo MCP, que deixa o sistema disponível para outros agentes utilizarem. Esta aula expõe o grafo por um servidor MCP, primeiro para uso local, por stdio, e depois para uso em um servidor, por Streamable HTTP. Ao final, você saberá decidir o que expor por MCP, escrever a descrição de uma tool e explicar por que as duas portas de entrada do agente compartilham o mesmo grafo. Uma única tool: a experiência do agente Em MCP, como em uma API, pensa-se na experiência de quem consome. Só que aqui é a experiência do agente. Seria possível expor o grafo inteiro para um agente consumir. O risco é esse agente não aplicar o guardrail e usar o sistema para uma operação para a qual ele não foi feito. Por isso o servidor MCP abstrai o sistema para o agente externo e oferece uma função só: o agente pergunta, e o sistema responde. O que acontece da porta para dentro não interessa a quem consome.

- Explicar o papel da descrição da tool, que é lida pelo cliente MCP para decidir quando chamá-la.
- Diferenciar o transporte stdio, usado localmente, do Streamable HTTP, usado em um servidor, e compartilhar a

### EM SÍNTESE

Não se abre todo o sistema por MCP. Abre-se só o que faz sentido, na mesma lógica da API: ninguém transforma todas as funções do backend em APIs.

### Servidor e tool: os elementos de um MCP

O SDK do Model Context Protocol é uma biblioteca própria para expor um backend no protocolo MCP. No projeto o backend é um agente, mas vale para qualquer backend.

### Publicar um MCP exige duas coisas:

- Um servidor, criado com a classe de servidor do SDK.
- Uma tool registrada. Em MCP não há endpoints, há tools.

### Tool

Uma tool é um nome, um título, uma descrição, um schema e a função que executa a partir da entrada enviada pelo agente que consome o MCP.

### No arquivo perguntar.ts, esses elementos aparecem como constantes:

caso de erro, responde com a mensagem de erro e com o indicador de erro verdadeiro. A descrição da tool é lida pelo agente A descrição da tool não é documentação para humano. Ela é lida pelo cliente MCP, que a usa para decidir quando chamar a tool e quando não chamar. Quando uma tool é instalada, o agente a coloca no contexto. Diante de um prompt, ele raciocina e, se entender que a tool é importante para a resposta, a aciona. Por isso a descrição precisa deixar claro o domínio e repetir o guardrail. A descrição da tool perguntar informa:

empresas listadas na B3, com base em dados públicos da CVM;

fatos publicados e nunca dá conselho de investimento;

- Nome: perguntar.
- Schema de entrada: só a pergunta, com a indicação de que é sobre os indicadores financeiros.
- Resultado: o conteúdo, que é um texto, e o indicador de erro, verdadeiro ou falso.
- Função: recebe a pergunta, obtém o grafo, o mesmo usado pelo chat, manda processar e responde. Em
- que ela responde a perguntas sobre indicadores financeiros, como receita líquida e lucro líquido, de 20
- que, quando o contexto do corpus não é suficiente, ela busca na web;
- que toda resposta cita a fonte e o período do dado;
- que ela nunca recomenda comprar, vender ou manter uma posição em um ativo. Só informa números e
- que não é uma tool de consultoria. Pedidos de opinião, sugestão ou recomendação são recusados pela

### Prompt enviado ao Claude Code

Cria packages/mcp-server, um servidor MCP com uma única tool, perguntar: recebe uma pergunta em texto e roda o grafo inteiro que já existe em packages/agent — retrieve → grade → webSearch → answer — devolvendo a resposta final, já citada e com guardrail aplicado. A descrição da tool é lida pelo cliente MCP pra decidir quando chamar — não é documentação pra humano — então precisa deixar claro o domínio (20 empresas da B3, dados da CVM) e repetir o guardrail (nunca recomenda). O grafo é recebido por parâmetro (GetGraph), mesmo padrão de injeção de dependência do resto do projeto, pra testar com fake sem tocar Postgres nem Vertex AI — usa o InMemoryTransport do próprio SDK do MCP pra testar o servidor inteiro. Se o grafo falhar, a tool nunca deixa a exceção crua vazar — devolve isError: true com uma mensagem genérica, mesma filosofia de degradação graciosa da E.6. A construção do grafo real (Postgres + Vertex AI) — incluindo os clients de embeddings, grade e answer, que ainda não existem como módulo reutilizável — deve morar dentro de packages/agent, memoizada por processo: o transporte HTTP desta mesma aula vai precisar exatamente da mesma função. Constrói o grafo real só na primeira chamada, nunca na inicialização do processo. Sobe primeiro o transporte stdio, pro claude mcp add.

### Além da tool e da sua descrição, o prompt define:

fake, sem tocar no Postgres nem no Vertex AI. O servidor inteiro é testado com o InMemoryTransport do próprio SDK do MCP.

com uma mensagem genérica, na mesma filosofia da degradação graciosa.

embeddings, grade e answer, que ainda não existiam como módulo reutilizável. O projeto é refatorado para o MCP consumir o agente.

processo. Se for preciso usá-lo de novo e ele já estiver na memória, usa-se o que está lá. O transporte HTTP precisa exatamente dessa mesma função.

- Grafo por parâmetro: o mesmo padrão de injeção de dependência do resto do projeto, para testar com
- Falha sem vazamento: se o grafo falhar, a tool nunca deixa a exceção crua vazar. Devolve isError: true
- Construção do grafo real no pacote do agente: com Postgres e Vertex AI, incluindo os clientes de
- Memoização por processo: o grafo é instanciado na primeira chamada, nunca na inicialização do
- Transporte stdio primeiro.

### stdio

É a interface local de texto, de entrada e saída de strings: a própria interface do console. Nesse transporte, o que se expõe é basicamente um script, consumido localmente.

## Pontos de atenção

- O chat não é a única forma de interagir com o agente. Outra forma, hoje muito comum, é o protocolo MCP, que
- Seria possível expor o grafo inteiro para um agente consumir. O risco é esse agente não aplicar o guardrail e
- usar o sistema para uma operação para a qual ele não foi feito.
- o sistema responde. O que acontece da porta para dentro não interessa a quem consome.
- Não se abre todo o sistema por MCP. Abre-se só o que faz sentido, na mesma lógica da API: ninguém transforma
- Uma tool registrada. Em MCP não há endpoints, há tools.
- A descrição da tool não é documentação para humano. Ela é lida pelo cliente MCP, que a usa para decidir

## Checkpoint

- [ ] Você consegue explicar por que o servidor MCP expõe uma única tool em vez de abrir todo o grafo sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
