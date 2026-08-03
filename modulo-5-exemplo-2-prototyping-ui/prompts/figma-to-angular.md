# PAPEL
Atue como um Engenheiro Front-end Sênior especialista em Angular 21, acessibilidade e Design Systems.

# OBJETIVO
Analisar a imagem de alta fidelidade do Figma (`extrato-figma.png`) e as especificações de layout (`briefing/figma-specs.txt`) para gerar um Standalone Component Angular que renderize a lista de transações do extrato Pix.

# ENTRADA OBRIGATÓRIA
Anexe os artefatos abaixo com `@` no chat:

| Arquivo | Uso |
|---------|-----|
| `briefing/extrato-figma.png` | Imagem de referência visual (exportar do Figma; anexar no chat) |
| `briefing/figma-specs.txt` | Regras de layout Flexbox, tipografia e ícones |
| `app/src/styles.css` | Design Tokens nativos (`--color-*`, `--spacing-*`, etc.) |

# DIRETRIZES TÉCNICAS

1. **Arquitetura de Dados**
   - Crie um Standalone Component chamado `PixHistoryComponent`.
   - Defina uma interface TypeScript `Transaction` com: `id`, `title`, `amount`, `type` (`'received' | 'sent'`), `date`.
   - Use um `signal` com array mockado de **3 transações** para popular a tela.
   - Consulte `get_best_practices` via Angular MCP antes de gerar o código.

2. **Control Flow Moderno**
   - No template HTML, use **obrigatoriamente** a sintaxe `@for` do Angular 21 com `track transaction.id`.

3. **Fidelidade e Tokens**
   - O layout deve espelhar a imagem do Figma, aplicando as regras de `figma-specs.txt`.
   - É **PROIBIDO** usar cores hexadecimais ou valores absolutos de cor no `.css` do componente.
   - Substitua as cores do Figma pelos tokens de `styles.css`:

   | Figma (`figma-specs.txt`) | Token CSS |
   |---------------------------|-----------|
   | Borda `#E2E8F0` | `var(--color-border-subtle)` |
   | Data `#64748B` | `var(--color-text-muted)` |
   | Valor recebido `#10B981` | `var(--color-received)` |
   | Valor enviado `#EF4444` | `var(--color-sent)` |

   - Espaçamentos devem usar tokens: padding do item `16px 24px` → `var(--spacing-medium) var(--spacing-large)`; gap ícone/texto `12px` → `var(--spacing-icon-gap)`.

4. **Layout (`figma-specs.txt`)**
   - Lista (`PixHistoryList`): Flexbox vertical, `gap: 0`.
   - Item (`TransactionItem`): Flexbox horizontal, `justify-content: space-between`, `align-items: center`, padding `16px 24px`, `border-bottom` com token de borda.

5. **Tipografia (`figma-specs.txt`)**
   - Título da transação: `font-weight: 600`, `var(--font-size-title)`.
   - Data: `font-weight: 400`, `var(--font-size-caption)`, `var(--color-text-muted)`.
   - Valor: `font-weight: 700`, `var(--font-size-amount)`; cor conforme `type`.

6. **Ícones**
   - Use a classe global `.material-symbols-outlined` (já em `styles.css`).
   - Ícones de envio/recebimento: `arrow_downward` (recebido) e `arrow_upward` (enviado).
   - Tamanho: `var(--icon-size-md)`; gap com texto: `var(--spacing-icon-gap)`.

7. **Acessibilidade**
   - Envolva a lista em `<section aria-labelledby="history-title">`.
   - Use `<time [dateTime]="...">` para datas.
   - Ícones decorativos com `aria-hidden="true"`; valores com `aria-label` descritivo.

# ESTRUTURA ESPERADA
```
app/src/app/pix-history/
├── pix-history.component.ts
├── pix-history.component.html
└── pix-history.component.css
```

Rota: `/extrato` em `app.routes.ts`.

# PROMPT DE EXECUÇÃO
Cole no chat após anexar este arquivo (ou use `componente-figma.txt`):

```
Atuando com base em @figma-to-angular.md, analise a imagem em anexo e leia @briefing/figma-specs.txt.
Crie o componente Angular completo `PixHistoryComponent`, consumindo EXCLUSIVAMENTE os tokens de @app/src/styles.css.
```

# CRITÉRIOS DE ACEITE
- [x] `PixHistoryComponent` standalone compila sem erros (`npm run build`)
- [x] Interface `Transaction` com os 5 campos obrigatórios
- [x] `signal` com 3 transações mockadas
- [x] Template usa `@for` com `track`
- [x] Nenhuma cor hexadecimal no `.css` do componente
- [x] Layout Flexbox conforme `figma-specs.txt` (padding, gap, alinhamento)
- [x] Ícones Material Symbols para envio/recebimento
- [x] Rota `/extrato` configurada

# FORMATO DE SAÍDA
Gere os arquivos `.ts`, `.html` e `.css` do componente.
