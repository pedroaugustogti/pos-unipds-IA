# Relatório explicativo — execução do Capstone (Módulo 11)

> Run de evidências: `evidencias/run-2026-11-11T220837Z`  
> Workspace: `ai-researcher-seed` + `capstone-project-ai-researcher`  
> Script: [`../scripts/run_evidencias_capstone.py`](../scripts/run_evidencias_capstone.py)

## 1. O que foi feito

Percorremos **as 24 aulas** do Capstone (unidades 1–5) mapeando, para cada uma:

1. **Ferramenta da vídeo-aula** (GCP, Actions, pgvector, Serper, MCP, Playwright, Langfuse…)  
2. **Artefato no código** (seed e/ou projeto completo)  
3. **Prompt oficial da aula** (`prompts_aula/` no projeto completo)  
4. **Evidência executada** neste ambiente (`evidencias/run-…/aula-XX/`)  
5. **Conteúdo teórico** nas pastas `modulo-11-exemplo-1` … `5`

### Status agregado

| Status | Significado | Qtd (esta run) |
|--------|-------------|----------------|
| `executado` | Check local concluído com artefato OK | 15 |
| `parcial` | Artefato/repo OK; falta cloud, Docker daemon, key ou runtime | 8 |
| `hitl` | Exige humano (billing/IAM/custo) | 1 |
| `simulado` | Só documentação, sem artefato | 0 |

**Bloqueios deste ambiente na run:** Docker Desktop **não estava com o daemon ativo** (`dockerDesktopLinuxEngine`); `pnpm install` via `CreateProcess` falhou no path do shim (usar `pnpm.cmd` em reexecução).

---

## 2. Ambientes clonados (evidência)

| Repo | Papel | Evidência |
|------|-------|-----------|
| [ai-researcher-seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) | Walking skeleton (U1) | `workspace/ai-researcher-seed` |
| [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher) | Projeto completo (U2–U5) | `workspace/capstone-project-ai-researcher` |

Pacotes no projeto completo (snapshot): `agent`, `contracts`, `corpus`, `mcp-server` — ver `evidencias/run-…/packages_snapshot.json`.

Prompts oficiais das vídeo-aulas copiados para `evidencias/run-…/prompts_aula_index/` (20 arquivos `aula-*.md`).

---

## 3. Mapa aula → ferramenta → evidência → teoria

### Unidade 1 — Setup e Deploy

| Aula | Ferramenta (vídeo) | Automação | Evidência | Teoria |
|------|--------------------|-----------|-----------|--------|
| 1 | GitHub + RAG corretivo | Git clone / GitHub MCP | [`aula-01`](../evidencias/run-2026-11-11T220837Z/aula-01/EVIDENCIA.md) · slides 1.1 | [`AULA_01`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_01_BEM_VINDO.md) |
| 2 | CLAUDE.md / skills | Filesystem + skills | [`aula-02`](../evidencias/run-2026-11-11T220837Z/aula-02/EVIDENCIA.md) · `.claude/skills`, `.agents/skills` | [`AULA_02`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_02_CLAUDE_MD_SKILLS.md) |
| 3 | GCP Console / mapa | Playwright MCP (UI) · gcloud MCP | [`aula-03`](../evidencias/run-2026-11-11T220837Z/aula-03/EVIDENCIA.md) · `infra/`, `firebase.json`, compose pgvector | [`AULA_03`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_03_TOUR_GCP.md) |
| 4 | GitHub Actions + WIF | GitHub MCP | [`aula-04`](../evidencias/run-2026-11-11T220837Z/aula-04/EVIDENCIA.md) · `deploy.yml` com OIDC | [`AULA_04`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_04_GITHUB_ACTIONS.md) |
| 5 | Corpus CVM | script `pnpm collect` | [`aula-05`](../evidencias/run-2026-11-11T220837Z/aula-05/EVIDENCIA.md) · `packages/corpus` · prompt `aula-1.5-corpus-cvm.md` | [`AULA_05`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_05_CORPUS_CVM.md) |
| 6 | Fundação GCP | gcloud + HITL | [`aula-06`](../evidencias/run-2026-11-11T220837Z/aula-06/EVIDENCIA.md) · **HITL** · prompt `aula-1.6-fundacao-gcp.md` | [`AULA_06`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_06_FUNDACAO_GCP.md) |
| 7 | Docker + Deploy Zero | Docker Compose · Actions | [`aula-07`](../evidencias/run-2026-11-11T220837Z/aula-07/EVIDENCIA.md) · API/web OK; **daemon Docker off** | [`AULA_07`](../../modulo-11-exemplo-1-setup-deploy-inicial/docs/exemplo_aula/AULA_07_WALKING_SKELETON.md) |

