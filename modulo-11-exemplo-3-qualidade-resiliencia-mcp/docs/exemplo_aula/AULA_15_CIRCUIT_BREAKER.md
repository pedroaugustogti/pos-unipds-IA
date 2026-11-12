# Aula 15: Circuit breaker, retry e degradação graciosa

> Unidade 3 — Qualidade, Resiliência e MCP · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar o que timeout, retry com backoff e circuit breaker resolvem quando um serviço de terceiro falha.
- Aplicar o padrão decorator para acrescentar resiliência ao provedor de busca sem reescrever cada implementação.
- Implementar a degradação graciosa no nó de busca na web e avaliar em quais regras de negócio ela faz sentido.

## Desenvolvimento

### Contexto da aula

O modo demo resolve o desenvolvimento e as demonstrações, mas não a produção. Em produção, a flag está desligada, e o Serper está no ar de verdade, o que inclui os dias em que ele não está. API de terceiro cai, tem pico de latência e estoura limite. Esta aula trata de como tornar o sistema resiliente a essas falhas, sem impactar tanto a experiência do usuário. O sistema não responde da mesma maneira quando um serviço falha, mas também não precisa mostrar uma tela branca. São três camadas de proteção no provedor de busca, timeout, retry com backoff e circuit breaker, e mais a degradação graciosa no grafo. Ao final, você saberá explicar o problema que cada uma resolve e decidir quando uma falha deve ser contornada e quando deve ser uma falha. Timeout: um erro claro em vez de uma espera sem fim Por padrão, um fetch não tem timeout. Ele fica no ar pelo tempo que for preciso esperar pela resposta. Se o Serper travar no meio de uma resposta, a requisição toda trava junto, e o usuário fica olhando para a tela. É melhor mostrar um erro, pedindo para tentar de novo ou tentar mais tarde, do que deixar a requisição executando sem que o usuário saiba se o problema é a conexão dele, o computador dele ou outra coisa. O timeout dá um erro muito claro. Retry com backoff: a falha pode ser passageira Às vezes o serviço não saiu do ar indefinidamente. Houve só um pico de requisições, algo intermitente no serviço de terceiro. O retry responde a esse caso. Em vez de devolver o erro ao usuário ou de ficar esperando, o sistema cancela a conexão e tenta novamente. Muitas vezes isso resolve e, dependendo de como o frontend é desenvolvido, fica transparente para o cliente.

- Implementar a degradação graciosa no nó de busca na web e avaliar em quais regras de negócio ela faz

### Circuit breaker: parar de insistir em quem está se recuperando

Um retry mal implementado gera outro problema, a falha em massa. O serviço caiu de maneira intermitente e está se levantando, ainda sem condições de atender. Se o sistema insiste, retry atrás de retry, acaba derrubando o serviço de terceiro que tentava se recuperar.

### Circuit breaker

O circuito abre depois de algumas falhas consecutivas. Quando uma nova tentativa, automática ou não, é bem- sucedida, o circuito fecha de novo e volta a operar. O mecanismo protege ao mesmo tempo o serviço externo e a latência do próprio sistema.

Essas são algumas das técnicas de resiliência de sistemas. Há várias outras. Os conceitos da engenharia de sistemas clássica continuam funcionando nos sistemas agênticos, cada vez mais. Não há mistério nos sistemas que usam LLM.

### Onde esses padrões se aplicam

No projeto, as proteções são aplicadas ao Serper, mas o mesmo tratamento serve ao Vertex AI ou ao banco de dados. É o caso clássico do circuit breaker: não adianta insistir em um terceiro cujo serviço está tentando subir. Circuit breaker e retry com backoff são muito usados em microsserviços. O projeto não tem microsserviços: o único serviço externo de busca é o Serper. Em um sistema grande, com muitos microsserviços, esses padrões são muito comuns e muito necessários. O padrão decorator: resiliência sem reescrever os providers Os padrões de projeto não morreram. Ficaram mais importantes. Uma leitura recomendada é o livro de padrões de projeto do Gang of Four, um clássico.

### ATENÇÃO — Primeiro o problema, depois o padrão

A ordem é achar o problema e depois o padrão de projeto que o resolve, e não o inverso. É comum se empolgar com padrão de projeto.

O problema aqui é aplicar o mesmo comportamento de resiliência a duas funções, a do Serper e a do Google Custom Search, sem reescrever as duas.

### Um comportamento padronizado é implementado uma vez, em uma função. A função que deve receber esse

