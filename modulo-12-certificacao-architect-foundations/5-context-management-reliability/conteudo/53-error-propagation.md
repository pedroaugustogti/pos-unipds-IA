# 5.3 — Propagacao de erro

## Objetivo
Propagar erro com contexto; subagente faz retry local; nao abortar tudo; empty ≠ fail.

## Exemplo
```json
{
  "failure_type": "timeout",
  "service": "kb_search",
  "attempted_query": "return policy electronics >500",
  "is_retryable": true,
  "partial_results": null,
  "alternatives": ["FAQ direto", "simplificar query"]
}
```

Anti: `"Operation failed"` · `results:[]` em outage · matar workflow inteiro.

## Mini-lab
Dialogo user-facing para empty vs timeout da mesma search.

## Checkpoint
- [ ] Empty vs fail na fala ao user
- [ ] Retry local no sub antes de subir

← [5.2](./52-escalation-patterns.md) · [ESTUDO](./ESTUDO.md) · → [5.4](./54-large-codebase.md)
