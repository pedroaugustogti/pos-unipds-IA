# Google AI Studio — Setup do BragBot

Projeto local: `modulo-5-exemplo-6-brag-bot/app`

## 1. Setup automatizado (recomendado)

```powershell
cd modulo-5-exemplo-6-brag-bot/app
.\scripts\setup-ai-studio.ps1
```

O script:
1. Abre [AI Studio Projects](https://aistudio.google.com/projects) para você criar o projeto
2. Abre [API Keys](https://aistudio.google.com/apikey) para gerar a chave
3. Salva `GEMINI_API_KEY` no `.env`
4. Executa build + teste em `POST /api/brag`

> **Limitação:** a criação do projeto no AI Studio exige login Google no navegador — não há API pública para automatizar sem credenciais OAuth/`gcloud`.

### Com chave já em mãos

```powershell
.\scripts\setup-ai-studio.ps1 -ApiKey "AIza..."
```

---

## 2. Setup manual

### Criar projeto no AI Studio

1. Acesse [Google AI Studio — Projects](https://aistudio.google.com/projects) (login Google necessário)
2. Clique em **Create project** (ou **New project**)
3. Nome sugerido: **`brag-bot-unipds`**
4. Anote o **Project ID** exibido no painel

## 2. Gerar API Key

1. Abra [Google AI Studio — API Keys](https://aistudio.google.com/apikey)
2. Selecione o projeto **`brag-bot-unipds`**
3. Clique em **Create API key**
4. Copie a chave (formato `AIza...`)

> A chave fica vinculada ao projeto. Não commite no Git.

## 3. Configurar `.env` local

```bash
cd modulo-5-exemplo-6-brag-bot/app
cp .env.example .env
```

Edite `.env`:

```env
GEMINI_API_KEY=AIza...sua-chave...
PORT=4000
```

> O Genkit lê `GEMINI_API_KEY` ou `GOOGLE_API_KEY` ([documentação](https://genkit.dev/docs/plugins/google-genai/)).

## 4. Validar

```bash
npm run build
node dist/brag-bot/server/server.mjs
```

Em outro terminal:

```powershell
curl.exe -X POST http://localhost:4000/api/brag `
  -H "Content-Type: application/json" `
  -d "{\"definition\":\"Otimizei a API com Redis e reduzi latencia de 800ms para 120ms\"}"
```

Resposta esperada: JSON com `title`, `context`, `businessImpact`, `metrics`.

## 5. Genkit Developer UI (opcional)

```bash
npm run genkit:ui
```

Inspecione o flow `bragGeneratorFlow` e teste inputs sem subir o Angular.

## Modelo usado

O flow em `src/flows.ts` usa **`gemini-2.5-flash`** via `@genkit-ai/google-genai`.

## Troubleshooting

| Erro | Causa provável | Solução |
|------|----------------|---------|
| `API key not valid` | Chave errada ou projeto sem billing habilitado | Recrie a key no projeto correto |
| `Failed to generate brag` | Key ausente no `.env` | Reinicie o servidor após editar `.env` |
| `403` / quota | Limite free tier | Aguarde ou habilite billing no Google Cloud |

## Referência UNIPDS

[brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)
