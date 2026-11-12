# Relatório dos materiais — Unidade 1: Setup e Deploy Inicial

> Capstone AI Researcher · aulas 1–7  
> Pasta: `modulo-11-exemplo-1-setup-deploy-inicial/materiais_aula`

## O que esta unidade constrói

Do **primeiro commit** ao **primeiro deploy na nuvem**, ainda sem o cérebro do agente. No fim você tem:

- regras do agente de código (`CLAUDE.md` + skills)
- mapa GCP (Cloud Run, Cloud SQL+pgvector, Firebase, Vertex, Secrets)
- esteira GitHub Actions com autenticação segura (WIF)
- corpus CVM pronto para o RAG
- **walking skeleton** em produção (health check + Angular mínimo)

## Como estudar (ordem intuitiva)

```
1. Entenda o caso     →  Diagrama 1.1 (RAG corretivo)
2. Veja a nuvem       →  Diagrama 1.3 (mapa GCP)
3. Veja a segurança   →  Diagrama 1.4 (WIF)
4. Leia as aulas      →  docs/exemplo_aula/AULA_01…07
5. Pratique no seed   →  fork/clone ai-researcher-seed
6. Valide             →  checkpoint no fim deste relatório
```

## Slides desta unidade

| Arquivo | Lê em 1 frase | Quando abrir |
|---------|---------------|--------------|
| [`Diagrama 1.1 — RAG corretivo (fluxo em alto nível).pptx`](./Diagrama%201.1%20—%20RAG%20corretivo%20(fluxo%20em%20alto%20nível).pptx) | Pergunta → base vetorial → contexto suficiente? → citação ou busca web | Antes de qualquer código |
| [`Diagrama 1.3 — Mapa de infraestrutura GCP.pptx`](./Diagrama%201.3%20—%20Mapa%20de%20infraestrutura%20GCP.pptx) | Actions → Artifact Registry → Cloud Run + Firebase + Cloud SQL + Vertex + Secrets | Ao falar de arquitetura |
| [`Diagrama 1.4 — Workload Identity Federation.pptx`](./Diagrama%201.4%20—%20Workload%20Identity%20Federation.pptx) | Sem chave JSON estática: Actions assume identidade federada | Antes do deploy |

### Leitura guiada do Diagrama 1.1

1. Usuário pergunta.
2. Sistema consulta a **base vetorial** (indicadores CVM).
3. Losango: **contexto suficiente?**
   - **sim** → resposta com **citação** (fonte + data-base).
   - **não** → **busca na web** (fallback) e só então responde com citação.
4. Regra de ouro: **nunca recomenda compra/venda** — isso fica no **código**, não só no system prompt.

### Leitura guiada do Diagrama 1.3

| Peça | Função didática |
|------|-----------------|
| GitHub Actions | Build, teste e deploy a cada push |
| Artifact Registry | Guarda a imagem Docker |
| Cloud Run | API Fastify (Node) — paga por requisição |
| Firebase Hosting | Angular estático; `/api` reescreve para Cloud Run |
| Cloud SQL + pgvector | Banco do RAG |
| Vertex AI | Embedding + geração |
| Secret Manager | Cofre — nada de secret no Git |

### Leitura guiada do Diagrama 1.4

- **Evitar:** chave de service account em JSON no repo ou em secret “solto” permanente.
- **Preferir:** Workload Identity Federation — o runner do GitHub troca um token OIDC de curta duração por permissão no GCP.

## Mapa das aulas (PDF)

| Aula | Arquivo local | Ideia central |
|------|---------------|---------------|
| 1 | [`../docs/exemplo_aula/AULA_01_BEM_VINDO.md`](../docs/exemplo_aula/AULA_01_BEM_VINDO.md) | O que é o AI Researcher e o RAG corretivo |
| 2 | [`../docs/exemplo_aula/AULA_02_CLAUDE_MD_SKILLS.md`](../docs/exemplo_aula/AULA_02_CLAUDE_MD_SKILLS.md) | CLAUDE.md = memória do agente; skills = procedimentos |
| 3 | [`../docs/exemplo_aula/AULA_03_TOUR_GCP.md`](../docs/exemplo_aula/AULA_03_TOUR_GCP.md) | Peças GCP e equivalentes em outras nuvens |
| 4 | [`../docs/exemplo_aula/AULA_04_GITHUB_ACTIONS.md`](../docs/exemplo_aula/AULA_04_GITHUB_ACTIONS.md) | YAML: `on` → `jobs` → `steps`; WIF vs chave estática |
| 5 | [`../docs/exemplo_aula/AULA_05_CORPUS_CVM.md`](../docs/exemplo_aula/AULA_05_CORPUS_CVM.md) | Dados abertos CVM; template fixo (não LLM) para o parágrafo |
| 6 | [`../docs/exemplo_aula/AULA_06_FUNDACAO_GCP.md`](../docs/exemplo_aula/AULA_06_FUNDACAO_GCP.md) | Provisionar projeto, APIs, SQL, secrets com mínima permissão |
| 7 | [`../docs/exemplo_aula/AULA_07_WALKING_SKELETON.md`](../docs/exemplo_aula/AULA_07_WALKING_SKELETON.md) | Health check + Angular + deploy zero |

## Conceitos que não podem confundir

| Confusão comum | Correção |
|----------------|----------|
| “O system prompt impede recomendação” | A restrição também (e principalmente) está no **código** |
| “Preciso de banco vetorial separado” | **pgvector** no Postgres já resolve |
| “Secret no Actions = seguro para sempre” | Melhor ainda: **WIF** sem JSON estático |
| “Deploy zero = agente completo” | É só o **esqueleto** (health); o grafo vem na Unidade 2 |

## Roteiro prático sugerido

1. Fork/clone do [ai-researcher-seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) (branch `starter`).
2. Ler `CLAUDE.md` e listar o que o agente deve perguntar antes de fazer.
3. Abrir os 3 PPTX nesta pasta na ordem 1.1 → 1.3 → 1.4.
4. Seguir o provisionamento GCP (aula 6) e o deploy zero (aula 7).
5. Comparar com a referência [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).

## Checkpoint

- [ ] Desenhar de memória o fluxo do Diagrama 1.1
- [ ] Nomear as 7 peças do mapa GCP e o papel de cada uma
- [ ] Explicar WIF em uma frase
- [ ] Distinguir seed × projeto completo
- [ ] Seguir o guia Capstone em [`../exemplo_real/README.md`](../exemplo_real/README.md)

## Relatório didático da unidade

[`../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)
