# Exemplo real — Capstone · Qualidade, resiliência e MCP (U3)

Etapa Capstone das **aulas 14–17**: testes sem rede, circuit breaker, erros padronizados, MCP server, guardrail e degradação.

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/) · Evidências: `03-u3-resiliencia-guardrails/`  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| U1–U2 | Repo Capstone + agent com grafo e Serper |
| Env | `DEMO=true` para testes offline; Serper real para degradação em prod |
| Pacotes | `packages/agent`, `packages/mcp-server`, `apps/api` |
| Opcional | Cursor MCP via [`setup_mcp_skills.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/setup_mcp_skills.ps1) |

---

## Ferramentas e artefatos

| Peça | Onde |
|------|------|
| Fakes / demo | [`llm-demo.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/llm-demo.ts), [`retrieve-demo.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/retrieve-demo.ts) |
| Circuit breaker | [`resilient-search-provider.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/resilient-search-provider.ts) |
| Serper | [`serper.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/serper.ts) |
| MCP Capstone | `packages/mcp-server` |
| Config Cursor | [`mcp.capstone.example.json`](../../../modulo-11-exemplo-pratico-automacao-capstone/config/mcp.capstone.example.json) + [`setup_mcp_skills.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/setup_mcp_skills.ps1) |
| Aceite | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

---

## Scripts e comandos

| Script | Função |
|--------|--------|
| [`setup_mcp_skills.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/setup_mcp_skills.ps1) | Mescla MCP/skills no Cursor |
| [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) | Itens 5, 7, 10 (degradação, 429, guardrail) |
| [`load-test.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/load-test.ts) | Carga / rate limit (`pnpm load:test`) |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher

$env:DEMO='true'
pnpm.cmd --filter @hero/agent test
pnpm.cmd test

cd ..\..
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_mcp_skills.ps1

cd workspace\capstone-project-ai-researcher
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

---

## Ações

1. Rodar suíte do agent com `DEMO=true`.
2. Revisar [`resilient-search-provider.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/resilient-search-provider.ts).
3. Simular falha Serper → chat **200** (degradação).
4. Wire MCP com [`setup_mcp_skills.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/setup_mcp_skills.ps1).
5. Validar guardrail na UI (recomendação → recusa).
6. Confirmar 429 com [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) ou [`load-test.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/load-test.ts).

---

## Validação de funcionamento

| Check | Como |
|-------|------|
| Testes | `pnpm --filter @hero/agent test` |
| Degradação | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) item **5** |
| Rate limit + alerta | item **7** |
| Guardrail | item **10** + `02-guardrail-recusa.png` |

### Critérios

- [x] Testes offline  
- [x] Degradação graciosa  
- [x] Guardrail + 429 em prod  
- [x] Pacote MCP no monorepo  
