# PAPEL
Atue como um Engenheiro Front-end Sênior especialista em Angular 21 e Design Systems corporativos.

# OBJETIVO
Refatorar o HTML/CSS bruto exportado do **Google Stitch** (`app/modelo/code.html`) em um Standalone Component Angular moderno, fiel ao layout desktop do comprovante Pix, consumindo os Design Tokens globais do projeto.

# ENTRADA OBRIGATÓRIA
Anexe os artefatos abaixo com `@` no chat:

| Arquivo | Uso |
|---------|-----|
| `app/modelo/code.html` | HTML/CSS bruto gerado pelo Google Stitch |
| `app/src/styles.css` | Design Tokens nativos (`--color-*`, `--spacing-*`, etc.) |
| `briefing/google-stitch.txt` | Briefing original da tela (opcional, para contexto) |

# DIRETRIZES TÉCNICAS

1. **Componentização Angular 21**
   - Crie um Standalone Component chamado `PixReceiptComponent`.
   - Use `@Input` Signals para dados dinâmicos: `valor`, `nome`, `dataHora`, `instituicao`, `transactionId`.
   - Emita `@Output` para a ação do botão **Voltar ao Início** (`voltarInicio`).
   - Consulte `get_best_practices` via Angular MCP antes de gerar o código.

2. **Estilização Restrita (Design Tokens)**
   - É **PROIBIDO** usar cores hexadecimais, classes Tailwind ou valores absolutos de cor no `.css` do componente.
   - Substitua todos os tokens do Stitch (ex.: `bg-secondary-fixed`, `text-on-surface`) pelas variáveis de `app/src/styles.css` (ex.: `var(--color-primary)`, `var(--color-action)`, `var(--color-text-muted)`).
   - Espaçamentos, raios e sombras devem usar `var(--spacing-*)`, `var(--radius-*)` e `var(--shadow-card)`.

3. **Ícones**
   - Use exclusivamente a classe global `.material-symbols-outlined` já definida em `styles.css`.
   - Ícones necessários: `check_circle` (sucesso), `arrow_forward` (botão).
   - Não adicione `<link>` do Google Fonts no componente; a fonte já está no `index.html`.

4. **Layout Desktop**
   - Mantenha o card centralizado na viewport (max-width ~480px).
   - Preserve a hierarquia visual do Stitch: faixa de destaque no topo, ícone de check, valor em destaque, detalhes da transferência e botão full-width no rodapé.
   - Ignore header, footer e navegação do `code.html` — extraia apenas o card do comprovante.

5. **Acessibilidade**
   - Marque o card com `role="region"` e `aria-label="Comprovante de transferência Pix"`.
   - O botão deve ter texto visível e suporte a `:focus-visible`.

# ESTRUTURA ESPERADA
```
app/src/app/features/receipt/
├── pix-receipt.component.ts
├── pix-receipt.component.html
└── pix-receipt.component.css
```

# PROMPT DE EXECUÇÃO
Cole no chat após anexar este arquivo:

```
Atuando com base em @google-stitch.md, refatore o conteúdo de @app/modelo/code.html.
Crie o componente Angular completo `PixReceiptComponent`, consumindo os tokens de @app/src/styles.css
e importando os ícones de @material-symbols-outlined.
```

# CRITÉRIOS DE ACEITE
- [x] Componente standalone compila sem erros (`npm run build`)
- [x] Nenhuma cor hexadecimal ou classe Tailwind no `.css` do componente
- [x] Dados dinâmicos via `@Input` Signals (`valor`, `nome`, `dataHora`)
- [x] Layout desktop fiel ao card do `code.html`
- [x] Ícones Material Symbols (`check_circle`, `arrow_forward`)
- [x] Botão **Voltar ao Início** emite evento para navegação

# FORMATO DE SAÍDA
Gere os arquivos `.ts`, `.html` e `.css` do componente.
