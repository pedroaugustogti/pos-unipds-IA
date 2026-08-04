# Próxima Aula — Exemplo 6: BragBot + Genkit

> **Scaffold criado:** [`modulo-5-exemplo-6-brag-bot`](../../modulo-5-exemplo-6-brag-bot/) (via delivery-agent)

**Referência UNIPDS:** [modulo-05/brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)

---

## Contexto pedagógico

| Aula anterior | Esta aula | Encerramento |
|---------------|-----------|--------------|
| Ex. 5 — Playwright MCP ✅ | **Ex. 6 — BragBot + Genkit** | Módulo 5 completo |

**Ponte com o Ex. 5:** nos exemplos 4–5 a IA **automatiza testes**; no Ex. 6 a IA **gera valor no produto** — Brag Documents a partir de rascunhos informais.

---

## Objetivos

1. Configurar **Genkit** + **Gemini** no Angular SSR
2. Definir flow tipado (`bragGeneratorFlow`) com schema Zod
3. Expor flow via `POST /api/brag` no Express
4. Consumir no frontend com signals
5. Debugar no **Genkit Developer UI**

---

## Pré-requisitos

- Node.js 22+
- Chave Google AI: [AI Studio](https://aistudio.google.com/apikey)
- Ex. 5 concluído (opcional — contexto de automação E2E)

---

## Início rápido

```bash
cd ../modulo-5-exemplo-6-brag-bot/app
npm install
cp .env.example .env
# GOOGLE_GENAI_API_KEY=...

npm run build
node dist/brag-bot/server/server.mjs
# http://localhost:4000

# Debug do flow (terminal separado)
npm run genkit:ui
```

---

## Materiais

| Documento | Conteúdo |
|-----------|----------|
| [`README.md`](../../modulo-5-exemplo-6-brag-bot/README.md) | Visão geral e critérios |
| [`docs/FLUXO_GENKIT.md`](../../modulo-5-exemplo-6-brag-bot/docs/FLUXO_GENKIT.md) | Arquitetura flow → API → UI |
| [`docs/ROTEIRO_AULA.md`](../../modulo-5-exemplo-6-brag-bot/docs/ROTEIRO_AULA.md) | Roteiro ~2h |
| [`prompts/genkit-brag-document.md`](../../modulo-5-exemplo-6-brag-bot/prompts/genkit-brag-document.md) | Lab evolução de prompt |

---

## Comandos de validação

```bash
cd ../modulo-5-exemplo-6-brag-bot/app
npm run build
curl -X POST http://localhost:4000/api/brag \
  -H "Content-Type: application/json" \
  -d '{"definition":"Otimizei a API com Redis e reduzi latência de 800ms para 120ms"}'
```

Resposta esperada: JSON com `title`, `context`, `businessImpact`, `metrics`, `technologiesUsed`.
