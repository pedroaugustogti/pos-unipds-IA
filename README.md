# POS — Engenharia de IA Aplicada

Repositório com **exemplos práticos** da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**: modelos em JavaScript/TypeScript, LLMs, **LangGraph**, embeddings, **Neo4j**, **RAG**, **MCP** e **Agent Skills** no Cursor.

Cada pasta `modulo-X-exemplo-Y-*` segue um **padrão didático** nos `README.md`: objetivo da atividade, passo a passo, critérios de sucesso e relação com o módulo. Referência de estilo: [`modulo-3-exemplo-4-skills/sample-video-ffmpeg/README.md`](./modulo-3-exemplo-4-skills/sample-video-ffmpeg/README.md).

O [`delivery-agent/`](./delivery-agent/) na raiz automatiza a preparação da próxima aula (comparar UNIPDS, scaffold, READMEs e commit).

---

## Módulo 1 — Fundamentos de IA e LLMs

**O que você aprende:** partir do zero com ML no Node.js, consumir LLMs locais e na nuvem, gerar **embeddings** e montar pipelines de **busca semântica** e **RAG** com grafo.

| Exemplo | Pasta | Principais aprendizados |
|---------|-------|-------------------------|
| 1 | [`modulo-1-exemplo-1-training-model`](./modulo-1-exemplo-1-training-model/) | TensorFlow.js no servidor: tensores, modelo simples, treino/inferência |
| 2 | [`modulo-1-exemplo-2- e-commerce`](./modulo-1-exemplo-2-%20e-commerce/) | Recomendação em e-commerce com rede neural e front estático |
| 3 | [`modulo-1-exemplo-3-duck game`](./modulo-1-exemplo-3-duck%20game/) | Jogo Duck Hunt com detecção/ML no browser |
| 4 | [`modulo-1-exemplo-4-ollama`](./modulo-1-exemplo-4-ollama/) | API **Ollama** local (compatível OpenAI) via `curl` |
| 5 | [`modulo-1-exemplo-5-open router`](./modulo-1-exemplo-5-open%20router/) | Chamadas à API **OpenRouter** com variáveis de ambiente |
| 6 | [`modulo-1-exemplo-6-embeddings-neo4j`](./modulo-1-exemplo-6-embeddings-neo4j/) | Embeddings locais (Transformers.js) + indexação vetorial no **Neo4j** |
| 7 | [`modulo-1-exemplo-7-embeddings-rag-neo4j`](./modulo-1-exemplo-7-embeddings-rag-neo4j/) | **RAG** completo: retrieve no Neo4j + geração com LLM (LangChain + OpenRouter) |

**Competências do módulo:** fundamentos de ML em JS; integração com LLMs; vetorização; recuperação aumentada por contexto.

---

## Módulo 2 — LangGraph e agentes

**O que você aprende:** construir **agentes com estado**, memória persistente, guardrails, consultas em grafo e análise multimodal de documentos.

| Exemplo | Pasta | Principais aprendizados |
|---------|-------|-------------------------|
| 1 | [`modulo-2-exemplo-1-langgraph-medical-appointment`](./modulo-2-exemplo-1-langgraph-medical-appointment/) | Agente **LangGraph** para agendamento médico (intenções, tools, multi-nó) |
| 2 | [`modulo-2-exemplo-2-song-highlights`](./modulo-2-exemplo-2-song-highlights/) | Memória conversacional com **checkpointer** e recomendação musical |
| 3 | [`modulo-2-exemplo-3-safe-guard`](./modulo-2-exemplo-3-safe-guard/) | **Prompt injection**, perfis de acesso e guardrails |
| 4 | [`modulo-2-exemplo-4-neo4j-students`](./modulo-2-exemplo-4-neo4j-students/) | **Text-to-Cypher** com LangGraph sobre dados de alunos no Neo4j |
| 5 | [`modulo-2-exemplo-5-doc-analysis`](./modulo-2-exemplo-5-doc-analysis/) | Q&A **multimodal** em PDF (LangGraph + Fastify + visão) |

