# Aula 7: Walking Skeleton e Deploy Zero

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Construir o esqueleto do projeto: uma API com health check, uma aplicação Angular que a consome e um

## Desenvolvimento

### Contexto da aula

Com os dados da CVM normalizados em JSON e a fundação criada no Google Cloud, o passo seguinte é ter código em produção. Esta aula cria uma API e um frontend bem simples, ainda sem a integração com o agente, e um pipeline de deploy que publica tudo na infraestrutura. O que sobe é basicamente um health check, mas ele já está em produção. Ao final, você terá o esqueleto do projeto rodando localmente e na nuvem, saberá ler o workflow de deploy e saberá resolver o erro mais comum do primeiro deploy.

- Explicar como o workflow de deploy do GitHub Actions testa, autentica sem chave e publica no Cloud Run e no
- Diagnosticar o status degraded do primeiro deploy e validar o ambiente com o capstone:check.

### Dois repositórios: o projeto completo e o seed

O curso tem dois repositórios, e a escolha depende de como você quer estudar. O Capstone Project AI Researcher tem o projeto completo, de ponta a ponta, com todos os marcos e até a branch starter. Como ele já traz a esteira pronta, refazê-la ali, passo a passo, causaria problemas de merge. O AI Researcher Seed tem só o projeto no estado da branch starter, sem uma branch com esse nome: esse conteúdo já é a main. Ou seja, a starter do AI Researcher é a main do AI Researcher Seed.

ou o Angular pelo React. O material é prático, mas nada substitui a sua própria prática. É fazendo a sua versão que você aprende.

- Para fazer desde o começo, acompanhando as aulas, use o Seed.
- Para ver o resultado inteiro, com todos os fontes, use o Capstone.
- Para explorar e fazer a sua versão, fique à vontade: a licença é MIT. Você pode trocar a nuvem pela AWS

### O que compõe o walking skeleton

O esqueleto tem quatro peças: uma API com uma rota de health check, um contrato compartilhado, uma aplicação Angular que mostra o status e um banco Postgres. A aplicação é JavaScript de ponta a ponta.

### Prompt enviado ao Claude Code

Crie apps/api com Fastify e TypeScript. Uma rota GET /api/health que checa o Postgres de verdade via pg — consulta simples tipo SELECT 1, com timeout curto, e nunca derruba o processo se o banco estiver fora do ar, só reporta degraded. A resposta segue um schema zod em packages/contracts, compartilhado entre API e frontend. Deixe pronto também o jeito de rodar isso localmente contra o Postgres do docker- compose: um .env na raiz (gitignorado) com a DATABASE_URL apontando pra localhost — não pro nome do serviço do docker-compose, que só resolve dentro da rede do Docker —, um .env.example versionado documentando a variável, e o script dev da API carregando esse .env automaticamente (sem quebrar produção, que continua vindo do Secret Manager).

Nesse primeiro momento, a API tem uma única rota. Ela checa o Postgres de verdade, com uma consulta simples do tipo SELECT 1 e timeout curto, só para saber se o banco está vivo. Se o banco estiver fora do ar, a rota nunca derruba o processo: apenas reporta degraded. A resposta segue um contrato, definido com o Zod.

### Zod

Biblioteca TypeScript que faz, em tempo de execução, as mesmas checagens de tipos que o TypeScript faz em tempo de build, de transpilação. Usa a mesma tipagem do TypeScript e é muito utilizada nesse ecossistema.

### O contrato do health check é simples e tem dois campos:

Ele fica em um pacote separado da pasta da API, porque o frontend também usa os contratos. O prompt também prepara a execução local com o Postgres do Docker Compose. O ponto de atenção é a variável de ambiente com a URL do banco, que é diferente para cada pessoa. O arquivo .env.example, versionado, documenta a variável e serve de modelo para você criar o seu próprio .env. O script de desenvolvimento da API carrega o .env automaticamente, sem afetar a produção, que continua lendo do Secret Manager.

- status, que pode ser ok ou degraded;
- database, que pode ser ok ou error.

### Prompt enviado ao Claude Code

Crie apps/web com a skill oficial angular-new-app. Angular 22, standalone, signals. Um componente que consome /api/health via resource() e mostra o status na tela. Depois de gerar o projeto, desligue o prompt de coleta de analytics do Angular CLI (ng analytics off) — sem isso, a primeira vez que o ng serve roda dentro do pnpm dev/turbo, ele trava esperando uma resposta interativa que nunca chega, e a tela nunca sobe.

O prompt manda usar a skill oficial angular-new-app, seguindo a regra do CLAUDE.md: havendo uma skill oficial do framework, é ela que deve ser usada. Se o projeto ainda não tiver a skill, o agente a baixa, seja o Claude Code, seja o Codex. Como ela vem do time do Angular, é a mesma para todos. O componente é simples: consome a API e mostra o status na tela, com o Angular 22.

### ATENÇÃO — A pergunta de analytics trava o ambiente

O projeto usa o Turborepo como ferramenta de monorepo. Na primeira execução, o Angular às vezes pergunta se pode enviar dados de analytics. Ele fica preso esperando a resposta, e o Turborepo fica esperando por ele. Por isso o prompt já desliga a coleta de analytics. Esse erro apareceu no ensaio da aula, e o prompt foi ajustado para evitá-lo.

Durante a criação, o agente abre o Chrome e opera a tela como se fosse um usuário, usando uma skill própria para isso. Há quem use esse recurso para teste automatizado. É válido, mas não recomendo muito, porque sai caro o agente analisar tudo dessa forma. Existem ferramentas muito mais baratas para esse fim, como o Cypress. Rodando localmente sem sair da sessão do agente Para executar um comando no shell sem sair da sessão com o agente, coloque um ponto de exclamação antes do comando. O ambiente local sobe com !pnpm dev. Com o ambiente no ar, a aplicação consulta o Postgres local. A exclamação evita perder o ritmo de trabalho trocando de janela ou de terminal. Docker Compose e o turbo prune O Docker Compose sobe o banco de dados, o backend e o frontend de uma vez:

### Prompt enviado ao Claude Code

Crie docker-compose.yml na raiz subindo Postgres com pgvector, a API e o Web, usando turbo prune -- docker nos Dockerfiles pra build eficiente em monorepo. O Postgres do compose é efêmero, só pra desenvolvimento — nunca é o Cloud SQL.

## Pontos de atenção

- — consulta simples tipo SELECT 1, com timeout curto, e nunca derruba o processo se o banco estiver fora
- compose: um .env na raiz (gitignorado) com a DATABASE_URL apontando pra localhost — não pro nome do
- rota nunca derruba o processo: apenas reporta degraded.
- O prompt também prepara a execução local com o Postgres do Docker Compose. O ponto de atenção é a
- serve roda dentro do pnpm dev/turbo, ele trava esperando uma resposta interativa que nunca chega, e a
- do framework, é ela que deve ser usada. Se o projeto ainda não tiver a skill, o agente a baixa, seja o Claude
- ATENÇÃO  ·  A pergunta de analytics trava o ambiente

## Checkpoint

- [ ] Você consegue explicar o que a rota de health check verifica e por que o contrato Zod fica em um pacote

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
