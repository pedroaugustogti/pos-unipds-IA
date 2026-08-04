# Agents CLI — Refatoração com IA no Terminal

Este diretório é o **Módulo 5 — Exemplo 3** (`modulo-5-exemplo-3-agents-cli`) — adaptação local da atividade da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [modulo-03](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03)

## Objetivo

Usar **agentes CLI** (Gemini CLI ou equivalente) para **consolidar** o protótipo Angular do Exemplo 2: remover código morto, aplicar refatorações guiadas por prompt e aumentar cobertura de testes — com diff mínimo e evidências de build.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| [Exemplo 2 concluído](../modulo-5-exemplo-2-prototyping-ui/) | `pix-app` buildando (`npm run build`) |
| Node.js 22+ | Angular CLI 21 |
| Nx CLI | `npm install -g nx@latest` |
| Gemini CLI (ou Cursor CLI) | Agente no terminal conforme UNIPDS modulo-03 |
| [delivery-agent](../../delivery-agent/) | Scaffold desta aula (opcional) |

## Estrutura

```
modulo-5-exemplo-3-agents-cli/
├── README.md
├── cfp-platform/                 # workspace Nx (preset apps)
├── prompts/
│   ├── refactor-safe.md          # diff mínimo, sem over-engineering
│   ├── dead-code-cleanup.md      # remover scaffold legado
│   └── test-gap-fixer.md         # testes Vitest para componentes UI
└── docs/
    ├── ROTEIRO_AULA.md           # roteiro ~2h para sala
    ├── EVIDENCIAS_ACEITE.md      # checklist da aula
    └── RELATORIO_DIDATICO.md     # tópicos e comandos (delivery-agent)
```

**App alvo:** `../modulo-5-exemplo-2-prototyping-ui/app/` (não duplicar o projeto).

## Configuração

```bash
npm install -g nx@latest
nx --version

cd modulo-5-exemplo-3-agents-cli
npx create-nx-workspace@latest cfp-platform --preset=apps --nxCloud=skip
```

## Como executar

```bash
cd ../modulo-5-exemplo-2-prototyping-ui/app
npm run build
npm test -- --watch=false
```

### Laboratório 1 — Código morto

Anexe `@prompts/dead-code-cleanup.md` no agente CLI e execute no diretório `app/`.

### Laboratório 2 — Refatoração CSS

Anexe `@../modulo-5-exemplo-2-prototyping-ui/prompts/correcao_css.md` + `@prompts/refactor-safe.md`.

### Laboratório 3 — Testes do comprovante

Anexe `@prompts/test-gap-fixer.md` e gere testes para `PixReceiptComponent`.

## Critérios de sucesso

- [ ] Pasta criada no padrão `modulo-5-exemplo-3-*`
- [ ] README local com objetivo, passo a passo e critérios de sucesso
- [ ] Gemini CLI (ou equivalente) executado no `pix-app`
- [ ] Código morto removido ou documentado
- [ ] `npm run build` e `npm test` verdes após refatorações
- [ ] ≥ 3 testes novos em componente de UI (extrato ou comprovante)
- [ ] ≥ 1 refatoração feita somente via CLI (evidência no terminal)
- [ ] `docs/EVIDENCIAS_ACEITE.md` preenchido
- [ ] README raiz do `pos-unipds-IA` atualizado

## Exemplo anterior

[`modulo-5-exemplo-2-prototyping-ui`](../modulo-5-exemplo-2-prototyping-ui/) ✅

## Próxima aula

**Exemplo 4:** Automação MCP — testes E2E e depuração ([modulo-04 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04))
