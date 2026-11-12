# Aula 19: Chat com streaming e citações clicáveis

> Unidade 4 — Frontend · Capstone AI Researcher

## Objetivos de aprendizagem

- Conectar a casca estática do chat ao backend, com roteamento, um serviço que lê o stream de eventos e um store que guarda as mensagens.
- Explicar o truque de frontend que revela a resposta palavra por palavra para dar fluidez ao streaming.
- Formatar as citações da resposta, diferenciando a base local da CVM das fontes da web.

## Desenvolvimento

### Contexto da aula

A casca do chat existe, mas não faz nada: nenhum componente conversa com o backend. Esta aula conecta a tela à API e começa a moldar a experiência do usuário. O trabalho é dividido em peças pequenas, cada uma com o seu prompt: as rotas, o serviço que lê o stream, o store que guarda as mensagens, a função que formata as citações e, por fim, a ligação de tudo no componente. Ao final, você saberá explicar o papel de cada peça e por que a resposta é exibida palavra por palavra. As peças do chat no frontend A tabela a seguir apresenta as peças e o papel de cada uma: Peça Papel Rotas A rota vazia abre o chat e a rota de health mostra o status, com o router outlet no lugar do componente fixo. ChatService Faz o POST para a API de chat, lê o stream da resposta e entrega os eventos do grafo; lança exceção se o evento for de erro. ChatStore Adiciona a mensagem do usuário e o placeholder do assistente e revela a resposta palavra por palavra, a cada 70 milissegundos. parseAnswer Separa o corpo da resposta do bloco de fontes e monta as citações: base local da CVM com período, ou o host da URL. Componente Chat Liga a textarea e o botão de envio ao store e renderiza as mensagens e as citações.

Roteamento: o chat vira a página inicial Por padrão, a aplicação abria a página de health check, e não o chat. O primeiro prompt corrige isso com uma refatoração simples, só do frontend:

- Explicar o truque de frontend que revela a resposta palavra por palavra para dar fluidez ao streaming.
- Formatar as citações da resposta, diferenciando a base local da CVM das fontes da web.

### Prompt enviado ao Claude Code

No projeto Angular já existente em apps/web, adicione roteamento com @angular/router (já é dependência).

### Crie src/app/app.routes.ts com duas rotas: '' aponta pro componente Chat, e 'health' aponta pra um

componente novo Health em src/app/health/, reaproveitando o HealthService que já existe desde o Bloco C pra mostrar o texto de status que hoje está solto em app.html. Registre as rotas em app.config.ts com provideRouter. Troque app.html pra só <router-outlet />, e app.ts pra importar RouterOutlet em vez do Chat direto.

A aplicação usa standalone components, e por isso não há módulos Angular. Um bug escondido na rota /chat A mudança do MCP deixou um bug que passou despercebido: a rota /chat da API passou a responder só pelo grafo falso, que não chega ao Vertex AI nem ao Postgres.

- o arquivo de rotas, com a rota vazia apontando para o chat e a rota de health para um componente novo;
- o componente de health, que reaproveita o serviço de health já existente para mostrar o texto de status que
- o provider do router registrado na configuração da aplicação;
- o router outlet no lugar em que o componente ficava direto.

### Prompt enviado ao Claude Code

apps/api/src/routes/chat.ts ainda recebe graph: GraphLike já resolvido. Troque pra receber getGraph: GetGraph, resolvendo com await getGraph() dentro do handler, do mesmo jeito que packages/mcp-server já faz. Em apps/api/src/app.ts, renomeie as opções de build() pra getChatGraph e getMcpGraph. Em apps/api/src/index.ts, passe getRealGraph (de @hero/agent) pras duas — a mesma função memoizada, senão /api/chat e /api/mcp acabam com Postgres/Vertex AI/circuit breaker duplicados.

A rota passa a receber o getGraph e a resolvê-lo com await dentro do handler, como o servidor MCP já faz. As opções de build separam o grafo do chat do grafo do MCP, e as duas recebem a mesma função memoizada.

### ATENÇÃO — A mesma função memoizada nas duas rotas

