# Playwright no Capstone

Dois papéis — não misturar.

## 1. Playwright MCP (exploração pelo agente)

Pacote: `@playwright/mcp`

**Quando usar**

- Validar `/health` após deploy zero (aula 7)
- Percorrer chat + painel do grafo (aulas 19–20)
- Assistir Console GCP / Langfuse UI (leitura; HITL em ações caras)

**Exemplo de intenção para o agente**

```
Abra http://localhost:4200 (ou a URL do Firebase Hosting).
Confirme o disclaimer visível.
Envie a pergunta demo do modo demo.
Espere o painel mostrar retrieve → grade → answer.
Capture o texto da citação (CVM ou web).
```

## 2. Playwright Test + MCP test server (CI / regressão)

Padrão do monorepo: `playwright run-test-mcp-server --config …` (ver `playwright-test-cfp` no `.cursor/mcp.json`).

**Quando usar**

- Aula 21: E2E no CI com **modo demo** (sem Serper/Vertex reais)
- Smoke de disclaimer + streaming fake

**Regras**

| Regra | Motivo |
|-------|--------|
| Modo demo no CI | Custo e flaky |
| Disclaimer sem botão fechar | Assert sempre presente |
| Não logar tokens SSE completos | Ruído / PII |

## 3. O que Playwright **não** substitui

- Provisionar Cloud SQL / WIF (use gcloud + HITL)
- Assinar faturamento GCP
- Garantir “não recomenda investimento” (isso é **código** + teste unitário do guardrail)

## Setup rápido

```bash
# MCP exploratório
npx -y @playwright/mcp@latest

# No clone do Capstone (ajuste o path)
cd $CAPSTONE_ROOT
npx playwright install chromium
npx playwright test --config apps/web/playwright.config.ts
```
