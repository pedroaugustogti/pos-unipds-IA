# Aula 16: Erros padronizados

> Unidade 3 — Qualidade, Resiliência e MCP · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar por que os erros de uma API devem ser tratados em um ponto central e devolvidos em um contrato padronizado.
- Criar um error handler único, que mapeia erros de validação, de circuito aberto e genéricos sem vazar detalhes internos.
- Avaliar o trade-off entre criar uma dependência entre pacotes e identificar um erro por duck typing.

## Desenvolvimento

### Contexto da aula

Em uma aplicação production-ready, é preciso decidir como um erro chega ao cliente, seja o corpo inválido de uma requisição, seja um erro que ninguém previu. Se cada rota trata o erro do seu jeito, sem padrão, a experiência do usuário fica ruim. Esta aula cria um tratamento único, que captura todos os erros da aplicação em um ponto só, em vez de espalhá-lo pelas rotas. É sobre esse ponto que entram depois a telemetria e os demais controles. Ao final, você saberá montar um error handler central, explicar o contrato de erro adotado e avaliar a decisão de identificar um erro por duck typing. Um error handler central no lugar do tratamento por rota O error handler é uma função de tratamento de erro unificada, no app.ts. Ela recebe o app como parâmetro, e qualquer exceção levantada pelos endpoints é tratada ali. O projeto tem só duas rotas por enquanto, mas, com mais rotas, todos os erros continuariam unificados nessa função.

- Criar um error handler único, que mapeia erros de validação, de circuito aberto e genéricos sem vazar detalhes
- Avaliar o trade-off entre criar uma dependência entre pacotes e identificar um erro por duck typing.

### Prompt enviado ao Claude Code

Hoje cada rota da API trata erro do seu próprio jeito, sem padrão. Quero um error handler central, registrado uma única vez com app.setErrorHandler() — nenhuma rota deve tratar erro por conta própria. Mapeia ZodError pra 400, CircuitoAbertoError (do SearchProvider, já existe em @hero/agent) pra 503, e qualquer outro erro pra 500 genérico, sem vazar detalhe interno tipo stack trace. O formato da resposta é RFC 7807 — application/problem+json, com type/title/status/detail — define esse schema em packages/contracts, porque o frontend também vai precisar dele quando chegar a hora de mostrar erro na tela.

O handler é registrado uma única vez, com o setErrorHandler da aplicação, e nenhuma rota trata erro por conta própria. Ele analisa o problema, pega o detalhe e trata três casos:

### Tipo de erro Quando acontece Como é identificado

ZodError O consumidor envia um parâmetro errado na requisição. Por instanceof.

### Erro de circuito aberto O Serper falha repetidamente e o circuit

breaker abre. Por duck typing: é um Error com o nome do erro de circuito aberto.

### Qualquer outro erro Um erro que ninguém previu. Cai no tratamento genérico, sem vazar

Com o handler pronto, os tratamentos antigos saem das rotas, como o que devolvia o código 400. O código das rotas fica mais simples, principalmente no caso dos erros do Zod, de validação dos parâmetros de entrada da API. Não vazar detalhes internos O erro genérico não leva detalhes internos, como o stack trace. É uma questão de segurança.

### ATENÇÃO — O stack trace não vai para o cliente externo

A telemetria fica nos serviços internos, onde quem enxerga é a própria equipe. O cliente externo recebe somente a informação necessária para tratar o problema, por exemplo com uma tela de erro específica. Uma pessoa mal- intencionada pode usar o stack trace para analisar o que acontece nos servidores e explorar essa informação.

O contrato de erro: RFC 7807 A resposta de erro segue o formato da RFC 7807, um formato padrão, com os campos type, title, status e detail. O schema fica no pacote de contratos, de onde é exportado. O contrato atende a dois consumidores:

outros agentes. Um agente consegue entender o contexto de um erro sem padrão, mas, com o erro padronizado, ele o trata gastando muito menos tokens e com muito mais efetividade. Dependência nova ou duck typing Durante a execução do prompt, o Claude Code parou para perguntar, porque encontrou um conflito entre o pedido e a arquitetura. O pacote da API não depende do pacote do agente. Depende só de contratos, do Fastify e do pg. Isso é deliberado: a rota de chat recebe o grafo por um tipo estrutural, em vez de importar os tipos reais do grafo, para manter a API testável sem LLM e sem Postgres. As dependências são fracamente acopladas. Além disso, o erro de circuito aberto só é exportado pelo módulo de busca, e não pelo índice público do pacote do agente. Uma verificação com instanceof exigiria duas mudanças: adicionar o pacote do agente como dependência da API e reexportar o erro no índice público. E instalar uma dependência nova é exatamente o que o CLAUDE.md manda perguntar antes de fazer. O agente apresentou duas saídas: refatorar o projeto, criando a dependência, ou usar duck typing pelo nome do erro.

- O frontend: é um acordo. Todo erro devolvido pelo backend vem nesse formato, e o frontend pode mostrá-
- Outros agentes: hoje há muito mais agentes monitorando sistemas e, com MCP, agentes consumindo

### Duck typing

Em vez de um tipo exportado e verificável, o erro é reconhecido pelas suas características. Aqui, a verificação é que o objeto é uma instância de Error e que o nome dele é o do erro de circuito aberto.

Mantive o duck typing, porque a prioridade é conservar as dependências como estão e continuar testando sem LLM e sem Postgres.

- Duck typing: mantém o acoplamento fraco. Em troca, se o nome da exceção mudar, a verificação quebra,
- Dependência nova: permite o instanceof, mas acopla a API ao pacote do agente.

### EM SÍNTESE

No dia a dia, vale conversar mais com o agente, no Claude Code ou em outra ferramenta, para verificar as alternativas e os riscos antes de decidir.

Testando com a aplicação no ar O tratamento pode ser conferido com a aplicação rodando, e não só com teste unitário: 1. Suba só a API local. 2. Faça uma requisição com curl a uma rota que não existe. A resposta volta no formato unificado: uma mensagem de rota POST não encontrada, com o status 404. 3. Envie um body vazio à rota de chat e verifique se o erro retornado está no formato do contrato. Na demonstração, o terceiro passo foi pedido ao Claude Code, que subiu o servidor internamente e fez o teste pela própria aplicação. A aplicação didática tem só dois endpoints, mas a técnica facilita muito quando o assunto passa a ser volume, observabilidade e telemetria.

## Pontos de atenção

- O erro genérico não leva detalhes internos, como o stack trace. É uma questão de segurança.
- ATENÇÃO  ·  O stack trace não vai para o cliente externo
- O pacote da API não depende do pacote do agente. Depende só de contratos, do Fastify e do pg. Isso é
- Além disso, o erro de circuito aberto só é exportado pelo módulo de busca, e não pelo índice público do pacote
- alternativas e os riscos antes de decidir.
- O tratamento pode ser conferido com a aplicação rodando, e não só com teste unitário:
- 2. Faça uma requisição com curl a uma rota que não existe. A resposta volta no formato unificado: uma

## Checkpoint

- [ ] Você consegue explicar por que o tratamento de erros deve ficar em um ponto central e seguir um contrato sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
