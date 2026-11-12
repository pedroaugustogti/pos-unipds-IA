# Mapa — Unidade 1: Ideação, Setup e Deploy Inicial

> Capstone AI Researcher · aulas 1-7

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher

## Aulas desta unidade

### Aula 1 — Bem-vindo ao Capstone

Arquivo: [`AULA_01_BEM_VINDO.md`](./AULA_01_BEM_VINDO.md)

O que você deve sair sabendo:

- Reconhecer o que a disciplina constrói: o AI Researcher, um chatbot especializado em investimentos de bolsa, do primeiro commit à produção.
- Explicar, em alto nível, a regra de negócio do agente: buscar na base vetorial, julgar o contexto e recorrer à web quando ele não basta.
- Justificar por que a restrição de não recomendar investimentos é garantida no código, e não apenas no system prompt.

### Aula 2 — CLAUDE.md e AI Dev Skills

Arquivo: [`AULA_02_CLAUDE_MD_SKILLS.md`](./AULA_02_CLAUDE_MD_SKILLS.md)

O que você deve sair sabendo:

- Preparar o ponto de partida do projeto: fazer o fork do repositório, clonar e trabalhar na branch starter.
- Explicar o papel do CLAUDE.md como arquivo de contexto e de regras de trabalho que o agente carrega em toda interação.
- Diferenciar o CLAUDE.md das skills e aplicar a regra de precedência entre a skill oficial de um framework e a skill do próprio projeto.

### Aula 3 — Tour pelo Google Cloud

Arquivo: [`AULA_03_TOUR_GCP.md`](./AULA_03_TOUR_GCP.md)

O que você deve sair sabendo:

- Identificar as peças do Google Cloud que sustentam o projeto e o papel de cada uma na arquitetura.
- Explicar por que o projeto usa um backend serverless no Cloud Run e o Postgres com a extensão pgvector no

### Aula 4 — GitHub e GitHub Actions

Arquivo: [`AULA_04_GITHUB_ACTIONS.md`](./AULA_04_GITHUB_ACTIONS.md)

O que você deve sair sabendo:

- Explicar o papel do GitHub Actions como a peça que faz build, teste e deploy a cada push.
- Comparar a autenticação por chave estática guardada em secret com a autenticação por workload identity pool, de chaves efêmeras.
- Reconhecer a estrutura de um arquivo YAML do GitHub Actions: gatilho, jobs, máquina de execução e steps.

### Aula 5 — Corpus CVM

Arquivo: [`AULA_05_CORPUS_CVM.md`](./AULA_05_CORPUS_CVM.md)

O que você deve sair sabendo:

- Explicar por que os dados do sistema vêm da CVM e por que os parágrafos do corpus nunca são gerados por

### Aula 6 — Fundação GCP

Arquivo: [`AULA_06_FUNDACAO_GCP.md`](./AULA_06_FUNDACAO_GCP.md)

O que você deve sair sabendo:

- Provisionar a fundação do projeto no Google Cloud com prompts ao Claude Code: projeto, APIs, Artifact

### Aula 7 — Walking Skeleton e Deploy Zero

Arquivo: [`AULA_07_WALKING_SKELETON.md`](./AULA_07_WALKING_SKELETON.md)

O que você deve sair sabendo:

- Construir o esqueleto do projeto: uma API com health check, uma aplicação Angular que a consome e um

## Relatórios

- Didático da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
- Materiais (PDF/slides): [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)
