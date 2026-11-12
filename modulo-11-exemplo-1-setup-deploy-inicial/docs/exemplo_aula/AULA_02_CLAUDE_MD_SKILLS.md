# Aula 2: CLAUDE.md e AI Dev Skills

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Preparar o ponto de partida do projeto: fazer o fork do repositório, clonar e trabalhar na branch starter.
- Explicar o papel do CLAUDE.md como arquivo de contexto e de regras de trabalho que o agente carrega em toda interação.
- Diferenciar o CLAUDE.md das skills e aplicar a regra de precedência entre a skill oficial de um framework e a skill do próprio projeto.

## Desenvolvimento

### Contexto da aula

Um agente de código não lembra, de uma interação para a outra, como o projeto funciona nem quais regras deve seguir. Esta aula mostra como resolver isso com dois recursos: o arquivo CLAUDE.md, carregado em toda interação, e as skills, carregadas conforme a tarefa. Antes disso, a aula prepara o ponto de partida do projeto. Ao final, você terá o repositório clonado na branch certa e saberá o que colocar no CLAUDE.md, o que deixar para as skills e qual skill vale quando duas tratam do mesmo assunto.

- Diferenciar o CLAUDE.md das skills e aplicar a regra de precedência entre a skill oficial de um framework e a skill

### O ponto de partida: fork, clone e a branch starter

O projeto é feito de ponta a ponta, inclusive com a esteira de DevOps que entrega o código no Google Cloud. Por isso, você usa as suas próprias contas, tanto do GitHub quanto do Google Cloud, e precisa de uma cópia do repositório na sua conta. 1. Pegue o link do repositório do Capstone no material complementar da aula. O endereço pode mudar, e por isso o material complementar é a referência. O repositório é o Capstone Project AI Researcher. 2. Faça um fork do projeto, para tê-lo na sua conta do GitHub. 3. Clone o projeto a partir do seu fork, com git clone. 4. Entre na pasta do projeto e abra-a no seu editor. Uso o VS Code, mas qualquer ferramenta de desenvolvimento serve. O repositório contém o projeto de fim a fim, separado em várias branches, para que o desenvolvimento possa ser consultado passo a passo. O trabalho acontece na branch starter, que tem o mínimo já configurado, para que o estudo se concentre nas partes mais importantes e mais teóricas do projeto.

### Projeto seed

É comum chamar de projeto seed um ponto de partida que traz só o início do que é necessário. A branch starter cumpre esse papel. A Aula 7 apresenta um repositório separado com esse mesmo conteúdo.

Muita coisa nesse repositório já está adiantada, e as aulas destacam as partes mais importantes. Como você tem acesso ao código completo, pode examinar cada detalhe ou pedir ao Claude que explique cada um deles.

### Por que o agente precisa de um arquivo de contexto

O modelo com o qual um agente de codificação conversa é stateless: ele não lembra o contexto. Cada vez que você fala com ele, é como se fosse uma requisição nova aos modelos, no caso, os da Anthropic. A solução é um arquivo em que se configura como o agente deve trabalhar no projeto e quais são as suas diretrizes. No Claude, esse arquivo é o CLAUDE.md, que fica na pasta .claude. O Gemini e o Codex têm o equivalente: todas as ferramentas têm.

### CLAUDE.md

Arquivo que o Claude carrega em toda interação para saber onde está, qual é o contexto do projeto e quais regras deve seguir. É fundamental para quem trabalha com o Claude.

### O que o CLAUDE.md deste projeto define

O arquivo começa pelo contexto: o repositório é um demonstrativo do módulo Capstone, e o código é didático. Ele descreve as partes do projeto e guarda também o estado atual do repositório. Depois vêm as regras de trabalho, divididas em dois grupos.

### O primeiro grupo lista o que o agente deve perguntar antes de fazer:

- instalar qualquer dependência nova;
- criar uma abstração ou interface;
- alterar esquemas do banco de dados;
- mudar configurações de deploy, de workflow ou de infraestrutura;
- reorganizar pastas ou mover arquivos.

### O segundo grupo lista o que o agente nunca deve fazer:

e, em produção, do Secret Manager, o que coloca segurança e desenvolvimento seguro no projeto desde o zero;

do tipo, como no retorno de uma API, o preferível é unknown com narrowing;

A regra dos testes tem um complemento: em todo desenvolvimento são criados testes automatizados, testes unitários, para validar o que está acontecendo. O arquivo termina com as convenções do projeto.

- escrever segredos, chaves ou connection strings em arquivo versionado: tudo vem de variável de ambiente
- usar LLM para gerar os parágrafos de resumo de cada ação, na carga do RAG com os CSVs da CVM;
- adicionar any sem um comentário justificando: no TypeScript, quando não se sabe ou não se tem certeza
- escrever teste que dependa de rede: usam-se fixtures ou fakes.

### Por que a carga do RAG aparece nas regras

Os CSVs da CVM são carregados na base de dados que serve de primeira fonte do agente. Ele busca primeiro no RAG, que é uma informação muito mais rápida e mais barata do ponto de vista de tokens, e só depois, caso não encontre, vai para a internet.

## Pontos de atenção

- Um agente de código não lembra, de uma interação para a outra, como o projeto funciona nem quais regras
- que o estudo se concentre nas partes mais importantes e mais teóricas do projeto.
- Muita coisa nesse repositório já está adiantada, e as aulas destacam as partes mais importantes. Como você
- O modelo com o qual um agente de codificação conversa é stateless: ele não lembra o contexto. Cada vez que
- O segundo grupo lista o que o agente nunca deve fazer:
- adicionar any sem um comentário justificando: no TypeScript, quando não se sabe ou não se tem certeza
- O que manda é o arquivo do projeto. Quando o projeto não tem alguma definição, o agente recorre ao arquivo

## Checkpoint

- [ ] Você consegue explicar por que é preciso fazer um fork do repositório e em qual branch o trabalho acontece

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
