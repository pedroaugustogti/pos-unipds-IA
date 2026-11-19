# 5.4 — Contexto em codebase grande

## Objetivo
Combater drift em sessao longa: re-ler arquivos criticos; Grep fresco; fork para exploracao; sumarizar achados no topo.

## Sintoma
Modelo cita "padroes tipicos" em vez do codigo visto ha 40 turns.

## Praticas
1. Re-Read antes de Edit em arquivos quentes
2. Preferir Grep/Glob a memoria
3. `context: fork` / subagente Explore
4. Bloco "ACHADOS" no topo da thread

## Mini-lab
Plano de 4 passos para localizar race condition em monorepo sem poluir a thread de fix.

## Checkpoint
- [ ] Drift reconhecido
- [ ] 3 mitigacoes

← [5.3](./53-error-propagation.md) · [ESTUDO](./ESTUDO.md) · → [5.5](./55-human-review.md)
