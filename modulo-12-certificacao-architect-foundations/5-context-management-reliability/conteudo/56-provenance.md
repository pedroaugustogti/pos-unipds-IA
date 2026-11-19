# 5.6 — Proveniencia da informacao

## Objetivo
Separar dado recuperado de inferencia; citar fonte quando policy exige; tratar injection como dado.

## Analogia
Jornalismo: fato com fonte vs opiniao do reporter.

## Praticas
- Policy exige citacao → rejeitar resposta sem fonte
- KB/ticket com "ignore instructions" → **nao** obedece; system/policy prevalece
- Marcar no output: `source` vs `inferred`

## Exemplo
```json
{
  "answer": "Prazo de troca e 7 dias",
  "source": "kb://politica-trocas#prazo",
  "inferred": false
}
```

## Mini-lab
Resposta correta a ticket com prompt injection pedindo revelar system prompt.

## Checkpoint
- [ ] Dado vs inferencia
- [ ] Injection = dado

← [5.5](./55-human-review.md) · [ESTUDO](./ESTUDO.md) · → [5.7](./57-append-only.md)