Muitos frameworks já trazem isso pronto. O NestJS tem. No mundo Java, o Spring Boot tem um módulo de resiliência: basta anotar com @CircuitBreaker, sem criar o mecanismo. O decorator não é o arroba em cima da função. O arroba, do Java ou do TypeScript, é syntax sugar, um recurso para deixar o código mais bonito. Na execução, ele faz a mesma coisa: chama uma função de uma função. No projeto, a função que cria o provider do Serper aparece envelopada pelo comResiliencia, sem a sintaxe com arroba. Essa sintaxe não é padrão do JavaScript nem do TypeScript. É uma tentativa que existe há bastante tempo e não é unanimidade. Pelo que conheço, só o NestJS e o Angular usam bastante o decorator do TypeScript. O padrão de projeto pode ser usado com ou sem o syntax sugar.

### Prompt enviado ao Claude Code

O SearchProvider (Serper e Google Custom Search) não tem nenhuma proteção contra falha externa hoje — se a API travar, o fetch espera pra sempre. Adiciona timeout explícito de 10 segundos no fetch dos dois providers. Depois, cria um decorador comResiliencia() que envolve qualquer SearchProvider com retry e backoff exponencial, mais um circuit breaker: falhas consecutivas o bastante abrem o circuito, e chamadas seguintes falham na hora, sem chamar o provider, até um tempo de resfriamento passar. criarSearchProvider() aplica isso por padrão pro Serper e pro Google — a fixture do modo DEMO não passa por essa camada, porque não tem rede ali pra proteger. Tempo de espera e relógio precisam ser injetáveis, pra dar pra testar sem esperar de verdade os segundos de backoff ou o resfriamento do circuito.

### O prompt define quatro pontos:

circuit breaker. Com falhas consecutivas em número suficiente, o circuito abre, e as chamadas seguintes falham na hora, sem chamar o provider, até passar o tempo de resfriamento.

fixture do modo demo fica de fora, porque ali não há rede para proteger.

verdade os segundos de backoff ou de resfriamento. A resiliência fica em um arquivo próprio. O decorador é uma função com algumas constantes, que podem ser alteradas:

O funcionamento não tem nada de sofisticado. As tentativas ficam em um for, que chama a busca da função envelopada até três vezes. Depois de três tentativas, o circuito abre. Para saber quando pode chamar de novo, o decorador verifica o tempo restante do circuito. O timeout não fica nesse arquivo. Ele está nos próprios providers, o do Serper e o do Google: o fetch recebe o parâmetro signal, que aborta a requisição depois de 10 segundos. A exceção que sobe é capturada, e o decorador faz uma nova tentativa. Testes unitários documentam esses tratamentos e garantem a sua qualidade. Se o framework já dá timeout e as demais capacidades de resiliência por padrão, use o que está nele. O sistema funciona com ou sem essas proteções. Com elas, um serviço que depende de outros, fora do seu controle, consegue atender ao cliente por mais tempo. Resiliência é isso: fazer de tudo para o serviço não sair do ar. A tabela a seguir resume as camadas de proteção, incluindo a degradação graciosa, explicada na próxima seção:

- Timeout: explícito, de 10 segundos, no fetch dos dois providers.
- Decorador comResiliencia: envolve qualquer search provider com retry e backoff exponencial, mais o
- Aplicação por padrão: a função que cria o search provider aplica o decorador ao Serper e ao Google. A
- Tempo injetável: o tempo de espera e o relógio são injetáveis, para que os testes não precisem esperar de
- o máximo de tentativas, que por padrão é três;
- o backoff inicial;
- o limite de falhas consecutivas para abrir o circuito;
- o tempo de resfriamento, depois do qual o circuito volta a chamar o serviço envelopado.

### Técnica Problema que resolve Como foi aplicada

Timeout O fetch não tem timeout por padrão: se o serviço trava, a requisição trava junto. Timeout explícito de 10 segundos no fetch dos dois providers, com o parâmetro signal.

## Pontos de atenção

- O modo demo resolve o desenvolvimento e as demonstrações, mas não a produção. Em produção, a flag está
- desligada, e o Serper está no ar de verdade, o que inclui os dias em que ele não está. API de terceiro cai, tem
- O sistema não responde da mesma maneira quando um serviço falha, mas também não precisa mostrar uma
- Por padrão, um fetch não tem timeout. Ele fica no ar pelo tempo que for preciso esperar pela resposta. Se o
- Às vezes o serviço não saiu do ar indefinidamente. Houve só um pico de requisições, algo intermitente no
- mais. Não há mistério nos sistemas que usam LLM.
- dados. É o caso clássico do circuit breaker: não adianta insistir em um terceiro cujo serviço está tentando subir.

## Checkpoint

- [ ] Você consegue explicar a diferença entre timeout, retry com backoff e circuit breaker e o problema que cada um

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