### Unidade 2 — Orquestração cognitiva

| Aula | Ferramenta | Evidência | Prompt oficial | Teoria |
|------|------------|-----------|----------------|--------|
| 8 | pgvector / HNSW / seed | [`aula-08`](../evidencias/run-2026-11-11T220837Z/aula-08/EVIDENCIA.md) | `aula-2.1-pgvector-hnsw-e-seed.md` | [`AULA_08`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_08_PGVECTOR_SEED.md) |
| 9 | LangGraph retrieve/grade | [`aula-09`](../evidencias/run-2026-11-11T220837Z/aula-09/EVIDENCIA.md) | `aula-2.2-nos-retrieve-e-grade.md` | [`AULA_09`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_09_RETRIEVE_GRADE.md) |
| 10 | Serper | [`aula-10`](../evidencias/run-2026-11-11T220837Z/aula-10/EVIDENCIA.md) | `aula-2.3-serper.md` | [`AULA_10`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_10_SERPER.md) |
| 11 | Fallback + upsert | [`aula-11`](../evidencias/run-2026-11-11T220837Z/aula-11/EVIDENCIA.md) | `aula-2.4-fallback-busca-web.md` | [`AULA_11`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_11_FALLBACK_UPSERT.md) |
| 12 | Grafo + guard | [`aula-12`](../evidencias/run-2026-11-11T220837Z/aula-12/EVIDENCIA.md) | `aula-2.5-grafo-real.md` | [`AULA_12`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_12_GRAFO_GUARD.md) |
| 13 | Answer + SSE + guardrail | [`aula-13`](../evidencias/run-2026-11-11T220837Z/aula-13/EVIDENCIA.md) | `aula-2.6-no-answer-guardrail-e-sse.md` | [`AULA_13`](../../modulo-11-exemplo-2-orquestracao-cognitiva/docs/exemplo_aula/AULA_13_ANSWER_SSE.md) |

Pacote-chave: `packages/agent`.

### Unidade 3 — Qualidade, resiliência e MCP

| Aula | Ferramenta | Evidência | Prompt | Teoria |
|------|------------|-----------|--------|--------|
| 14 | Testes / modo demo | [`aula-14`](../evidencias/run-2026-11-11T220837Z/aula-14/EVIDENCIA.md) | `aula-3.1-testando-o-grafo-sem-rede.md` | [`AULA_14`](../../modulo-11-exemplo-3-qualidade-resiliencia-mcp/docs/exemplo_aula/AULA_14_TESTES_SEM_REDE.md) |
| 15 | Circuit breaker | [`aula-15`](../evidencias/run-2026-11-11T220837Z/aula-15/EVIDENCIA.md) | `aula-3.2-circuit-breaker-e-degradacao.md` | [`AULA_15`](../../modulo-11-exemplo-3-qualidade-resiliencia-mcp/docs/exemplo_aula/AULA_15_CIRCUIT_BREAKER.md) |
| 16 | Erros padronizados | [`aula-16`](../evidencias/run-2026-11-11T220837Z/aula-16/EVIDENCIA.md) | `aula-3.3-problem-json.md` | [`AULA_16`](../../modulo-11-exemplo-3-qualidade-resiliencia-mcp/docs/exemplo_aula/AULA_16_ERROS_PADRONIZADOS.md) |
| 17 | **Servidor MCP** | [`aula-17`](../evidencias/run-2026-11-11T220837Z/aula-17/EVIDENCIA.md) · pacote `mcp-server` | `aula-3.4-servidor-mcp.md` | [`AULA_17`](../../modulo-11-exemplo-3-qualidade-resiliencia-mcp/docs/exemplo_aula/AULA_17_SERVIDOR_MCP.md) |

### Unidade 4 — Frontend

