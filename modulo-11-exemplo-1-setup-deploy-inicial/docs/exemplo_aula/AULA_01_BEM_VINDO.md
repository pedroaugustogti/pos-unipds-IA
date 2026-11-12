# Aula 1: Bem-vindo ao Capstone

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Reconhecer o que a disciplina constrói: o AI Researcher, um chatbot especializado em investimentos de bolsa, do primeiro commit à produção.
- Explicar, em alto nível, a regra de negócio do agente: buscar na base vetorial, julgar o contexto e recorrer à web quando ele não basta.
- Justificar por que a restrição de não recomendar investimentos é garantida no código, e não apenas no system prompt.

## Diagramas desta aula

- [`Diagrama 1.1 — RAG corretivo (fluxo em alto nível).pptx`](../../materiais_aula/Diagrama 1.1 — RAG corretivo (fluxo em alto nível).pptx)

## Desenvolvimento

### Contexto da aula

Esta disciplina aplica o que foi aprendido nas demais matérias em um único projeto, construído do começo ao fim: do primeiro commit até a entrega em produção, na nuvem. O projeto é o AI Researcher, um chatbot especializado em investimentos de bolsa. Esta primeira aula apresenta o produto pronto e a sua regra de negócio em alto nível. Ao final, você saberá dizer o que o sistema faz com uma pergunta, por que ele nunca recomenda compra ou venda e o que, além do agente, faz parte do projeto.

- Explicar, em alto nível, a regra de negócio do agente: buscar na base vetorial, julgar o contexto e recorrer à web
- Justificar por que a restrição de não recomendar investimentos é garantida no código, e não apenas no system

### O que a disciplina constrói: do primeiro commit à produção

O projeto percorre todas as etapas de um sistema real. Além do código da aplicação, ele inclui:

Em todo o projeto há observabilidade. Uso o Grafana para verificar as requisições e a latência, e outra ferramenta de observabilidade é apresentada mais adiante, quando o projeto chega à produção. O AI Researcher: um chatbot de investimentos O AI Researcher é um chatbot especializado em investimentos de bolsa. Escolhi esse exemplo porque ele exercita as duas frentes da disciplina ao mesmo tempo: é um projeto em que agentes são usados para desenvolver o código e é, ele próprio, um sistema que consome LLMs. O agente que pesquisa e dá a resposta também é construído ao longo das aulas. A interface tem um recurso que ajuda a entender o que acontece por dentro: o pipeline de raciocínio. Ele mostra cada etapa que o sistema percorre para responder, inclusive os erros, caso ocorram.

- observabilidade, para acompanhar o sistema em funcionamento;
- FinOps, inclusive aplicado a sistemas que consomem LLMs;
- deploy automatizado, com o GitHub Actions publicando o projeto na nuvem.

### A regra de negócio: buscar na base, julgar o contexto e recorrer à web

A regra de negócio do agente tem três movimentos. Quando o usuário faz uma pergunta, o sistema busca na base vetorial, a base de RAG montada para ele. Se o contexto encontrado é suficiente, a resposta é dada com a citação da base. Se não é suficiente, e é o próprio sistema que faz esse julgamento, ele busca na internet.

### Pergunta respondida pela base

À pergunta "Qual é a receita líquida da Vale no último semestre?", o sistema responde com o que encontrou na base de RAG. O pipeline de raciocínio mostra que ele não inventou a informação e também não foi buscá-la na internet.

### Pergunta que exige a web

À pergunta "Qual foi o último fato relevante da Vale?", o sistema apresenta o fato relevante e avisa: "Contexto local insuficiente neste turno — a etapa Search buscou complemento na web". Ele fez a busca na base e, em seguida, a pesquisa na web.

Informar, nunca recomendar: a restrição regulatória O chat exibe um aviso permanente: "Este assistente apresenta informações públicas, não recomendação de investimento". Esse aviso reflete uma regra do domínio, e não uma escolha de estilo.

### ATENÇÃO — Recomendar investimento é atividade regulada

No Brasil, para dar recomendações de investimento, é preciso ter as certificações e ser registrado na CVM. Os youtubers sérios nunca recomendam: comentam informações, forecast e as ações. Para dizer "compre" ou "venda" uma ação, é preciso estar registrado junto à Bolsa de Valores e à CVM.

Por isso, as regras de negócio precisam estar também no chat. Um guardrail impede o sistema de responder a pedidos de compra ou venda. O ponto central é onde ele fica: o guardrail está no código. Mais do que no system prompt, coloquei essa proteção no próprio código, como a Aula 13 mostra em detalhe.

### Pergunta que força uma recomendação

À pergunta "Eu devo comprar a Vale no preço atual?", o sistema faz a busca, mas bloqueia a recomendação. A resposta é "Não recomendamos decisões de compra, venda ou manutenção", com o aviso de que o contexto disponível pode estar incompleto para responder com certeza.

### A ferramenta de desenvolvimento e o que realmente importa

O desenvolvimento do projeto é feito com o Claude, da Anthropic, uma ferramenta muito utilizada para desenvolvimento de software. Em outro curso, usei bastante as ferramentas do Google, e aqui a escolha foi outra para variar. Você não precisa ficar preso ao Claude. O mesmo trabalho pode ser feito com o Antigravity, o Codex ou o Kimi. Ferramentas vão e vêm: quando você estiver estudando este material, pode haver outra ferramenta da moda.

### EM SÍNTESE

O que permanece é o fundamento. Quem entende o processo e o fundamento consegue aplicá-los com qualquer ferramenta.

## Pontos de atenção

- Justificar por que a restrição de não recomendar investimentos é garantida no código, e não apenas no system
- dizer o que o sistema faz com uma pergunta, por que ele nunca recomenda compra ou venda e o que, além do
- a citação da base. Se não é suficiente, e é o próprio sistema que faz esse julgamento, ele busca na internet.
- base de RAG. O pipeline de raciocínio mostra que ele não inventou a informação e também não foi buscá-la na
- Informar, nunca recomendar: a restrição regulatória
- O chat exibe um aviso permanente: "Este assistente apresenta informações públicas, não recomendação de
- investimento". Esse aviso reflete uma regra do domínio, e não uma escolha de estilo.

## Checkpoint

- [ ] Você consegue explicar o que é o AI Researcher e por que ele foi escolhido como projeto da disciplina sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
