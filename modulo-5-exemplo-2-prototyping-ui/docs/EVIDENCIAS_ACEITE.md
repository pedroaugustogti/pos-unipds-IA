# Evidências de Aceite — Exemplo 2 (Prototyping UI)

Validação em **03/08/2026** contra prompts, specs do Exemplo 1 e build local.

## Comandos executados

```bash
cd app
npm run build   # ✅ sucesso
npm test -- --watch=false   # ✅ 5 testes passando
```

## Critérios globais (README)

| Critério | Status | Evidência |
|----------|--------|-----------|
| Pasta `modulo-5-exemplo-2-*` | ✅ | Estrutura do repositório |
| README local | ✅ | `README.md` |
| Entrada Ex. 1 documentada | ✅ | `docs/ENTRADA_EXEMPLO_1.md` |
| App Angular 21 (`npm run build`) | ✅ | Build sem erros |
| Caminho feliz Pix Agendado | ✅ | `/pix` → MFA → comprovante |
| ≥ 3 unhappy paths | ✅ | Limite R$ 5k, saldo, chave inválida, cancelamento bloqueado |
| `mensagens-ui.json` em `messages.ts` | ✅ | `core/messages.ts` |
| Angular MCP configurado | ✅ | `.cursor/mcp.json` |
| Prompts UNIPDS + índice | ✅ | `prompts/` (10+ arquivos) |
| Revisão `get_best_practices` | ✅ | `docs/MCP_REVISAO.md` |
| README raiz atualizado | ✅ | `README.md` (Módulo 5, Ex. 2 ✅) |

## `figma-to-angular.md` → `PixHistoryComponent`

| Critério | Status | Evidência |
|----------|--------|-----------|
| Standalone compila | ✅ | Lazy route `/extrato` |
| Interface `Transaction` (5 campos) | ✅ | `pix-history.component.ts:4-10` |
| `signal` com 3 transações | ✅ | `pix-history.component.ts:20-42` |
| `@for` com `track transaction.id` | ✅ | `pix-history.component.html:4` |
| Sem hex no `.css` | ✅ | Apenas `var(--*)` |
| Flexbox conforme `figma-specs.txt` | ✅ | padding 16×24, gap ícone 12px |
| Material Symbols envio/recebimento | ✅ | `arrow_downward` / `arrow_upward` |
| Rota `/extrato` | ✅ | `app.routes.ts` |
| Acessibilidade | ✅ | `aria-labelledby`, `<time>`, `aria-label` |

## `google-stitch.md` → `PixReceiptComponent`

| Critério | Status | Evidência |
|----------|--------|-----------|
| Standalone compila | ✅ | Integrado em `pix-transfer` + `/comprovante` |
| Sem hex/Tailwind no `.css` | ✅ | `features/receipt/pix-receipt.component.css` |
| `@Input` Signals (`valor`, `nome`, `dataHora`, …) | ✅ | `pix-receipt.component.ts` |
| Layout fiel ao `modelo/code.html` | ✅ | Card, faixa, check, valor, detalhes, CTA |
| Ícones `check_circle`, `arrow_forward` | ✅ | Template do componente |
| `@Output` `voltarInicio` | ✅ | Navegação em `pix-transfer` e preview |
| A11y `role="region"` + `:focus-visible` | ✅ | Template + CSS do botão |

## `figma-to-code.md` → fluxo Pix Agendado

| Critério | Status | Evidência |
|----------|--------|-----------|
| Wizard transferência | ✅ | `pix-transfer/` |
| Limite diário R$ 5.000 | ✅ | `DAILY_LIMIT` + validação |
| Não agendar hoje | ✅ | Modal Pix imediato |
| MFA senha demo `1234` | ✅ | Modal MFA |
| Idempotency key no POST | ✅ | `crypto.randomUUID()` em `confirmSchedule` |
| Lista/cancelamento agendamentos | ✅ | `/agendamentos` |

## `correcao_css.md`

| Critério | Status | Evidência |
|----------|--------|-----------|
| Extrato mobile em coluna | ✅ | `@media (max-width: 600px)` em `pix-history.component.css` |
| Menu hambúrguer colapsável | ✅ | `isMenuOpen` signal em `app.ts` + `app.html` |
| Contraste no recibo | ✅ | Tokens `--color-text`, `--color-text-muted` no card |

## Rotas da aplicação

| Rota | Componente | Uso |
|------|------------|-----|
| `/pix` | `PixTransfer` | Wizard + comprovante pós-agendamento |
| `/extrato` | `PixHistoryComponent` | Lista de transações (Figma) |
| `/agendamentos` | `PixSchedulesComponent` | Cancelar agendamentos |
| `/comprovante` | `ReceiptPreview` | Preview visual do Stitch |

## Demo rápida (sala de aula)

1. `cd app && npm start` → http://localhost:4200
2. **Extrato:** `/extrato` — validar tokens e ícones
3. **Comprovante:** `/comprovante` — validar layout Stitch
4. **Fluxo:** `/pix` → chave válida → valor `100` → data futura → MFA `1234`
5. **Erros:** valor `6000` · chave `invalid@pix` · cancelar item em processamento em `/agendamentos`

## Pendências opcionais (não bloqueiam aceite)

- `briefing/extrato-figma.png` — exportar do Figma e versionar (referência visual)
- Limpar pasta `features/` legada do scaffold inicial (não referenciada nas rotas)
