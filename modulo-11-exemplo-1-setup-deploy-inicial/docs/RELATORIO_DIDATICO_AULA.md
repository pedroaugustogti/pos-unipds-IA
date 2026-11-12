# Relatório Didático — Ideação, Setup e Deploy Inicial

> Aula `modulo-11-exemplo-1-setup-deploy-inicial`  
> Capstone AI Researcher · aulas 1-7

## Objetivo da unidade

Montar o terreno do Capstone: entender o AI Researcher, configurar o agente de código, conhecer o mapa GCP, preparar o corpus CVM e colocar um walking skeleton em produção.

## Percurso das aulas

| Aula | Arquivo | Síntese |
|------|---------|---------|
| 1 | [`AULA_01_BEM_VINDO.md`](./AULA_01_BEM_VINDO.md) | Reconhecer o que a disciplina constrói: o AI Researcher, um chatbot especializado em investimentos de bolsa, do primeiro commit à produção. |
| 2 | [`AULA_02_CLAUDE_MD_SKILLS.md`](./AULA_02_CLAUDE_MD_SKILLS.md) | Preparar o ponto de partida do projeto: fazer o fork do repositório, clonar e trabalhar na branch starter. |
| 3 | [`AULA_03_TOUR_GCP.md`](./AULA_03_TOUR_GCP.md) | Identificar as peças do Google Cloud que sustentam o projeto e o papel de cada uma na arquitetura. |
| 4 | [`AULA_04_GITHUB_ACTIONS.md`](./AULA_04_GITHUB_ACTIONS.md) | Explicar o papel do GitHub Actions como a peça que faz build, teste e deploy a cada push. |
| 5 | [`AULA_05_CORPUS_CVM.md`](./AULA_05_CORPUS_CVM.md) | Explicar por que os dados do sistema vêm da CVM e por que os parágrafos do corpus nunca são gerados por |
| 6 | [`AULA_06_FUNDACAO_GCP.md`](./AULA_06_FUNDACAO_GCP.md) | Provisionar a fundação do projeto no Google Cloud com prompts ao Claude Code: projeto, APIs, Artifact |
| 7 | [`AULA_07_WALKING_SKELETON.md`](./AULA_07_WALKING_SKELETON.md) | Construir o esqueleto do projeto: uma API com health check, uma aplicação Angular que a consome e um |

## Caso permanente

O **AI Researcher** busca na base vetorial (CVM), julga se o contexto basta, recorre à web quando não basta e responde com **citação** (fonte + data-base). Nunca recomenda compra ou venda — a restrição vive no **código**, não só no system prompt.

## Como estudar

1. Abrir [`MAPA_AULAS.md`](./MAPA_AULAS.md) e ler a aula na ordem.
2. Conferir slides/roteiro em [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md).
3. Reproduzir no [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) ou no [projeto completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).
4. Anotar a ponte Guardião em [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md).

## Checkpoint da unidade

- [ ] Explicar o objetivo da Unidade 1 em duas frases
- [ ] Completar o checkpoint de cada aula 1-7
- [ ] Relacionar ao menos um conceito ao Guardião Família
