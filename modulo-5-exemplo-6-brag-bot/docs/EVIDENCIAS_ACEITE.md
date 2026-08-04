# Evidências de Aceite — Exemplo 6 (BragBot + Genkit)

Validação executada em **2026-08-04**.

## Stack validada

| Tecnologia | Artefato |
|------------|----------|
| **Genkit Flows** | `app/src/flows.ts` → `bragGeneratorFlow` |
| **Zod** | `BragInputSchema`, `BragSchema` |
| **OpenRouter** | `app/src/llm-config.ts` (`LLM_PROVIDER=openrouter`) |
| **Express API** | `POST /api/brag` em `app/src/server.ts` (Micro-BFF) |
| **HttpClient** | `provideHttpClient(withFetch())` em `app.config.ts` |
| **BragService** | `generateBrag()` — POST real, signals `loading`/`brags` |
| **Genkit UI** | `npm run genkit:ui` → http://localhost:4003 |

## Comandos executados

```bash
cd app
npm install
cp .env.example .env
.\scripts\copy-openrouter-key.ps1   # ou configurar GEMINI_API_KEY

npm run build
npm run serve:ssr:brag-bot          # http://localhost:4000
npm run genkit:ui                   # http://localhost:4003
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| `BragInputSchema` / `BragSchema` (Zod) | ✅ | `flows.ts` |
| `bragGeneratorFlow` definido | ✅ | `ai.defineFlow(...)` |
| Micro-BFF `express.json()` + `POST /api/brag` | ✅ | `server.ts` — antes do catch-all |
| `provideHttpClient(withFetch())` | ✅ | `app.config.ts` |
| `BragService.generateBrag()` sem mock | ✅ | POST `/api/brag` + signals |
| `POST /api/brag` retorna JSON | ✅ | `title`, `businessImpact`, `metrics` |
| Dashboard — destilar conquista | ✅ | UI `/` |
| Detail — `/detail/:id` | ✅ | contexto, impacto, métricas |
| Genkit Developer UI | ✅ | `genkit:ui` + `--non-interactive` |
| OpenRouter integrado | ✅ | `llm-config.ts` + `@genkit-ai/compat-oai` |
| `.env` não commitado | ✅ | `.gitignore` |

## Registro de execução

| Lab | Comando | Resultado |
|-----|---------|-----------|
| Setup | `copy-openrouter-key.ps1` | ✅ OPENROUTER_API_KEY |
| Build | `npm run build` | ✅ SSR bundle |
| API | `POST /api/brag` | ✅ JSON estruturado |
| Genkit UI | `npm run genkit:ui` | ✅ http://localhost:4003 |
| Prompt lab | `genkit-brag-document.md` | ✅ Documentado |

## Exemplo de resposta da API

```json
{
  "title": "Otimização de API com Redis",
  "context": "...",
  "businessImpact": "...",
  "metrics": ["Redução da latência de 800ms para 120ms"],
  "technologiesUsed": ["Redis"]
}
```
