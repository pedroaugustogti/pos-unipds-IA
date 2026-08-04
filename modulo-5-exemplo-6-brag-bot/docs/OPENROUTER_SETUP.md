# OpenRouter — Setup do BragBot (recomendado no curso)

Reutilize a mesma `OPENROUTER_API_KEY` dos módulos anteriores (Ex. 3–4).

## Por que OpenRouter?

| | OpenRouter | Google AI Studio |
|---|------------|------------------|
| Chave | Já usada no curso POS | Nova conta/projeto |
| Modelo | `google/gemini-2.5-flash` via proxy | Gemini direto |
| Custo | Créditos OpenRouter / modelos free | Quota Google AI |
| Genkit | Plugin `@genkit-ai/compat-oai` | Plugin `@genkit-ai/google-genai` |

O BragBot detecta automaticamente: se `OPENROUTER_API_KEY` estiver definida, usa OpenRouter.

## Setup rápido

```powershell
cd modulo-5-exemplo-6-brag-bot/app
cp .env.example .env
```

Edite `.env`:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemini-2.5-flash
```

### Copiar chave de outro exemplo

```powershell
cd modulo-5-exemplo-6-brag-bot/app
.\scripts\copy-openrouter-key.ps1
```

Ou manualmente:

## Validar

```bash
npm run build
npm run serve:ssr:brag-bot
```

```powershell
$body = @{ definition = "Otimizei a API com Redis" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:4000/api/brag -Method POST -Body $body -ContentType "application/json"
```

## Modelos sugeridos

| `OPENROUTER_MODEL` | Uso |
|--------------------|-----|
| `google/gemini-2.5-flash` | Padrão — alinhado ao UNIPDS |
| `openrouter/free` | Sem custo (qualidade variável) |
| `google/gemini-2.0-flash-001` | Alternativa Gemini |

Lista completa: [openrouter.ai/models](https://openrouter.ai/models)

## Implementação técnica

Arquivo `src/llm-config.ts` usa o plugin [OpenAI-compatible do Genkit](https://genkit.dev/docs/integrations/openai-compatible/):

```typescript
openAICompatible({
  name: 'openrouter',
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.ai/api/v1',
})
```

Modelo referenciado como `openrouter/google/gemini-2.5-flash`.

## Voltar ao Google AI Studio

```env
LLM_PROVIDER=google
GEMINI_API_KEY=AIza...
```

Ver também [`AI_STUDIO_SETUP.md`](AI_STUDIO_SETUP.md).
