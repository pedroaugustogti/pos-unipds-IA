# Revisão MCP Angular — Pix Agendado

Revisão do app `app/` alinhada ao guia **`get_best_practices`** do [Angular CLI MCP](https://angular.dev/ai/mcp) e aos **prompts UNIPDS** em `../prompts/`.

## Arquitetura (pós-refatoração prompts)

```
app/src/app/
├── app.ts / app.html / app.css     # shell + menu lateral colapsável (correcao_css.md)
├── app.routes.ts                   # /pix, /extrato, /agendamentos
├── core/                           # state, mock API, messages (figma-to-code.md)
├── components/error-modal/         # a11y-component-generator.md
├── pix-transfer/                   # wizard + integração comprovante (adicionar-fluxo-comprovante.txt)
├── features/receipt/               # google-stitch.md / stitch-code-refactor.md (@Input signals)
├── pix-history/                    # figma-to-angular.md (@for extrato)
└── pix-schedules/                  # lista/cancelamento agendamentos
```

## Checklist prompts

| Prompt / Briefing | Aplicado |
|-------------------|----------|
| `briefing/branding-briefing.txt` | Tokens em `styles.css` (cores, fontes, espaçamentos 4px) |
| `briefing/figma-specs.txt` | `PixHistoryComponent` — padding 16×24, tipografia, ícones 24px |
| `briefing/google-stitch.txt` | `PixReceiptComponent` — card desktop, check, valor, CTA único |
| `design-tokens-generator.md` | Tokens semânticos em `src/styles.css` |
| `figma-to-angular.md` | `PixHistoryComponent` com `@for` + material symbols |
| `stitch-code-refactor.md` | `PixReceiptComponent` com tokens, sem hex no CSS |
| `adicionar-fluxo-comprovante.txt` | `@if` alterna wizard ↔ comprovante em `pix-transfer` |
| `criacao-menu-extrato.txt` | Rota `/extrato` + link no menu |
| `correcao_css.md` | Menu hambúrguer mobile + `--color-text-light` no recibo |
| `a11y-component-generator.md` | `ErrorModal` com ARIA, ESC e foco |
| `figma-to-code.md` | Regras Pix Agendado (limite, MFA, idempotency) |

## Build

```bash
cd app
npm run build
npm test
```
