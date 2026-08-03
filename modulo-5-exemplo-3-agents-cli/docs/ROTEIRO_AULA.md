# Roteiro de Aula — Agents CLI (~2h)

Scaffold gerado pelo **delivery-agent** ([`delivery-agent`](../../delivery-agent/)).

**Referência UNIPDS:** [modulo-03](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 2 — Prototyping UI ✅ | **Ex. 3 — Agents CLI** | Ex. 4 — Automação MCP |

**App alvo:** `../modulo-5-exemplo-2-prototyping-ui/app/`

## Roteiro

### 1. Recapitulação (15 min)
- Demo: `/pix`, `/extrato`, `/comprovante`
- Revisar [`EVIDENCIAS_ACEITE.md`](../modulo-5-exemplo-2-prototyping-ui/docs/EVIDENCIAS_ACEITE.md)
- Conceito: prototipação ≠ produção

### 2. Setup CLI (20 min)
```bash
cd ../modulo-5-exemplo-2-prototyping-ui/app
npm run build && npm test -- --watch=false
```

### 3. Lab 1 — Código morto (25 min)
Prompt: `@prompts/dead-code-cleanup.md` + `@prompts/refactor-safe.md`

### 4. Lab 2 — CSS mobile (25 min)
Prompt: `@../modulo-5-exemplo-2-prototyping-ui/prompts/correcao_css.md` via CLI vs Cursor

### 5. Lab 3 — Testes (25 min)
Prompt: `@prompts/test-gap-fixer.md`

### 6. Encerramento (10 min)
- Preencher [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md)
- Preview Ex. 4 (MCP + Playwright)

## Discussão
1. Cursor Agent vs CLI agent?
2. Como limitar escopo do diff?
3. Papel do review humano?