Com o agente memoizado, não importa se a chamada vem do MCP ou do /chat: se ele já está instanciado, é reutilizado. Os mecanismos de resiliência continuam funcionando e não ficam duplicados.

ChatService: quem conversa com o backend é o serviço No padrão correto do Angular, quem interage com o backend nunca é o componente gráfico. É um serviço, que concentra a regra de negócio e toda a lógica de integração.

### No projeto Angular já existente em apps/web, crie um ChatService em src/app/api/chat.service.ts. Um

método ask(question) que faz POST /api/chat, lê o ReadableStream do corpo da resposta e produz um AsyncGenerator dos eventos do grafo (retrieve, grade, webSearch, answer). O formato dos frames é o mesmo que apps/api/src/routes/chat.ts escreve: blocos separados por linha em branco, data: com o JSON do evento. Se o evento for error, lance uma exceção com a mensagem.

O formato dos frames é o mesmo que a rota de chat escreve: blocos separados por linha em branco, com data: e o JSON do evento. O Claude Code cria o serviço usando a skill do Angular. Como há um contrato novo, ele o coloca no pacote de contratos, o lugar correto, em vez de deixá-lo no projeto web. Assim o mesmo contrato serve ao Angular e ao backend.

- faz o POST para a API de chat, com um fetch;
- lê o stream do corpo da resposta;
- produz um async generator dos eventos do grafo;
- lança uma exceção com a mensagem quando o evento é de erro.

### Três detalhes do Angular atual aparecem nesse código:

porque, quando o projeto foi desenvolvido, ainda não tratava retorno por stream. ChatStore: a resposta revelada palavra por palavra O frontend recebe a resposta do agente por streaming, mas os chunks não chegam de forma regular. Mostrar os dados conforme chegam deixa o texto truncado, diferente do que o ChatGPT e o Gemini fazem.

- inject: nas versões mais recentes, a forma antiga de construir e injetar serviços deu lugar à função
- Observable: não é mais obrigatório. Ele não morreu, mas, principalmente com a API de signals, a
- Resource: é o recurso próprio do Angular para essa integração, baseado em signal. Ele não foi usado

### O truque da digitação fluida

O frontend guarda a resposta conforme a recebe, como um buffer, e a solta na tela palavra por palavra, a 70 milissegundos por palavra. O truque não é obrigatório: serve para dar a sensação de UX do modelo respondendo de um jeito fluido.

### Prompt enviado ao Claude Code

Crie um ChatStore em src/app/state/chat-store.ts. send(question) adiciona a mensagem do usuário e um placeholder do assistente, chama ChatService.ask, e quando chegar o evento do nó answer, revela o texto palavra por palavra (70ms por palavra) — com um helper tokenize separado. Se a chamada falhar, mostra uma mensagem de erro fixa, sem streaming. Limpe qualquer timer pendente ao destruir o store.

O store adiciona a mensagem do usuário e um placeholder do assistente, chama o ask do serviço e, quando chega o evento do answer, revela o texto palavra por palavra. Se a chamada falhar, o store mostra uma mensagem de erro fixa, sem streaming. É esse cuidado que evita que um erro simplesmente estoure na tela. Citações: de onde veio cada informação As citações aparecem abaixo da resposta e dizem de onde veio a informação. Uma função as extrai do texto e as formata:

## Pontos de atenção

- A casca do chat existe, mas não faz nada: nenhum componente conversa com o backend. Esta aula conecta a
- Por padrão, a aplicação abria a página de health check, e não o chat. O primeiro prompt corrige isso com uma
- A aplicação usa standalone components, e por isso não há módulos Angular.
- grafo falso, que não chega ao Vertex AI nem ao Postgres.
- ATENÇÃO  ·  A mesma função memoizada nas duas rotas
- Com o agente memoizado, não importa se a chamada vem do MCP ou do /chat: se ele já está instanciado, é
- reutilizado. Os mecanismos de resiliência continuam funcionando e não ficam duplicados.

## Checkpoint

- [ ] Você consegue explicar o papel do serviço, do store e do componente na conexão do chat com o backend sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
