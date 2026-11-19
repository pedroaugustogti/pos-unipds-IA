# 5.7 — Historico append-only e compactacao moderna

## Objetivo
Em modelos com thinking preservado: nao editar/remover turns antigos no client; preferir compact server-side / context editing; mudancas via novas mensagens system.

## Analogia
Livro razao contabil: voce lanca novos assentos — nao rasura paginas velhas sem invalidar a auditoria.

## Regras praticas
1. Messages array append-only
2. Mid-session: `role: system` novo (tools/instrucoes)
3. Trim via compaction/context editing — nao snip manual de turns com thinking
4. Estado critico fora do chat (memory/file/DB)

## Mini-lab
Explique o que quebra se o host apagar 3 tool_results antigos para "economizar tokens" numa sessao com thinking.

## Checkpoint
- [ ] Append-only justificado
- [ ] Compact ≠ delete arbitrario de historia

← [5.6](./56-provenance.md) · [ESTUDO](./ESTUDO.md)
