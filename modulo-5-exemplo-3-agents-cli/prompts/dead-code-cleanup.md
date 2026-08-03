# PAPEL
Atue como Engenheiro Front-end Sênior especialista em Angular 21.

# OBJETIVO
Remover **código morto** do `pix-app` sem quebrar rotas ou fluxos ativos.

# ESCOPO
Diretório: `modulo-5-exemplo-2-prototyping-ui/app/src/app/`

**Rotas ativas (NÃO remover):**
- `pix-transfer/` → `/pix`
- `pix-history/` → `/extrato`
- `features/receipt/` → comprovante + `/comprovante`
- `pix-schedules/` → `/agendamentos`
- `components/error-modal/`
- `core/`

**Candidatos a remoção (se não importados):**
- `features/contacts/`, `features/amount-date/`, `features/review/`, `features/schedules/`
- `features/receipt/receipt.component.*` (se existir e não referenciado)
- `shared/error-alert.component.ts` (se não importado)

# REGRAS
1. Confirme com busca de imports antes de deletar qualquer arquivo.
2. Não altere comportamento das rotas ativas.
3. Execute `npm run build` e `npm test -- --watch=false` ao final.

# FORMATO DE SAÍDA
Relatório: arquivos removidos, imports limpos, linhas economizadas, resultado do build/test.
