# Prototyping UI — Figma to Code

Este diretório é o **Módulo 5 — Exemplo 2** (`modulo-5-exemplo-2-prototyping-ui`) — adaptação local da pós UNIPDS.

Referência UNIPDS: [modulo-02](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02)

## Objetivo

Transformar a especificação refinada do **Exemplo 1** em **protótipo funcional**: via Figma + Firebase Studio (fluxo UNIPDS) ou implementação local no Cursor a partir dos artefatos de refinamento.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| [Exemplo 1 concluído](../modulo-5-exemplo-1-discovery-refinement/) | `edge-cases.md`, `ui-states-checklist.md`, `fluxo-logico.mmd`, `mensagens-ui.json` |
| [Firebase Studio](https://firebase.google.com/docs/studio) | App Prototyping agent (fluxo cloud UNIPDS) |
| Figma + [Builder.io plugin](https://www.builder.io/c/docs/builder-figma-plugin) | Import design → Firebase Studio (opcional) |
| Node.js 22+ | App local em `app/` (fluxo Cursor) |
| Cursor | Geração de código a partir de `prompts/` |

Entrada detalhada: [`docs/ENTRADA_EXEMPLO_1.md`](docs/ENTRADA_EXEMPLO_1.md)

## Estrutura

```
modulo-5-exemplo-2-prototyping-ui/
├── prompts/
│   ├── figma-to-code.md              # Design → componentes React
│   └── firebase-studio-prototyper.md
├── docs/
│   ├── ENTRADA_EXEMPLO_1.md          # Links para artefatos do Ex. 1
│   └── PIPELINE.md
└── app/                              # Implementação (a gerar)
    └── README.md
```

## Como executar

### Trilha A — UNIPDS (Firebase Studio + Figma)

1. Abra o design Pix Agendado no Figma (ou use wireframe da aula)
2. Exporte com **Builder.io → Classic Export → Firebase Studio**
3. No Firebase Studio, use `prompts/firebase-studio-prototyper.md` como guia de prompts
4. Valide estados de UI contra `ui-states-checklist.md` do Exemplo 1
5. Publique protótipo e compartilhe URL de preview

### Trilha B — Cursor (código local)

1. Cole em System Instructions: `prompts/figma-to-code.md`
2. Anexe como contexto os arquivos listados em `docs/ENTRADA_EXEMPLO_1.md`
3. Gere o app em `app/` (React + Vite recomendado)
4. Implemente estados de erro com `mensagens-ui.json`
5. Valide fluxo contra `fluxo-logico.mmd`

```bash
cd app
npm install
npm run dev
```

## Critérios de sucesso

- [ ] Pasta criada no padrão `modulo-5-exemplo-2-*`
- [ ] README local com objetivo, passo a passo e critérios de sucesso
- [ ] Entrada do Exemplo 1 documentada (`ENTRADA_EXEMPLO_1.md`)
- [ ] Protótipo ou app cobre o **caminho feliz** do Pix Agendado
- [ ] Pelo menos 3 **unhappy paths** da checklist implementados
- [ ] Mensagens de UI alinhadas a `mensagens-ui.json`
- [ ] README raiz do `pos-unipds-IA` atualizado

## Fluxo didático

```
Ex. 1 (refinamento)  →  Ex. 2 (protótipo)  →  Ex. 3+ (CLI, MCP, integração)
     specs/json/mmd        app / Firebase Studio
```

Pipeline completo: [`docs/PIPELINE.md`](docs/PIPELINE.md)

## Exemplo anterior

[`modulo-5-exemplo-1-discovery-refinement`](../modulo-5-exemplo-1-discovery-refinement/) — Discovery e Refinamento AI-First ✅
