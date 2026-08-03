# Evidências de Aceite — Exemplo 3 (Agents CLI)

Preencher ao concluir a aula.

## Comandos de validação

```bash
cd ../modulo-5-exemplo-2-prototyping-ui/app
npm run build
npm test -- --watch=false
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| Gemini CLI configurado e executado | [ ] | |
| Código morto removido/documentado | [ ] | |
| Build verde | [ ] | |
| Testes verdes | [ ] | |
| ≥ 3 testes novos em UI | [ ] | |
| ≥ 1 refatoração só via CLI | [ ] | log/screenshot |
| Diff revisado por humano | [ ] | |

## Registro de execução

| Lab | Prompt usado | Arquivos alterados | Build | Test |
|-----|--------------|-------------------|-------|------|
| 1 — dead code | `dead-code-cleanup.md` | | | |
| 2 — CSS | `correcao_css.md` | | | |
| 3 — testes | `test-gap-fixer.md` | | | |

## Mensagem de commit sugerida (delivery-agent)

```
feat(modulo-5): add agents-cli scaffold and pix-app refactors

- Remove dead scaffold from pix-app
- Add PixReceiptComponent tests
- Document CLI lab evidence
```
