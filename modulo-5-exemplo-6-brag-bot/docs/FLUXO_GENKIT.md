# Fluxo Genkit — BragBot

Arquitetura da integração IA no Exemplo 6.

## Visão geral

```mermaid
sequenceDiagram
    participant U as Usuário
    participant D as Dashboard (Angular)
    participant S as BragService
    participant API as Express /api/brag
    participant F as bragGeneratorFlow
    participant G as Gemini 2.5 Flash

    U->>D: Rascunho informal
    D->>S: generateBrag(definition)
    S->>API: POST { definition }
    API->>F: bragGeneratorFlow({ definition })
    F->>G: prompt + BragSchema (JSON)
    G-->>F: title, context, metrics...
    F-->>API: BragDocument + id
    API-->>S: JSON
    S-->>D: signal brags atualizado
    D-->>U: Card + link /detail/:id
```

## Camadas

| Camada | Arquivo | Responsabilidade |
|--------|---------|------------------|
| **Flow** | `app/src/flows.ts` | Define `BragInputSchema`, `BragSchema`, prompt e `bragGeneratorFlow` |
| **API** | `app/src/server.ts` | `POST /api/brag` — chama o flow e retorna JSON |
| **Service** | `app/src/app/services/brag.service.ts` | HTTP client + signals (`brags`, `loading`) |
| **UI** | `dashboard/`, `detail/` | Formulário, lista e visualização |

## Schema de saída (`BragSchema`)

| Campo | Descrição |
|-------|-----------|
| `title` | Ação + resultado de alto nível |
| `context` | Situação / problema original |
| `actionTaken` | Passos técnicos tomados |
| `businessImpact` | Impacto de negócio |
| `metrics` | Dados quantificáveis |
| `technologiesUsed` | Stack inferida ou mencionada |

## Genkit UI

```bash
cd app
npm run genkit:ui
```

Permite executar `bragGeneratorFlow` isoladamente, ajustar temperatura e inspecionar traces — útil antes de alterar o prompt em produção.

## Diferença vs Ex. 4–5

| Aspecto | Cypress / Playwright (Ex. 4–5) | Genkit (Ex. 6) |
|---------|-------------------------------|----------------|
| Objetivo | Validar UI existente | **Gerar conteúdo** com IA |
| IA no loop | `cy.prompt()` / agentes MCP | Flow tipado + Gemini |
| Artefato | Spec de teste | Brag Document estruturado |

## Referência UNIPDS

[brag-bot no repositório UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)
