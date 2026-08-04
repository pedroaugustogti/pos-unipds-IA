# BragBot — Genkit + Gemini no Angular

**Módulo 5 — Exemplo 6** (`modulo-5-exemplo-6-brag-bot`)

App **Angular 21** que transforma rascunhos informais de conquistas profissionais em **Brag Documents** estruturados, usando **Firebase Genkit** + **Gemini** (via OpenRouter ou Google AI Studio).

**Referência UNIPDS:** [modulo-05/brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 5 — Playwright MCP ✅ | **Ex. 6 — BragBot + Genkit** ✅ | Encerramento Módulo 5 |

## Objetivos

1. Integrar **Genkit Flows** com schemas **Zod** (`BragInputSchema`, `BragSchema`)
2. Definir `bragGeneratorFlow` com saída JSON estruturada via `ai.generate`
3. Expor o flow via **API Express** (`POST /api/brag`) no `server.ts`
4. Consumir a API no frontend com `BragService` + signals
5. Explorar **Genkit UI** (`npm run genkit:ui`) para debug de prompts e flows
6. Comparar integração de IA **no produto** (esta aula) vs **automação de testes** (Ex. 4–5)

## Estrutura

```
modulo-5-exemplo-6-brag-bot/
├── README.md
├── docs/
│   ├── OPENROUTER_SETUP.md      ← recomendado (chave do curso)
│   ├── AI_STUDIO_SETUP.md       ← alternativa UNIPDS
│   ├── ROTEIRO_AULA.md
│   ├── EVIDENCIAS_ACEITE.md
│   └── RELATORIO_DIDATICO.md
├── prompts/
│   └── genkit-brag-document.md  ← lab: evoluir prompt do flow
└── app/                         ← projeto Angular UNIPDS (brag-bot)
    ├── src/llm-config.ts        ← OpenRouter ou Google AI
    ├── src/flows.ts             ← Genkit Flow + Zod (bragGeneratorFlow)
    ├── src/server.ts            ← Express + POST /api/brag
    └── src/app/
        ├── dashboard/           ← formulário + lista
        ├── detail/              ← visualização do Brag Document
        └── services/brag.service.ts
```

## Pré-requisitos

- Node.js 22+, npm 11+
- **LLM** — uma das opções:
  - **OpenRouter** (recomendado): `OPENROUTER_API_KEY` dos módulos anteriores → [`docs/OPENROUTER_SETUP.md`](docs/OPENROUTER_SETUP.md)
  - **Google AI Studio** (UNIPDS original): `GEMINI_API_KEY` → [`docs/AI_STUDIO_SETUP.md`](docs/AI_STUDIO_SETUP.md)
- Exemplos anteriores do Módulo 5 (opcional)

## Configuração

**Opção A — OpenRouter (curso POS):**

```bash
cd app
npm install
cp .env.example .env
# LLM_PROVIDER=openrouter + OPENROUTER_API_KEY
```

Guia: [`docs/OPENROUTER_SETUP.md`](docs/OPENROUTER_SETUP.md)

**Opção B — Google AI Studio (UNIPDS):**

Guia: [`docs/AI_STUDIO_SETUP.md`](docs/AI_STUDIO_SETUP.md)

Variáveis:

| Variável | Uso |
|----------|-----|
| `LLM_PROVIDER` | `openrouter` (padrão se key existir) ou `google` |
| `OPENROUTER_API_KEY` | Chave OpenRouter (curso POS) |
| `OPENROUTER_MODEL` | Ex.: `google/gemini-2.5-flash` |
| `GEMINI_API_KEY` | Alternativa Google AI Studio |
| `PORT` | Porta SSR (padrão `4000`) |

## Início rápido

### Desenvolvimento (Angular dev server)

```bash
cd app
npm start
# http://localhost:4200
```

> Em dev, o proxy para `/api/brag` depende da configuração do `angular.json`. Para testar o flow completo, use o build SSR abaixo.

### Produção local (SSR + API Genkit)

```bash
cd app
npm run serve:ssr:brag-bot
# ou: npm run start:ssr  (build + serve)
# http://localhost:4000
```

### Genkit Developer UI

```bash
cd app
npm run genkit:ui
# Abre UI para inspecionar bragGeneratorFlow
```

## Lab sugerido

1. Descreva uma conquista informal no dashboard
2. Clique em **Destilar Conquista**
3. Abra o card gerado → página de detalhe com contexto, impacto e métricas
4. Edite o prompt em `src/flows.ts` usando [`prompts/genkit-brag-document.md`](prompts/genkit-brag-document.md)
5. Compare saída antes/depois no Genkit UI

## Critérios de sucesso

Validação executada em **2026-08-04** — ver [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md).

- [x] Base UNIPDS `brag-bot` em `app/`
- [x] **Genkit Flow** `bragGeneratorFlow` com **Zod** (`BragInputSchema`, `BragSchema`)
- [x] `llm-config.ts` — OpenRouter ou Google AI
- [x] `POST /api/brag` retorna JSON estruturado (validado)
- [x] Dashboard gera e lista Brag Documents
- [x] Página `/detail/:id` exibe contexto, impacto e métricas
- [x] Genkit UI (`npm run genkit:ui`) executa o flow
- [x] README, roteiro e evidências de aceite completos

## Anterior

[`modulo-5-exemplo-5-playwright-mcp`](../modulo-5-exemplo-5-playwright-mcp/)
