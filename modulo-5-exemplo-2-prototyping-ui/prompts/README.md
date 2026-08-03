# Prompts — Módulo 5 Exemplo 2

Orientações de prompting para prototipagem UI com Angular, alinhadas ao repositório oficial UNIPDS:

[modulo-02/pix-app/prompts](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app/prompts)

## Prompts oficiais UNIPDS (pix-app)

| Arquivo | Uso |
|---------|-----|
| [`figma-to-angular.md`](figma-to-angular.md) | System prompt: Figma → `PixHistoryComponent` (extrato) |
| [`componente-figma.txt`](componente-figma.txt) | Prompt de execução com imagem + `figma-specs.txt` |
| [`design-tokens-generator.md`](design-tokens-generator.md) | Gerar tokens CSS em `:root` |
| [`a11y-component-generator.md`](a11y-component-generator.md) | Componente acessível com WAI-ARIA + tokens |
| [`stitch-code-refactor.md`](stitch-code-refactor.md) | System prompt: Stitch → `PixReceiptComponent` |
| [`google-stitch.md`](google-stitch.md) | System prompt local: Stitch + `modelo/code.html` |
| [`refatoracao-stich.txt`](refatoracao-stich.txt) | Prompt de execução com `stitch-bruto.html/css` |
| [`adicionar-fluxo-comprovante.txt`](adicionar-fluxo-comprovante.txt) | Integrar comprovante na tela de transferência |
| [`criacao-menu-extrato.txt`](criacao-menu-extrato.txt) | Rota `/extrato` + link no menu lateral |
| [`correcao_css.md`](correcao_css.md) | Responsividade mobile + contraste do recibo |

## Prompts locais (adaptação Exemplo 1 → 2)

| Arquivo | Uso |
|---------|-----|
| [`figma-to-code.md`](figma-to-code.md) | Scaffold completo do **Pix Agendado** a partir do refinement do Ex. 1 |
| [`firebase-studio-prototyper.md`](firebase-studio-prototyper.md) | Trilha alternativa Firebase Studio (cloud UNIPDS) |

## Como usar no Cursor

1. Anexe o system prompt (`.md`) como contexto fixo ou cole no início do chat.
2. Use o prompt de execução (`.txt`) na mensagem seguinte, com `@` nos arquivos referenciados.
3. Com **Angular MCP** ativo, peça antes: *"consulte get_best_practices antes de gerar o componente"*.

## Mapeamento com o app local

O app em `app/` implementa o fluxo **Pix Agendado** (Ex. 1). Os prompts UNIPDS de extrato/comprovante/Stitch são complementares — use-os para estender o protótipo (ex.: tela de extrato, refino visual do recibo).

| Prompt UNIPDS | Equivalente local |
|---------------|-------------------|
| `PixHistoryComponent` | `pix-history/` → `/extrato` |
| `PixReceiptComponent` | `features/receipt/` → `pix-transfer` + `/comprovante` |
| `PixTransferComponent` | `pix-transfer/` (wizard único) |
