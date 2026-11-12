# Aula 4: GitHub e GitHub Actions

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar o papel do GitHub Actions como a peça que faz build, teste e deploy a cada push.
- Comparar a autenticação por chave estática guardada em secret com a autenticação por workload identity pool, de chaves efêmeras.
- Reconhecer a estrutura de um arquivo YAML do GitHub Actions: gatilho, jobs, máquina de execução e steps.

## Diagramas desta aula

- [`Diagrama 1.4 — Workload Identity Federation.pptx`](../../materiais_aula/Diagrama 1.4 — Workload Identity Federation.pptx)

## Desenvolvimento

### Contexto da aula

Falta uma peça para fechar o mapa da arquitetura: a que faz o build do código, executa os testes automatizados, passa por todos os quality gates e envia o código aos serviços do Google Cloud, sem comandos manuais a cada push. Essa peça é o GitHub Actions. Esta aula explica como uma esteira do GitHub Actions é organizada e como ela se autentica na nuvem. Ao final, você saberá ler um workflow e explicar por que o projeto não guarda nenhuma chave de acesso no repositório. Dois jeitos de dar à esteira acesso à nuvem As primeiras etapas da esteira, o build e os testes, não precisam de acesso ao Google Cloud. O deploy precisa. Há dois jeitos de dar esse acesso. O primeiro é o modelo padrão: criar uma chave no Google Cloud, sempre com as permissões mínimas necessárias para o deploy, e guardar esse JSON na área de secrets do repositório no GitHub. A cada execução, a esteira usa essa chave.

- Reconhecer a estrutura de um arquivo YAML do GitHub Actions: gatilho, jobs, máquina de execução e steps.

### ATENÇÃO — Nunca versione um secret

Um secret nunca vai para o código versionado. O GitHub tem uma área própria para os secrets do repositório.

Esse modelo funciona, mas tem um risco. Se o repositório for comprometido de alguma forma, o secret pode ser usado de maneira mal-intencionada. Mesmo com a boa prática de dar o mínimo de permissão, o risco continua existindo. O segundo jeito, adotado no projeto como opção de segurança, é a Workload Identity Federation (WIF), com um workload identity pool.

### Workload identity pool: chaves que existem só durante o deploy

Com o workload identity pool, a esteira não guarda chave nenhuma. A autenticação acontece a cada execução, em quatro passos: 1. O runner do GitHub Actions, ao executar, faz um login no próprio GitHub, baseado em quem está fazendo o push, e recebe um token OIDC de curtíssima duração. A cada execução, um novo token é gerado. 2. Com esse token, ele faz o login no GCP, previamente configurado. O login confirma duas coisas: que quem chama é alguém que a nuvem conhece e que a chamada vem de um repositório que o GCP conhece. 3. Nesse momento é criado um token impersonado, que representa uma service account de deploy. Ele é criado no ato e faz toda a execução necessária. 4. Quando o deploy acaba, tudo isso é apagado.

Fluxo editorial que organiza as etapas descritas na aula.

### EM SÍNTESE

Todas as chaves são efêmeras: fazem o seu papel e somem. Isso é mais seguro do que manter um JSON estático no secret.

Nas configurações gerais de Actions do GitHub existe, por padrão, o GITHUB_TOKEN. Esse token não é da nuvem, é do próprio GitHub. Ele identifica quem está executando aquela run, conforme a permissão que a pessoa tem no repositório.

### O runner troca um token OIDC de curtíssima

duração por um token impersonado da service account de deploy.

### Duração da credencial Estática: fica guardada enquanto não for

removida. Efêmera: é criada no ato e apagada quando o deploy termina.

### Risco Se o repositório for comprometido, o secret

pode ser usado de maneira mal-intencionada. Não sobra nenhuma chave, e o acesso é condicionado a um repositório específico.

### Toda esteira do GitHub Actions é um arquivo YAML com a mesma estrutura:

ou de um fork. Várias ações dentro do ecossistema do GitHub podem disparar uma esteira;

Onde a esteira é executada O GitHub sobe uma máquina, na verdade um container, e executa toda a esteira nesse container. Quando a run acaba, o container é desmontado, e o GitHub espera a próxima execução. A imagem da máquina é definida no próprio YAML. Por padrão, é uma máquina Linux, a ubuntu-latest. Também há máquinas Windows e Mac, mas normalmente são pagas. De graça, é basicamente só a Linux. O sistema operacional é definido por job. Como essa chave fica abaixo do job, um job pode executar em Linux e outro, por exemplo o de teste, em Windows.

- nome: o nome da ação;
- on: o gatilho, que define quando a ação é executada. Pode ser um push, a criação de um PR, de uma issue
- jobs: o que é executado a cada gatilho. Pode haver um ou mais jobs. A esteira do projeto tem o job de
- steps: os comandos que cada job executa. O job de deploy tem vários.

### Jobs em máquinas diferentes

Em aplicações para o ecossistema da Apple, como as de iPhone, é normal fazer o build em uma máquina Mac e os testes em uma máquina Linux. Neste projeto, que é uma aplicação web, tudo roda em Linux.

Steps e actions prontas Cada step executa um comando. Como a máquina é Linux, um step pode rodar comandos do próprio sistema, como um echo que aparece na linha de comando. Ele também pode usar ações já criadas pela equipe do GitHub ou por terceiros. A action mais usada é a checkout, que faz o checkout do código-fonte. Ela é necessária porque a máquina nasce nova a cada execução e precisa receber o fonte. Daria para escrever um step com o git clone e todo o resto, mas as actions da equipe do GitHub e as da comunidade facilitam o trabalho e deixam o YAML mais simples. O lado do GCP: o pool de identidade No GCP, o pool fica na parte de IAM, em federação de identidade. O console em português traduz workload pool como pool de identidade. No projeto, o pool se chama GitHub Actions, e é ele que guarda as definições usadas na autenticação. A tela do pool traz três informações úteis:

- quando o pool foi usado: cada uso é registrado para auditoria, e o próprio Google Cloud avisa se houver
- as asserções usadas na autenticação;
- a condição: o acesso só vale para um repositório específico.

## Pontos de atenção

- você saberá ler um workflow e explicar por que o projeto não guarda nenhuma chave de acesso no repositório.
- As primeiras etapas da esteira, o build e os testes, não precisam de acesso ao Google Cloud. O deploy precisa.
- ATENÇÃO  ·  Nunca versione um secret
- Um secret nunca vai para o código versionado. O GitHub tem uma área própria para os secrets do repositório.
- Esse modelo funciona, mas tem um risco. Se o repositório for comprometido de alguma forma, o secret pode
- ser usado de maneira mal-intencionada. Mesmo com a boa prática de dar o mínimo de permissão, o risco
- Com o workload identity pool, a esteira não guarda chave nenhuma. A autenticação acontece a cada execução,

## Checkpoint

- [ ] Você consegue explicar o que o GitHub Actions faz a cada push e por que só a etapa de deploy precisa de

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
