# Discovery e Refinamento AI-First

Este diretório é o **Módulo 5 — Exemplo 1** (`modulo-5-exemplo-1-discovery-refinement`) — adaptação local da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [modulo-01](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-01)

## Objetivo

Usar IA para **refinar requisitos ambíguos** em especificações acionáveis: edge cases, fluxo Mermaid, copy de UX e backlog priorizado a partir de feedbacks sanitizados — **antes** de escrever código.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Cursor ou Google AI Studio | Engine LLM (Gemini / OpenRouter) |
| [Mermaid Live Editor](https://mermaid.live) | Validar `fluxo-logico.mmd` |
| Material em `prompts/` e `docs/refinement/` | Base da atividade |

## Estrutura

```
modulo-5-exemplo-1-discovery-refinement/
├── prompts/
│   ├── system-instructions-refinement.md
│   ├── mermaid-flowchart.md
│   ├── data-sanitizer.md
│   ├── tech-leader.md
│   └── ux-writing-system.md
├── docs/refinement/
│   ├── briefing-bruto.md
│   ├── edge-cases.md
│   ├── ui-states-checklist.md
│   ├── fluxo-logico.mmd
│   ├── mensagens-ui.json
│   └── PIPELINE.md
└── data/
    ├── raw-feedbacks.json
    ├── sanitized-feedbacks.json
    └── backlog.json
```

## Como executar (Cursor / LLM)

### Projeto 1 — Refinamento (Pix Agendado)

1. System instructions ← `prompts/system-instructions-refinement.md`
2. User input ← `docs/refinement/briefing-bruto.md`
3. Salvar saída em `edge-cases.md` e `ui-states-checklist.md`
4. Novo turno com `prompts/mermaid-flowchart.md` → `fluxo-logico.mmd`
5. `prompts/ux-writing-system.md` + edge cases → `mensagens-ui.json`

### Projeto 2 — Data discovery

1. `prompts/data-sanitizer.md` + `data/raw-feedbacks.json` → `sanitized-feedbacks.json`
2. `prompts/tech-leader.md` + sanitized → `backlog.json` (**temperature 0**)

Detalhes e rastreabilidade: [`docs/refinement/PIPELINE.md`](docs/refinement/PIPELINE.md)

## Critérios de sucesso (UNIPDS)

- [x] Prompts versionados em `prompts/` (5 arquivos reutilizáveis)
- [x] Rastreabilidade briefing → Mermaid (`PIPELINE.md`)
- [x] Backlog determinístico (`data/backlog.json`, 3 itens priorizados)
- [x] Sanitização LGPD (`data/sanitized-feedbacks.json`, 6 → 3 tickets)
- [x] Artefatos de saída completos em `docs/refinement/`
- [x] README local com objetivo, passo a passo e critérios de sucesso

## Evidências de aceite

| Entregável UNIPDS | Artefato | Status |
|-------------------|----------|--------|
| Versionamento de prompts | `prompts/*.md` | ✅ |
| Rastreabilidade | `PIPELINE.md` + `fluxo-logico.mmd` | ✅ |
| Determinismo (backlog) | `backlog.json` (TKT-101 → 103) | ✅ |
| Edge cases | `edge-cases.md` | ✅ |
| UI states | `ui-states-checklist.md` | ✅ |
| Copy i18n | `mensagens-ui.json` | ✅ |

## Próximo exemplo

**Exemplo 2:** [`modulo-5-exemplo-2-prototyping-ui`](../modulo-5-exemplo-2-prototyping-ui/) — Figma to Code / Firebase Studio, usando os artefatos deste exemplo como especificação de entrada.
