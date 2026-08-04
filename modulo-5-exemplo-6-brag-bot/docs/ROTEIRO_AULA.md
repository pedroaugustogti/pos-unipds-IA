# Roteiro de Aula — BragBot + Genkit (~2h)

**Referência UNIPDS:** [modulo-05/brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)

## Contexto

| Anterior | Esta aula | Encerramento |
|----------|-----------|--------------|
| Ex. 5 — Playwright MCP ✅ | **Ex. 6 — BragBot + Genkit** | Módulo 5 completo |

## Objetivos de aprendizagem

Ao final, o aluno será capaz de:

1. Configurar Genkit + Google AI no Angular SSR
2. Definir flows tipados com Zod e structured output JSON
3. Expor flows como endpoints REST no `server.ts`
4. Consumir IA no frontend com services e signals
5. Debugar prompts no Genkit Developer UI

---

## Roteiro

### 1. Recapitulação do módulo (10 min)

- Ex. 1–2: specs → UI (discovery, prototyping)
- Ex. 3: OpenSpec spec-driven
- Ex. 4–5: testes E2E (Cypress, Playwright MCP)
- Pergunta: **onde a IA entra no produto final**, não só nos testes?

### 2. Introdução Brag Documents (15 min)

- O que é um Brag Document (IDP, promoções, retrospectivas)
- Demo do app: rascunho informal → documento estruturado
- Mostrar [`FLUXO_GENKIT.md`](FLUXO_GENKIT.md)

### 3. Lab 1 — Setup e primeira geração (25 min)

```bash
cd modulo-5-exemplo-6-brag-bot/app
npm install
cp .env.example .env
# GOOGLE_GENAI_API_KEY=...
npm run build
node dist/brag-bot/server/server.mjs
```

Exercício: gerar 3 Brag Documents com conquistas diferentes e comparar qualidade.

### 4. Lab 2 — Explorar `flows.ts` (25 min)

Arquivo: `app/src/flows.ts`

- `BragInputSchema` / `BragSchema` — contrato de entrada e saída
- Prompt com persona "Senior Career Consultant"
- `output: { format: 'json', schema: BragSchema }`

Exercício: identificar as 4 regras do prompt e prever o efeito de cada uma.

### 5. Lab 3 — Genkit UI (20 min)

```bash
npm run genkit:ui
```

- Executar `bragGeneratorFlow` com input de teste
- Variar `temperature` (0.2 vs 0.8)
- Documentar diferença na criatividade vs precisão das métricas

### 6. Lab 4 — Evoluir o prompt (20 min)

Prompt guia: [`prompts/genkit-brag-document.md`](../prompts/genkit-brag-document.md)

Exercício: adicionar regra para **nunca inventar métricas numéricas** quando o usuário não fornecer dados — validar no Genkit UI.

### 7. Encerramento — Módulo 5 (5 min)

- Mapa mental: UI/UX + specs + testes + **IA no produto**
- Próximos passos: Firebase AI Logic, deploy, observabilidade de flows

---

## Materiais de apoio

| Recurso | Link |
|---------|------|
| Genkit docs | https://firebase.google.com/docs/genkit |
| Angular AI / MCP | https://angular.dev/ai |
| Google AI Studio | https://aistudio.google.com/apikey |
