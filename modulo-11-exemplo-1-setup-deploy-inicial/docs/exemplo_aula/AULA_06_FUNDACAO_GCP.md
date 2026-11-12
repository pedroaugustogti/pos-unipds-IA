# Aula 6: Fundação GCP

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Provisionar a fundação do projeto no Google Cloud com prompts ao Claude Code: projeto, APIs, Artifact

## Diagramas desta aula

- [`Diagrama 1.4 — Workload Identity Federation.pptx`](../../materiais_aula/Diagrama 1.4 — Workload Identity Federation.pptx)

## Desenvolvimento

### Contexto da aula

Registry, Cloud SQL, Secret Manager, Workload Identity Federation e Firebase Hosting.

Esta aula cria a infraestrutura do projeto no Google Cloud usando o Claude Code e o SDK do GCP. O agente propõe e executa os comandos, um por vez, e você aprova cada um. O mesmo caminho serve para AWS ou Azure. Talvez algum prompt precise mudar, mas o jeito é muito parecido, porque todos os grandes provedores de nuvem têm o seu SDK, e isso existe muito antes das IAs. O SDK é uma parte fundamental do que se chama IaC, Infrastructure as Code. Ao final, você terá provisionado a fundação do projeto e saberá explicar a organização do GCP em contas de faturamento e projetos, o princípio da mínima permissão e os cuidados com secrets.

- Explicar os conceitos de conta de faturamento, projeto e mínima permissão no GCP.
- Aplicar os cuidados com secrets: nunca gravá-los em arquivo, gerar senhas aleatórias e invalidar imediatamente

### Como o GCP se organiza: conta de faturamento e projetos

Em alto nível, o GCP trabalha com dois conceitos: a billing account, ou conta de faturamento, no console em português, e os projetos.

### Conta de faturamento e projeto

Uma conta de faturamento pode ter N projetos. Cada projeto reúne uma infraestrutura, que fica isolada da infraestrutura dos outros projetos.

Uma conta pessoal normalmente tem uma só conta de faturamento. Empresas muito grandes podem ter mais de uma, conforme a organização. O isolamento entre projetos é quase total. Alguns recursos são compartilhados, mas a maioria não: por padrão, o banco de dados de um projeto não enxerga o de outro. É possível ligar projetos por rede, mas o efeito é o de duas instâncias separadas de nuvem.

### Mínima permissão: as APIs começam desligadas

Por segurança, o GCP trabalha com a mínima permissão necessária. Um projeto recém-criado nasce sem permissão para nenhum SDK fazer absolutamente nada. As APIs são habilitadas conforme a necessidade do projeto. Por isso, o primeiro prompt do provisionamento habilita as APIs, e só as que o projeto vai utilizar. Antes de começar: dois logins e o tempo do banco Antes de abrir o agente de código, é preciso instalar o gcloud, que é o SDK, o CLI do Google Cloud, e fazer dois logins com a sua conta: 1. O login do CLI. 2. O login do SDK, feito com outro comando. Depois dele, o terminal informa que as bibliotecas do Google já podem usar as credenciais. Ter dois logins é uma característica do Google Cloud. Em AWS, Azure ou Oracle, talvez seja um só.

### ATENÇÃO — O banco de dados é o passo mais demorado

O provisionamento do Cloud SQL leva de 20 minutos a meia hora. De tudo o que é criado aqui, é de longe o que mais demora. O resto é rápido.

### O provisionamento, prompt a prompt

O provisionamento segue sete passos, cada um com um prompt. Em todos, o agente lê o infra/README.md, que descreve a arquitetura, e usa o gcloud para interagir com o Google. Em outra nuvem, seria o Azure CLI ou o AWS CLI.

Fluxo editorial com a ordem em que os recursos são criados. 1. Crie o projeto, vincule a conta de faturamento e habilite as APIs:

### Seguindo o infra/README.md, crie o projeto GCP ai-researcher-capstone, vincule à billing account e

habilite as APIs necessárias: Cloud Run, Cloud SQL Admin, Artifact Registry, Secret Manager e IAM Credentials. Rode um comando por vez e espere minha aprovação antes de cada execução.

Ao criar o projeto, o agente mostra o número dele. Cada projeto tem o seu número. Essa informação é específica do projeto, mas não é sensível: não é um secret. 2. Crie o repositório de imagens Docker:

### Prompt enviado ao Claude Code

Crie o repositório Docker do Artifact Registry pra este projeto, seguindo o infra/README.md.

O repositório recebe as imagens Docker do projeto. A região usada é us-central1, escolhida por custo: é a mais barata. Você pode alterar a sua. 3. Provisione o banco de dados:

### Prompt enviado ao Claude Code

Provisione o Cloud SQL Postgres 16 com pgvector, seguindo o infra/README.md: instância ai-researcher-db, tier db-f1-micro, região us-central1. Depois crie o banco ai_researcher, habilite a extensão vector, e crie o usuário app_user com senha gerada de forma segura.

O prompt informa o nome da instância, o tier e a região. A ordem é: criar a instância, criar o banco de dados, habilitar a extensão vector e criar o usuário, com a senha gerada de forma segura. Enquanto a instância é criada, o agente avisa que vai ficar acompanhando. Você também pode acompanhar pelo console: em bancos de dados aparecem o Cloud SQL e os outros produtos do Google, como AlloyDB, Spanner, Bigtable, Firestore e Memorystore.

## Pontos de atenção

- Aplicar os cuidados com secrets: nunca gravá-los em arquivo, gerar senhas aleatórias e invalidar imediatamente
- faturamento e projetos, o princípio da mínima permissão e os cuidados com secrets.
- o banco de dados de um projeto não enxerga o de outro. É possível ligar projetos por rede, mas o efeito é o de
- ATENÇÃO  ·  O banco de dados é o passo mais demorado
- específica do projeto, mas não é sensível: não é um secret.
- ATENÇÃO  ·  Troque o repositório pelo seu
- O prompt aponta para o repositório do curso. Você consegue cloná-lo, mas, como não é o dono dele, o

## Checkpoint

- [ ] Você consegue explicar o que cada prompt da aula provisiona no Google Cloud e em que ordem sem consultar

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
