# D5 — Context Management & Reliability (15%)

> 6 task statements · [CertPrep D5](https://certprep.pratechlabs.com/claude/ccar-f/learn/) · [mapa 30 tasks](../../README.md#mapa-dos-30-tasks)

## O que a prova valida

Preservar fatos (CASE FACTS); escalate/ambiguity; erro entre agentes; codebase grande; human review + confidence; provenance na síntese.

## Trilha = tasks 5.1–5.6

| Task | Arquivo | One-liner |
|------|---------|-----------|
| 5.1 | [51-janela-e-compact.md](./51-janela-e-compact.md) | CASE FACTS; trim tools; importante no início (não no miolo) |
| 5.2 | [52-escalation-patterns.md](./52-escalation-patterns.md) | Escalate: pedido humano / policy gap / stuck — não sentiment/confidence |
| 5.3 | [53-error-propagation.md](./53-error-propagation.md) | Retry local; reportar tipo + parcial + alternativas; não abortar tudo |
| 5.4 | [54-large-codebase.md](./54-large-codebase.md) | Scratchpad; sub Explore; summaries; `/compact`; export+manifest pós-crash |
| 5.5 | [55-human-review.md](./55-human-review.md) | Calibrar confidence; métrica por tipo de doc; same-session self-review = não |
| 5.6 | [56-provenance.md](./56-provenance.md) | Cada claim com fonte+data; conflito → mostrar ambos |

**Extra:** [57-append-only.md](./57-append-only.md) — histórico append-only (apoio 5.1/1.7).

## Cronograma dias 14–15

| Dia | Tasks | Prática |
|-----|-------|---------|
| 14 | 5.1 + 5.3–5.4 | CASE FACTS + empty vs fail + scratchpad |
| 15 | 5.2 + 5.5–5.6 | Handoff + provenance |

## Hábitos CertPrep (D5)

- Nunca chutar ID; nunca esconder falha  
- Dois customers → perguntar identificador  
- Duas fontes divergem → mostrar as duas com data  

## Checklist

- [ ] CASE FACTS
- [ ] Triggers vs anti-triggers de escalate
- [ ] Empty vs timeout na fala ao user
- [ ] Provenance na síntese

## Prova

[`../prova/PROVA.md`](../prova/PROVA.md)
