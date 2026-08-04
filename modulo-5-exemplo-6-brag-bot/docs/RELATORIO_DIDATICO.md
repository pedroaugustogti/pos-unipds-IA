# Relatório Didático — Exemplo 6: BragBot + Genkit

> Scaffold via delivery-agent · material base [UNIPDS modulo-05/brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)

## Posição no módulo

O Exemplo 6 **fecha o Módulo 5** com integração de IA **dentro do produto**. Enquanto os Exemplos 4 e 5 usam IA para **automatizar testes** (Cypress `cy.prompt`, Playwright MCP), o BragBot usa **Genkit + Gemini** para **gerar valor direto ao usuário**.

## Competências trabalhadas

| Competência | Como aparece na aula |
|-------------|---------------------|
| IA aplicada à UX | Transformar input informal em documento estruturado e legível |
| Engenharia de prompts | Persona, regras e schema JSON no `flows.ts` |
| Arquitetura full-stack | Flow server-side + API REST + Angular signals |
| Observabilidade de IA | Genkit Developer UI para traces e iteração |
| Boas práticas | `.env.example`, structured output, tipagem Zod |

## Stack técnica

- **Angular 21** (standalone, signals, SSR)
- **Genkit 1.32** + `@genkit-ai/google-genai`
- **Gemini 2.5 Flash** (modelo configurado em `flows.ts`)
- **Express 5** no `server.ts` para `/api/brag`
- **Tailwind CSS 4** na UI

## Ponte pedagógica

```
Ex. 1–2: O QUE construir (specs + UI)
Ex. 3:   COMO evoluir com spec-driven (OpenSpec)
Ex. 4–5: COMO validar (Cypress, Playwright MCP)
Ex. 6:   COMO embutir IA no produto (Genkit flows)
```

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| API key exposta | `.env` no `.gitignore`, `.env.example` no repo |
| Métricas alucinadas | Lab 4 — regra explícita no prompt |
| Dev vs SSR | Documentar `npm start` vs `build + node server.mjs` |
| Custo de API | Usar `gemini-2.5-flash`, limitar demos em sala |

## Entregáveis do aluno

1. App rodando com pelo menos 1 Brag Document gerado
2. Evidências em [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md)
3. (Opcional) Prompt evoluído commitado em `flows.ts`
