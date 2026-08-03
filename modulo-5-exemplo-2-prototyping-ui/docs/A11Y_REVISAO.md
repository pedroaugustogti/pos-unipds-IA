# Revisão A11y — `a11y-component-generator.md`

Auditoria dos componentes do app contra o prompt UNIPDS de acessibilidade.

## Critérios do prompt

| Critério | Status |
|----------|--------|
| WAI-ARIA (`role`, `aria-*`, `aria-hidden`) | ✅ Aplicado |
| Navegação por teclado + ESC em modais | ✅ Aplicado |
| CSS com tokens `var(--*)` nos componentes | ✅ Aplicado |

## Checklist por componente

### `app` (shell)
- [x] Skip link → `#conteudo-principal`
- [x] `role="banner"` no header
- [x] `aria-label` na navegação lateral
- [x] `aria-current="page"` nos links ativos
- [x] `aria-expanded` no menu mobile
- [x] ESC fecha menu lateral
- [x] `main` com `id` e `tabindex="-1"` para foco via skip link

### `error-modal` (`a11y-component-generator.md`)
- [x] Standalone `ErrorModal` com `input()` de `title` e `message`
- [x] Fechar via botão (ícone × e ação **Fechar**) ou tecla **ESC**
- [x] CSS exclusivamente com `var(--*)` de `styles.css`
- [x] `aria-labelledby` + `aria-describedby`
- [x] Foco inicial no botão fechar
- [x] ESC fecha o modal
- [x] Ícone decorativo com `aria-hidden="true"`

### `pix-transfer`
- [x] Formulário com `<label for>` em todos os campos
- [x] Modais MFA e Pix imediato: `role="dialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby`
- [x] ESC fecha modais
- [x] Foco automático no campo senha / diálogo instantâneo
- [x] Erros com `role="alert"` e `aria-invalid`
- [x] Overlay de processamento: `aria-live="polite"` + `aria-busy`

### `pix-receipt`
- [x] `<article>` com `aria-labelledby`
- [x] Lista de detalhes semântica (`<dl>/<dt>/<dd>`)
- [x] `<time datetime>` para datas
- [x] Ícones decorativos com `aria-hidden`

### `pix-history`
- [x] Seção com `aria-labelledby`
- [x] `<time datetime>` nas transações
- [x] Ícones com `aria-hidden`
- [x] `aria-label` + texto `.sr-only` no valor (recebido/enviado)

### `pix-schedules`
- [x] Seção com `aria-labelledby`
- [x] Loading: `aria-busy` + `aria-live` + texto `.sr-only`
- [x] Botão cancelar com `aria-label` contextual
- [x] Toast com `aria-live="polite"`
- [x] Badge de status com `role="status"`

## Utilitários globais (`styles.css`)

- `.skip-link` — navegação rápida por teclado
- `.sr-only` — texto apenas para leitores de tela
- `:focus-visible` — indicador de foco visível

## Teste manual sugerido

1. Navegar só com **Tab** / **Shift+Tab** pelo formulário e modais
2. Pressionar **ESC** em cada modal (erro, MFA, Pix imediato, menu mobile)
3. Usar leitor de tela (NVDA/VoiceOver) nos fluxos `/pix`, `/extrato`, `/agendamentos`
4. Verificar contraste no comprovante (header escuro + `--color-text-light`)
