# Exemplo real — Capstone · Frontend (U4)

Etapa Capstone das **aulas 18–21**: chat Angular com streaming SSE, citações, painel do grafo, disclaimer e E2E.

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/) · Evidências: `04-u4-frontend/`  
**App:** https://ai-researcher-cap-pedro.web.app  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| U1–U2 | API com `/api/chat` SSE no ar (local ou prod) |
| App | `apps/web` (Angular standalone) |
| Tooling | pnpm, Playwright browsers |
| Deploy | Firebase Hosting no pipeline `deploy.yml` |

---

## Ferramentas

Angular · skill frontend-design · Playwright Test · Browser/Playwright MCP · Firebase Hosting.

Stack local (opcional): [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1)  
Aceite: [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts)

---

## Scripts e comandos

| Script / comando | Arquivo |
|------------------|---------|
| Stack local | [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) |
| `pnpm test:e2e` | app `apps/web` (Playwright) |
| `pnpm capstone:check` | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher

pnpm.cmd install --frozen-lockfile
pnpm.cmd dev
# ou: pnpm.cmd --filter @hero/web start

pnpm.cmd test:e2e
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

---

## Ações

1. Subir API + web (`pnpm dev` ou [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1)).
2. Validar home: marca, disclaimer, input + Enviar.
3. Pergunta B3 → streaming + chips de citação.
4. Painel **Pipeline de raciocínio**.
5. **Nova conversa** limpa estado.
6. Rodar E2E; job `test` verde no Actions ([`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) item 4).

---

## Validação de funcionamento

**Produção:** https://ai-researcher-cap-pedro.web.app/  
Screenshots: `01-home-chat.png`, `02-chat-citacoes.png`.

Script de aceite: [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts).

### Critérios

- [x] Streaming + citações em Hosting  
- [x] Painel do grafo  
- [x] Disclaimer / guardrail visual  
- [x] E2E / CI  
