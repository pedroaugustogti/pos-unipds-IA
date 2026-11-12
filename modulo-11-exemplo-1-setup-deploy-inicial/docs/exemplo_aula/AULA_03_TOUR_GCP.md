# Aula 3: Tour pelo Google Cloud

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Identificar as peças do Google Cloud que sustentam o projeto e o papel de cada uma na arquitetura.
- Explicar por que o projeto usa um backend serverless no Cloud Run e o Postgres com a extensão pgvector no

## Diagramas desta aula

- [`Diagrama 1.3 — Mapa de infraestrutura GCP.pptx`](../../materiais_aula/Diagrama 1.3 — Mapa de infraestrutura GCP.pptx)

## Desenvolvimento

### Contexto da aula

Antes de pedir a um agente que provisione qualquer peça da arquitetura, é preciso entender o que será provisionado. Esta aula percorre, sem terminal e sem commit, os serviços do Google Cloud que o projeto usa e explica o papel de cada um. A escolha do Google Cloud não é uma obrigação. No seu projeto, você pode usar qualquer solução de nuvem, ou até montar uma VM com essas peças. Todas elas existem em outros provedores, como AWS e Azure. A exceção é o Vertex AI, que é um serviço bem específico do Google, mas os outros provedores também têm o seu garden de modelos, talvez com outros modelos, não necessariamente com o Gemini.

- Relacionar cada serviço do GCP ao equivalente que existe em outros provedores de nuvem.

### O mapa da arquitetura

ele. A esteira passa pelas guardas de qualidade do código e, no final, faz o deploy no Google Cloud.

O modelo cumpre dois papéis. Ele faz o embedding, transformando o texto do RAG em embeddings para serem guardados como vetores no Cloud SQL, e é também a LLM que o agente utiliza para fazer a busca e toda a orquestração.

- GitHub Actions: a estrutura de DevOps do GitHub. Todas as ações na infraestrutura são disparadas por
- Cloud Run: a peça principal, onde é executada toda a regra de negócio, a API, o backend. É o serviço de
- Firebase Hosting: armazena a interface e os arquivos estáticos, como a interface feita em Angular.
- Artifact Registry: armazena a imagem Docker que o Cloud Run executa, e que também pode ser
- Cloud SQL: o banco de dados Postgres, com a extensão pgvector, onde ficam os dados, principalmente os
- Vertex AI: o serviço de API em que o modelo é consumido.
- Secret Manager: o cofre de secrets e senhas.

### Cloud Run: o backend serverless

O serviço que roda no Cloud Run é a API do AI Researcher, um backend em Node com o framework Fastify, escolhido porque se trata de uma API relativamente simples.

### Serverless

O próprio GCP sobe os containers, serviços dedicados exclusivamente a atender às requisições, e faz isso sob demanda, sem nenhuma configuração manual. Enquanto ninguém acessa, não há nenhum servidor de backend ligado. O serviço é executado somente quando necessário e pode escalar infinitamente.

Na AWS, o equivalente são as Lambda Functions. A Azure também tem um serviço serverless equivalente. Escolhi essa peça por dois motivos: quis manter o projeto o mais barato possível, e ela pode ser útil no seu dia a dia. O Cloud Run, como os outros serviços do tipo Lambda, é extremamente barato, porque é cobrado por requisição. Na tabela de preços, o valor por gigabyte de memória por segundo tem vários zeros depois da vírgula. Se a aplicação fica no ar 24 horas por dia, 7 dias por semana, com muita gente fazendo requisições, às vezes vale a pena criar um servidor dedicado e deixá-lo ligado. Em regras de negócio com consultas esporádicas, o serverless deixa o processamento basicamente gratuito. Cloud SQL: o banco de dados e o seu custo Os dados ficam no Cloud SQL. O Google tem serviços de banco de dados mais robustos, como o Spanner, mas o projeto só precisa de um pequeno banco Postgres. Ele foi criado na menor instância possível, com 10 GB de armazenamento. Quem nunca teve conta no GCP ganha créditos ao criá-la, em torno de 300 dólares, dependendo da época. Com eles, toda essa infraestrutura fica basicamente gratuita. No meu caso, como tenho conta há bastante tempo, não tenho crédito em alguns desses serviços. Mesmo assim, com a aplicação inteira rodando por mais de um mês, o gasto foi de R$ 30.

