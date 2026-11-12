# Aula 23: Métricas, budget de tokens e rate limiting

> Unidade 5 — Observabilidade e produção · Capstone AI Researcher

## Objetivos de aprendizagem

- Diferenciar telemetria, que registra item a item, de métrica, que é o valor agregado ao longo do tempo.
- Criar contadores de tokens e de custo e expô-los em um endpoint de métricas.
- Implementar o rate limiting e um orçamento diário de tokens como mecanismos de controle de custo e de volumetria.

## Desenvolvimento

### Contexto da aula

Aplicações agênticas podem ficar bem caras. Em produção, vale ter controles de custo dentro da própria aplicação, para não haver surpresa indesejável quando um usuário abusa ou quando o gasto passa do que a empresa deseja. Esta aula cria as métricas internas do agente e, sobre elas, dois mecanismos de controle: o rate limit, que limita o volume de chamadas, e o orçamento diário de tokens. Ao final, você saberá diferenciar telemetria de métrica, explicar de onde vêm os números de custo e descrever o que acontece quando cada limite é atingido.

### Telemetria e métrica

O Langfuse oferece os dois. Mesmo assim, o projeto cria uma métrica própria, local, porque é sobre ela que os controles de custo são implementados no agente.

- Telemetria: o dado analítico, item a item. É o trace de cada chamada.
- Métrica: o agregado. Quanto neste mês, quanto nesta semana e assim por diante.

### FinOps

Com a métrica na aplicação, um abuso ou um custo acima do desejado pode receber um tratamento de erro ou outro tratamento, como um fallback para um modelo mais barato. Contadores de tokens e de custo

### Prompt enviado ao Claude Code

Crie contadores Prometheus (prom-client) num Registry próprio: llm_tokens_total (labels node, model, kind) e llm_cost_usd_total (labels node, model). Crie um callback LangChain genérico que correlacione handleChatModelStart/handleLLMEnd por runId, lendo metadata.langgraph_node e metadata.ls_model_name, e incremente os contadores a partir do usage_metadata real devolvido pela Vertex AI — nunca uma estimativa. O custo vem de uma tabela de preço USD por milhão de tokens; modelo fora da tabela loga aviso e conta como custo zero, nunca quebra a resposta. Esse callback deve entrar somado ao criarLangfuseCallbacks() já existente — callbacks: [...criarLangfuseCallbacks(), criarMetricsCallback()] — no mesmo call site do graph.stream()/invoke() em apps/api/src/app.ts, nunca sozinho dentro de llm.ts: o LangGraph propaga o callback manager por AsyncLocalStorage, e um callbacks explícito dentro de um nó substituiria esse ambiente em vez de somar a ele.

### O prompt pede:

métrica: o total de tokens e o custo total, em dólar.

modelo, e incrementa os contadores a partir do uso real devolvido pelo Vertex AI, nunca de uma estimativa.

gera um aviso no log e conta como custo zero, sem nunca quebrar a resposta.

- Dois contadores Prometheus, em um registro próprio, com uma biblioteca bem utilizada para esse tipo de
- Um callback genérico do LangChain, nas chamadas do agente, que lê os metadados, como o nome do
- Uma tabela de preço, em dólar por milhão de tokens, de onde vem o custo. Um modelo fora da tabela
- O ponto de ligação: o callback entra somado ao do Langfuse, no mesmo ponto em que o grafo é

### Vários interceptors podem ser colocados na mesma chamada, sempre independentes, cada um fazendo uma

coisa, sem influenciar a regra de negócio. Aqui, um captura a telemetria para o Langfuse e outro cria as métricas locais.

O trabalho do Claude Code é parecido com o da instrumentação do Langfuse: ele aproveita a mesma estrutura, cria as funções de métricas, com os contadores, e a tabela com o valor por milhão de tokens dos modelos em uso. Dois limites dessa implementação:

custo de vários modelos, mas a opção aqui foi simplificar.

didáticos. No seu desenvolvimento, use a versão mais nova.

- Precisão: o cálculo não é tão preciso quanto o do Langfuse. Há serviços que retornam em tempo real o
- Biblioteca depreciada: na execução, o agente avisou que a biblioteca foi depreciada. Mantive, por fins

### Prompt enviado ao Claude Code

Exponha GET /api/metrics no formato Prometheus, usando o Registry já criado. Defina uma interface mínima pro registry, não o tipo concreto do prom-client, pra apps/api não ganhar essa dependência.

A rota entrega as métricas no formato Prometheus, usando o registro já criado. O registro entra por uma interface mínima, e não pelo tipo concreto da biblioteca, para a API não ganhar essa dependência.

### Rate limit: o limite de rajadas de chamadas

O rate limit independe de a aplicação ser agêntica. É um conceito de aplicação de backend.

### Rate limit

É o limite de chamadas, das rajadas de chamadas, na aplicação. Quando o limite é atingido, a aplicação devolve um 429, o erro que indica chamadas demais.

Ele existe para prevenir problemas. Toda aplicação tem um padrão de comportamento, conhecido pela regra de negócio ou por observação. Um volume de chamadas muito acima desse padrão pode indicar algo errado:

As consequências são o custo muito alto ou a queda da aplicação por uma volumetria para a qual ela não está preparada.

- uma invasão;
- um usuário cometendo abuso;
- um bot abusando da API, no caso do MCP;
- algo em loop infinito.

## Pontos de atenção

- aplicação, para não haver surpresa indesejável quando um usuário abusa ou quando o gasto passa do que a
- incremente os contadores a partir do usage_metadata real devolvido pela Vertex AI — nunca uma
- aviso e conta como custo zero, nunca quebra a resposta. Esse callback deve entrar somado ao
- — no mesmo call site do graph.stream()/invoke() em apps/api/src/app.ts, nunca sozinho dentro de llm.ts:
- modelo, e incrementa os contadores a partir do uso real devolvido pelo Vertex AI, nunca de uma estimativa.
- gera um aviso no log e conta como custo zero, sem nunca quebrar a resposta.
- Precisão: o cálculo não é tão preciso quanto o do Langfuse. Há serviços que retornam em tempo real o

## Checkpoint

- [ ] Você consegue explicar a diferença entre telemetria e métrica sem consultar o material?
- [ ] Você consegue explicar como os contadores de tokens e de custo são alimentados e de onde vem o valor do

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
