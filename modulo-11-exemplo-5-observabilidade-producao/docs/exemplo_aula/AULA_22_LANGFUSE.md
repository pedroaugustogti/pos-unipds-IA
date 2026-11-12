# Aula 22: Langfuse: tour e instrumentação por nó

> Unidade 5 — Observabilidade e produção · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar por que uma aplicação em produção precisa de observabilidade e o que é telemetria.
- Preparar um projeto no Langfuse e instrumentar o grafo do agente para enviar a telemetria.
- Reconhecer o papel do OpenTelemetry como padrão aberto e do padrão interceptor na instrumentação.

## Desenvolvimento

### Contexto da aula

Uma aplicação production-ready não se resolve só com controle de qualidade e testes. Com a aplicação em produção, duas perguntas precisam de resposta: como saber se o usuário está tendo algum problema e como controlar o custo. Na esteira, no ambiente de desenvolvimento ou no de homologação, é possível parar, abrir o capô e ver o que está acontecendo. Em produção, as respostas têm de vir com o avião voando. É o papel da observabilidade. Esta aula trata da observabilidade do consumo de modelos. Ao final, você saberá explicar o que é telemetria, instrumentar o grafo do agente para enviá-la a uma ferramenta de observabilidade e conferir o trace e o custo de cada chamada.

### Telemetria

São os dados puros de log, de quando algo começou e de quando terminou, que o sistema vai enviando ao servidor. É o sistema informando que está tudo bem, que deu erro em tal ponto, que tal operação demorou tanto. Na prática, é um JSON com essas informações.

Sobre a telemetria constroem-se o monitoramento e os alarmes. O ponto fundamental é a ingestão: sem a telemetria chegando, não há o que monitorar.

### Instrumentar

É usar o SDK da ferramenta de observabilidade nos pontos de chamada do projeto, para que ele envie a telemetria. Dependendo do framework, isso nem é tão invasivo.

No uso de modelos, o custo deve ser considerado desde o começo, sempre pesado contra o valor que se quer entregar ao usuário.

### O Langfuse

O projeto usa o Langfuse, um framework de observabilidade de agentes. Como outros frameworks open source, ele também tem um serviço de nuvem. O plano gratuito atende até dois usuários, com retenção de 30 dias, e não exige cartão de crédito. É o suficiente para o desenvolvimento e permite conhecer uma ferramenta real de observabilidade.

### O Langfuse não é a única opção. Há outras ferramentas do gênero, e ferramentas de observabilidade

tradicionais também já têm módulo de IA. Ele serve aqui para explicar os conceitos.

### EM SÍNTESE

Tecnologias, nuvens e agentes de código são efêmeros: ferramenta se troca como quem troca de roupa. O valor do profissional está nos fundamentos, no pensamento estratégico e analítico e na prática.

### Preparando o projeto e as chaves no Langfuse

A preparação tem três passos: 1. Faça o cadastro no Langfuse e o login. Você chega ao dashboard. 2. Crie um projeto e, em Settings, crie a API key, com a secret key. 3. Coloque no ambiente de desenvolvimento as três variáveis de ambiente que a própria tela indica, no arquivo de ambiente ou nas variáveis do sistema operacional.

### LangfuseSpanProcessor (@langfuse/otel) uma vez no boot de cada processo que pode invocar o grafo —

apps/api e os dois transportes do packages/mcp-server. Crie um CallbackHandler (@langfuse/langchain) a cada chamada de graph.stream()/graph.invoke(). Sem as chaves configuradas, nada disso deve registrar nada nem impedir o processo de subir.

### O prompt define três pontos:

uma vez na inicialização de cada processo que pode invocar o grafo. São três: a API e os dois transportes do servidor MCP.

normalmente. No código, a telemetria é inicializada quando a aplicação é instanciada, antes de o backend Node subir, e a função de callback fica preparada para as chamadas. A documentação do Langfuse oferece uma skill própria para agentes. Em uma aplicação simples como esta, o Claude Code se sai bem sem ela, explorando o Langfuse por conta própria. No seu projeto, instalar a skill deixa o agente mais rápido e mais assertivo nessa atividade. A instrumentação também pode partir de uma spec de fim a fim, escrita em conversa com o agente.

- Provider no boot: o provider do OpenTelemetry é registrado, com o span processor do SDK do Langfuse,
- Callback a cada chamada: um callback handler é criado a cada chamada do grafo, já que o projeto usa o
- Sem chaves, sem efeito: sem as chaves configuradas, nada é registrado, e o processo sobe

## Pontos de atenção

- Uma aplicação production-ready não se resolve só com controle de qualidade e testes. Com a aplicação em
- telemetria chegando, não há o que monitorar.
- O plano gratuito atende até dois usuários, com retenção de 30 dias, e não exige cartão de crédito. É o suficiente
- O Langfuse não é a única opção. Há outras ferramentas do gênero, e ferramentas de observabilidade
- necessário, mas estudar fundamentos é mais importante do que nunca. Hoje os agentes programam muito mais
- Com a variável DEMO igual a true, o sistema responde com mocks e não chama os modelos. Para ver a
- aberto é de outra, os dados não aparecem.

## Checkpoint

- [ ] Você consegue explicar por que a observabilidade é necessária em produção e o que é telemetria sem consultar

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
