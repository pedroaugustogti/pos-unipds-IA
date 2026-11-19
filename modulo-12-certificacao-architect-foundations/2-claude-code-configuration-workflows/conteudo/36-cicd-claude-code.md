# 3.6 — Claude Code em CI/CD

## Objetivo
Review no pipeline: criterios explicitos, multi-pass, structured output, controle de FP, least privilege.

## Analogia
Inspecao por estacoes — nao um olheiro unico no fim.

## Fluxo
```text
PR → Pass A security (nova sessao) → Pass B correctness → agregar JSON → comentar/falhar
```

Same-session self-review = anti-padrao.

## Exemplo (conceitual)
```yaml
- name: claude-review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude -p "/ci-review" --output-format json > review.json
    python scripts/validate_review.py review.json
```

FP: medir → desligar categoria → apertar criterio → religar.

## Mini-lab
2 passes + schema de finding (`file`, `line`, `severity`, `rule_id`, `message`).

## Checkpoint
- [ ] Multi-pass
- [ ] Secrets fora do prompt

← [3.5](./35-refinamento-iterativo.md) · [ESTUDO](./ESTUDO.md)