| Aula | Ferramenta | Evidência | Prompt | Teoria |
|------|------------|-----------|--------|--------|
| 18 | Claude Design / skill frontend | [`aula-18`](../evidencias/run-2026-11-11T220837Z/aula-18/EVIDENCIA.md) | `aula-4.1-…` | [`AULA_18`](../../modulo-11-exemplo-4-frontend/docs/exemplo_aula/AULA_18_PROTOTIPO_DESIGN.md) |
| 19 | Chat + streaming | [`aula-19`](../evidencias/run-2026-11-11T220837Z/aula-19/EVIDENCIA.md) · **Playwright MCP** | `aula-4.2-…` | [`AULA_19`](../../modulo-11-exemplo-4-frontend/docs/exemplo_aula/AULA_19_CHAT_STREAMING.md) |
| 20 | Painel do grafo | [`aula-20`](../evidencias/run-2026-11-11T220837Z/aula-20/EVIDENCIA.md) | `aula-4.3-…` | [`AULA_20`](../../modulo-11-exemplo-4-frontend/docs/exemplo_aula/AULA_20_PAINEL_GRAFO.md) |
| 21 | Disclaimer + E2E | [`aula-21`](../evidencias/run-2026-11-11T220837Z/aula-21/EVIDENCIA.md) · Playwright Test | `aula-4.4-…` | [`AULA_21`](../../modulo-11-exemplo-4-frontend/docs/exemplo_aula/AULA_21_DISCLAIMER_E2E.md) |

### Unidade 5 — Observabilidade

| Aula | Ferramenta | Evidência | Prompt | Teoria |
|------|------------|-----------|--------|--------|
| 22 | Langfuse | [`aula-22`](../evidencias/run-2026-11-11T220837Z/aula-22/EVIDENCIA.md) · `langfuse.ts` · **langfuse-mcp** | `aula-5.1-langfuse.md` | [`AULA_22`](../../modulo-11-exemplo-5-observabilidade-producao/docs/exemplo_aula/AULA_22_LANGFUSE.md) |
| 23 | Metrics / budget / rate limit | [`aula-23`](../evidencias/run-2026-11-11T220837Z/aula-23/EVIDENCIA.md) | `aula-5.2-…` | [`AULA_23`](../../modulo-11-exemplo-5-observabilidade-producao/docs/exemplo_aula/AULA_23_METRICAS_BUDGET.md) |
| 24 | README Mermaid + teardown | [`aula-24`](../evidencias/run-2026-11-11T220837Z/aula-24/EVIDENCIA.md) · teardown **HITL** | `aula-5.3-readme.md` | [`AULA_24`](../../modulo-11-exemplo-5-observabilidade-producao/docs/exemplo_aula/AULA_24_README_TEARDOWN.md) |

---

## 4. Ferramentas × canal de automação (resultado prático)

| Ferramenta | Canal | Nesta run |
|------------|-------|-----------|
| GitHub | MCP `github-cli` + `git clone` | ✅ clones seed + full |
| CLAUDE.md / skills | arquivos / Cursor skills | ✅ inventariadas |
| GitHub Actions / WIF | leitura `deploy.yml` | ✅ OIDC confirmado; IAM = HITL |
| Docker / pgvector | Compose | ⚠️ CLI ok, **daemon off** |
| Corpus CVM | `packages/corpus` + prompt 1.5 | ✅ estrutura; collect pendente |
| LangGraph agent | `packages/agent` | ✅ artefatos no full |
| Serper | prompt 2.3 + env | ⚠️ key HITL |
| MCP server Capstone | `packages/mcp-server` | ✅ pacote presente |
| Playwright | config + E2E no full | ✅ artefato; browser run pendente |
| Langfuse | `langfuse.ts` + MCP | ✅ código; cloud key HITL |
| GCP Cloud SQL / Run | gcloud / Console | ❌ HITL (aula 6) |
| Template MCP local | [`mcp.capstone.example.json`](../config/mcp.capstone.example.json) | ✅ |

---

## 5. Como reproduzir / completar o que ficou parcial

```powershell
# 1) Subir Docker Desktop, depois:
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\ai-researcher-seed
docker compose up -d postgres
docker compose exec -T postgres psql -U postgres -d ai_researcher -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2) Instalar deps (Windows: pnpm.cmd)
pnpm.cmd install --frozen-lockfile
pnpm.cmd test

# 3) Reexecutar evidências
cd ..\..\..
python modulo-11-exemplo-pratico-automacao-capstone\scripts\run_evidencias_capstone.py

# 4) MCP no Cursor — mesclar config/mcp.capstone.example.json
# 5) Playwright MCP — validar chat em modo demo (após pnpm dev)
# 6) GCP / Serper / Langfuse keys — só com HITL
```

---

## 6. Conclusão

O exemplo prático **executou o mapeamento ponta a ponta das 24 aulas**: cada etapa tem evidência JSON/MD, ligação com o prompt da vídeo-aula e com o material teórico U1–U5, e classificação clara do que já rodou localmente versus o que depende de Docker ligado, secrets ou aceite humano (fundação GCP / teardown).

Próximo incremento natural: com Docker Desktop ativo + `pnpm.cmd install`, regenerar a run para promover aulas 7–8 e a suíte de testes a `executado`, e anexar trace Langfuse quando houver chave.