**Competências do módulo:** grafos de agentes; persistência de estado; segurança em LLMs; integração banco de grafos + LLM.

---

## Módulo 3 — MCP na prática

**O que você aprende:** conectar agentes a ferramentas externas via **Model Context Protocol (MCP)**, criar servidores, integrar APIs legadas e aplicar **autenticação e rate limiting**.

| Exemplo | Pasta | Principais aprendizados |
|---------|-------|-------------------------|
| 1 | [`modulo-3-exemplo-1-mcp-tools`](./modulo-3-exemplo-1-mcp-tools/) | Agente **LangGraph** consumindo **tools MCP** (pipeline de dados) |
| 2 | [`modulo-3-exemplo-2-google-trends-agent`](./modulo-3-exemplo-2-google-trends-agent/) | Agente com **Google Trends** + structured outputs |
| 3 | [`modulo-3-exemplo-3-dev-instructions-events`](./modulo-3-exemplo-3-dev-instructions-events/) | **Dev instructions**, agents customizados e MCP Playwright |
| 4 | [`modulo-3-exemplo-4-skills`](./modulo-3-exemplo-4-skills/) | **Agent Skills** ([skills.sh](https://www.skills.sh/)): browser, FFmpeg — ver [`sample-video-ffmpeg`](./modulo-3-exemplo-4-skills/sample-video-ffmpeg/) |
| 5 | [`modulo-3-exemplo-5-server-mcp`](./modulo-3-exemplo-5-server-mcp/) | Criar **servidor MCP do zero** (criptografia AES-256-CBC) |
| 6 | [`modulo-3-exemplo-6-mcp-integration-api`](./modulo-3-exemplo-6-mcp-integration-api/) | **API legada** (Fastify + MongoDB) exposta como MCP |
| 7 | [`modulo-3-exemplo-7-security-auth-mcp`](./modulo-3-exemplo-7-security-auth-mcp/) | **Auth**, role/departamento, service token, **rate limit** e anti-DDoS |
| 8 | [`modulo-3-exemplo-8-publish-mcp`](./modulo-3-exemplo-8-publish-mcp/) | **Publicar MCP** no Verdaccio (privado) e no **npm público** (`@gorgan/customers-mcp`); consumir no Cursor via `customers-mcp-public` |
| 9 | [`modulo-3-exemplo-9-mcp-langchain`](./modulo-3-exemplo-9-mcp-langchain/) | **LangChain + MCP**: `MultiServerMCPClient` conecta `@gorgan/customers-mcp` (ex. 8) e filesystem; agente LangGraph com OpenRouter e LangSmith Studio |

**Competências do módulo:** protocolo MCP; tools/resources/prompts; adaptação de sistemas legados; segurança em integrações agenticas; empacotamento e distribuição via npm; **ponte MCP → LangChain** para agentes com tool calling.

### Fluxo de publicação do MCP (Exemplo 8)

O exemplo 8 fecha o arco do Módulo 3: o mesmo servidor MCP dos exemplos 6 e 7 vira um **pacote npm** instalável com `npx`, sem clonar o repositório.

```
Código MCP (ex. 6/7)
        ↓
package.json (bin, files, publishConfig)
        ↓
Registry privado (Verdaccio :4873)  →  npm run release:private
        ↓
Registry público (npmjs.org)        →  npm run release:public
        ↓
Cursor (.cursor/mcp.json)            →  customers-mcp-public
        ↓
Agente chama tools (list/create/get/update/delete)
```

| Etapa | Comando / artefato | Resultado |
|-------|-------------------|-----------|
| API legada | `modulo-3-exemplo-7-security-auth-mcp/legacy-api/start-docker.cmd` | `SERVICE_TOKEN` em `http://127.0.0.1:9999` |
| Registry privado | `npm run registry:start` + `registry:setup` + `release:private` | `@pedroaugusto/customers-mcp` no Verdaccio |
| Registry público | `npm run release:public` | [`@gorgan/customers-mcp`](https://www.npmjs.com/package/@gorgan/customers-mcp) no npmjs.org |
| Validação | `npm run validate:e2e` | CRUD completo via `npx` |
| Cursor | `scripts/start-public-mcp.mjs` | MCP conectado com 5 tools |

### Fluxo LangChain + MCP (Exemplo 9)

O exemplo 9 fecha o arco **MCP → agente**: o pacote publicado no exemplo 8 deixa de ser consumido só pelo Cursor e passa a ser **tool do LangChain**, orquestrado por um grafo LangGraph com LLM.

```
Pacote MCP publicado (ex. 8) — @gorgan/customers-mcp
        ↓
Launcher local (start-public-mcp.mjs) — stdio + SERVICE_TOKEN da API :9999
        ↓
@langchain/mcp-adapters (MultiServerMCPClient)
        ↓
LangChain Tools (create_customer, list_customers, … + filesystem em data/)
        ↓
createAgent() + OpenRouter (tool calling)
        ↓
LangGraph (graph multiple_mcp_tools) — Studio / API / CLI
        ↓
LLM executa CRUD real na API legada e retorna resultado ao usuário
```

| Etapa | Comando / artefato | Resultado |
|-------|-------------------|-----------|
| API legada | `modulo-3-exemplo-7-security-auth-mcp/legacy-api/start-docker.cmd` | Token para o MCP customers |
| Conexão MCP | `npm run validate:mcp-tools` | ~19 tools (5 customers + filesystem) |
| Agente completo | `npm run validate:langgraph` | 10× `create_customer` + `list_customers` |
| LangGraph Studio | `npm run langgraph:serve` | Chat em `smith.langchain.com/studio?baseUrl=http://localhost:2024` |

Detalhes da integração (camadas, diagrama, troubleshooting): [`modulo-3-exemplo-9-mcp-langchain/README.md`](./modulo-3-exemplo-9-mcp-langchain/README.md).

---

## Módulo 4 — Agentes autônomos

**O que você aprende:** definir agentes por **contratos** (YAML em Markdown), runtime Python com ciclo perceber→planejar→agir→avaliar, e automação de entrega (commit/push) com comparação ao repositório oficial UNIPDS.

| Exemplo | Pasta | Principais aprendizados |
|---------|-------|-------------------------|
| 1 | [`modulo-4-exemplo-1-agente-ia-contratos`](./modulo-4-exemplo-1-agente-ia-contratos/) | **Contratos de agente** (`agent.md`, `skills.md`, `rules.md`); runtime Python; [`delivery-agent`](./delivery-agent/) na raiz compara UNIPDS vs repo local, sugere próximo `modulo-X-exemplo-Y` e prepara **commit** (sem PR) |
| 2 | [`modulo-4-exemplo-2-runtime`](./modulo-4-exemplo-2-runtime/) | **Por dentro do runtime** — 6 módulos Python (`contratos`, `ciclo`, `planejador`, `ferramentas`, `executor`, `telemetria`); trace → código; `monitor-agent` com telemetria completa |
| 3 | [`modulo-4-exemplo-3-observabilidade`](./modulo-4-exemplo-3-observabilidade/) | **Observabilidade em 4 níveis** — `trace-analyzer`, comando `analisar`, `analise-agente.md`; planejador `auto`/`llm`; ferramentas determinísticas |
| 4 | [`modulo-4-exemplo-4-tipos-agentes-e-projetos`](./modulo-4-exemplo-4-tipos-agentes-e-projetos/) | **Tipos de agente** — `backlog-decomposer` (`goal_oriented`), modos `interactive` / `autonomous`, contract-driven development ([aula06 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula06-tipos-agentes-e-projetos)) |
| 5 | [`modulo-4-exemplo-5-arquiteturas-cognitivas`](./modulo-4-exemplo-5-arquiteturas-cognitivas/) | **Arquiteturas cognitivas** — `--arquitetura react`, campo `raciocínio` no trace, contratos em `architectures/` ([aula07 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula07-arquiteturas-cognitivas)) |
| 6 | [`modulo-4-exemplo-6-plan-execute-e-reflection`](./modulo-4-exemplo-6-plan-execute-e-reflection/) | **Plan-Execute e Reflection** — `--arquitetura plan_execute` / `reflect`, `critic.md`, autocritica antes de finalizar ([aula08 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula08-plan-execute-e-reflection)) |
| 7 | [`modulo-4-exemplo-7-evals-e-frameworks-mercado`](./modulo-4-exemplo-7-evals-e-frameworks-mercado/) | **Evals e frameworks de mercado** — dataset + eval suite YAML, `benchmark`/`comparar`, relatórios `report.md` e equivalências LangChain/LangGraph ([aula09 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula09-evals-e-frameworks-mercado)) |
| 8 | [`modulo-4-exemplo-8-de-mock-para-real`](./modulo-4-exemplo-8-de-mock-para-real/) | **De mock para real** — padrão Adapter, `tipo_implementacao: rest` no contrato, `rest_adapter.py`, API local FastAPI; mock e REST no mesmo agente ([aula10 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula10-de-mock-para-real)) |
| 9 | [`modulo-4-exemplo-9-database-e-mcp`](./modulo-4-exemplo-9-database-e-mcp/) | **Database, segurança e MCP** — `db_adapter.py`, `mcp_adapter.py`, SQLite (`seed_logs.py`), MCP stdio (`mcp/server.py`); 6 tools com 4 adapters (REST + database + MCP + mock); políticas e hooks; E2E validado (`trace_id` `97117d352739`) ([aula11 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula11-database-e-mcp)) |
| 10 | [`modulo-4-exemplo-10-tool-selection-eval`](./modulo-4-exemplo-10-tool-selection-eval/) | **Tool selection eval** — dataset com gabarito (`tool_selection_cases.json`), 4 métricas + suites v1/v2/LLM, CLI `tool-eval`/`tool-eval-comparar`; padrao/reflect **87,5%** com LLM; refinamento de `skills.md` ([aula12 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula12-tool-selection-eval)) |
| 11 | [`modulo-4-exemplo-11-agente-que-lembra`](./modulo-4-exemplo-11-agente-que-lembra/) | **Agente Que Lembra** — material base UNIPDS adaptado para o padrao pos-unipds-IA |
| 12 | [`modulo-4-exemplo-12-embeddings-reflexao-evolutiva`](./modulo-4-exemplo-12-embeddings-reflexao-evolutiva/) | **Embeddings Reflexao Evolutiva** — `embedding_adapter.py` (indexar/buscar/reindexar), memória contextual via OpenRouter, `reflection.md` + `reflection_store/`, lazy reindex; validação local com SQLite (`validar_execucao_embeddings.py`, sim ≥ 0,7) ([aula14 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula14-embeddings-reflexao-evolutiva)) |
| 13 | [`modulo-4-exemplo-13-evals-memoria`](./modulo-4-exemplo-13-evals-memoria/) | **Evals de memória** — `memory_eval.py`, `MEMORY_DISABLED=1`, dataset `memory_impact_cases.json`, 6 métricas, comparação com vs sem memória; **fechamento da Unidade 4** ([aula15 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula15-evals-memoria)) |

**Competências do módulo:** agentes orientados a contratos; planejamento com LLM (OpenRouter); ferramentas reais (git + GitHub API); governança de entrega sem abrir PR automaticamente; **observabilidade** (trace, KPIs, análise automatizada); **tipos de agente** (task_based, interactive, goal_oriented, autonomous) e decomposição de backlog; **arquiteturas cognitivas** (ReAct, Plan-Execute, Reflection); **evals** mensuráveis; **padrão Adapter** (REST, database, MCP declarados no contrato, secrets no `.env`).

---

## Módulo 5 — Ferramentas de IA para UI e UX

**O que você aprende:** aplicar IA como camada de engenharia no ciclo de produto — refinamento de requisitos, prototipação, agentes CLI, automação com MCP e integração de lógica de IA no front/back.

| Exemplo | Pasta | Principais aprendizados |
|---------|-------|-------------------------|
| 1 | [`modulo-5-exemplo-1-discovery-refinement`](./modulo-5-exemplo-1-discovery-refinement/) | **Discovery e refinamento AI-First** — prompts versionados, edge cases, Mermaid, data sanitizer, backlog; critérios UNIPDS ✅ ([modulo-01 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-01)) |
| 2 | [`modulo-5-exemplo-2-prototyping-ui`](./modulo-5-exemplo-2-prototyping-ui/) | **Prototyping UI** — app **Angular 21** Pix Agendado a partir das specs do Ex. 1; Figma/Stitch → componentes; critérios UNIPDS ✅ ([modulo-02 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02)) |
| 3 | [`modulo-5-exemplo-3-agents-cli`](./modulo-5-exemplo-3-agents-cli/) | **Agents CLI** — refatoração segura do `pix-app` com Gemini CLI / terminal ([modulo-03 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03)) |
| 4 | *próximo* [`modulo-04`](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04) | **Automação MCP** — testes E2E e depuração via MCP |
| 5 | *próximo* [`modulo-05`](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05) | **AI Integration** — Firebase AI Logic e APIs |

**Competências do módulo:** engenharia de prompts estruturados; refinamento técnico de requisitos; diagramação com Mermaid; data discovery; redução de variabilidade antes do código; integração de IA em produtos digitais.

---

## Requisitos gerais

| Recurso | Onde é necessário |
|---------|-------------------|
| **Node.js 22+** (24+ no Módulo 3 MCP) | Maioria dos exemplos TS/JS |
| **Python 3.10+** | Módulo 4 Exemplo 1 (runtime do agente por contratos) |
| **Docker** | Neo4j (M1 ex. 6–7), Postgres (M2 ex. 2), APIs legadas (M3 ex. 6–7) |
| **`.env`** | Chaves OpenRouter, Neo4j, etc. (copiar de `.env.example` quando existir) |
| **LangGraph Studio** | `npm run langgraph:serve` nos projetos do Módulo 2 e no **Módulo 3 Exemplo 9** |
| **Cursor / VS Code** | Módulo 3 (MCP e Skills) |
| **FFmpeg** | Módulo 3 Exemplo 4 (skills de vídeo) |

## MCP configurado no workspace

O arquivo [`.cursor/mcp.json`](./.cursor/mcp.json) registra servidores dos exemplos 5, 6, 7 e 8:

| Servidor | Exemplo |
|----------|---------|
| `ciphersuite-mcp` | Exemplo 5 — criptografia |
| `customers-mcp` | Exemplo 6 — API legada |
| `customers-secure-mcp` | Exemplo 7 — API com auth |
| `customers-mcp-public` | Exemplo 8 — pacote npm público [`@gorgan/customers-mcp`](https://www.npmjs.com/package/@gorgan/customers-mcp) |

Para o **Exemplo 8**, o launcher `modulo-3-exemplo-8-publish-mcp/scripts/start-public-mcp.mjs` obtém o `SERVICE_TOKEN` da API legada e inicia o MCP in-process (compatível com Node 22 do Cursor). Recarregue o MCP em **Settings → MCP** após subir a API na porta 9999.

O **Exemplo 9** reutiliza o mesmo launcher programaticamente (transporte **stdio** via `customersTool.ts`) — não depende do `.cursor/mcp.json`; o agente LangGraph sobe o MCP como processo filho em cada execução.

## Como navegar

1. Escolha o módulo e abra a pasta do exemplo.
2. Leia o `README.md` da pasta (objetivo + passo a passo).
3. Siga os critérios de sucesso com checkbox antes de considerar a atividade concluída.

## Autor / contexto

Exemplos derivados do material **UNIPDS** / **Erick Wendel** (Node, LangChain, MCP). Ajustes, extensões e documentação didática: **Pedro Augusto** ([`pedroaugustogti/pos-unipds-IA`](https://github.com/pedroaugustogti/pos-unipds-IA)).