### ATENÇÃO — O Cloud SQL cobra mesmo sem uso

De todos os serviços do projeto, o que continua cobrando é o Cloud SQL, porque a instância é cobrada por tamanho. Usando ou não o banco, os 10 GB estão reservados. Por isso, a infraestrutura deve ser desmontada quando o projeto termina, para não ficar consumindo recursos.

O Cloud SQL permite subir Postgres, MySQL e, ao que parece, também Oracle e SQL Server. O projeto usa o Postgres por causa das extensões. Ele é um banco relacional normal, com tabelas, colunas e índices, mas a comunidade criou várias extensões que permitem usá-lo em diversas aplicações. pgvector: o Postgres como banco de dados vetorial A extensão usada no projeto é a pgvector. Ela transforma o Postgres em um banco de dados vetorial e permite fazer buscas vetoriais com a linguagem SQL.

### Banco de dados vetorial

Banco que guarda embeddings, isto é, o texto em forma numérica, do mesmo jeito que uma LLM processa informação: matrizes de números. Com eles, é possível buscar por semântica, por proximidade de contexto.

### "Casa" e "lar"

Em uma busca por palavra, "lar" e "casa" não são a mesma coisa. Semanticamente, porém, são termos muito próximos. Uma busca por "eu quero ver minha casa" pode devolver "este é o seu lar".

Existem bancos de dados vetoriais específicos, nativos, oferecidos como serviço. O Postgres, porém, é extremamente versátil e pode ser uma opção válida na sua arquitetura. Uma aplicação que já roda Postgres e precisa de um RAG, por exemplo para um chatbot de atendimento, não precisa de outro banco de dados: pode usar o próprio Postgres. Dá para criar outra instância, mas o ganho da extensão é aproveitar todo o conhecimento que a equipe já tem do Postgres.

### Secret Manager: o cofre de segredos

Tudo o que foi descrito precisa de secrets e senhas. Por segurança, tanto no ambiente local quanto na nuvem, eles não ficam em nenhum local estático do código. Na nuvem, ficam no Secret Manager, um cofre seguro: toda vez que um serviço precisa de uma senha, ele a busca ali e a consome. No ambiente local, as informações sensíveis ficam em variáveis de ambiente. O cofre guarda as chaves dos serviços internos, como a do banco de dados, e as dos serviços externos ao GCP:

O termo vault, cofre, aparece com frequência para esse tipo de serviço. É o jeito seguro de guardar secrets, e pensar em segurança da informação é parte do projeto.

- o Langfuse, serviço de observabilidade de LLMs, que precisa de API keys e de secret;
- o exportador do OpenTelemetry, usado para enviar ao Grafana as métricas de serviço, a observabilidade
- o Serper, serviço de busca de informações via API.

### Artifact Registry: as imagens Docker

O Artifact Registry guarda a imagem Docker criada para o serviço de backend. Ele guarda também as versões: a cada imagem nova, a anterior é versionada. O Artifact Registry só armazena as imagens. Quem as executa é o Cloud Run.

## Pontos de atenção

- A escolha do Google Cloud não é uma obrigação. No seu projeto, você pode usar qualquer solução de nuvem,
- seu garden de modelos, talvez com outros modelos, não necessariamente com o Gemini.
- demanda, sem nenhuma configuração manual. Enquanto ninguém acessa, não há nenhum servidor de backend
- Quem nunca teve conta no GCP ganha créditos ao criá-la, em torno de 300 dólares, dependendo da época.
- tempo, não tenho crédito em alguns desses serviços. Mesmo assim, com a aplicação inteira rodando por mais
- ATENÇÃO  ·  O Cloud SQL cobra mesmo sem uso
- tamanho. Usando ou não o banco, os 10 GB estão reservados. Por isso, a infraestrutura deve ser desmontada

## Checkpoint

- [ ] Você consegue explicar o papel de cada peça do Google Cloud na arquitetura do projeto sem consultar o

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
