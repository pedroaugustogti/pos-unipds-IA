# Contrato CI — modelo (CCAR-F 3.6 + 4.1)

Pacote didático pronto para copiar para `.claude/ci/` + workflow.

## Peças

| Arquivo | Papel |
|---------|--------|
| `finding-schema.json` | Contrato parseável (`category`, `severity`, `status`) |
| `PROMPT_CORRECTNESS.md` | Include/exclude + severity com exemplo + PREV + tests |
| `PROMPT_SECURITY.md` | Pass security isolado |
| `gate_reviews.py` | Falha o job se `high` (código = contrato) |
| `ci-pr-claude.yml` | `-p`, 2 instances, artifacts, sem `--resume` |

## Boas práticas cobertas

1. **FP baixo** — categories report/skip + severity com exemplo (`If unsure → skip`)  
2. **`-p`** — CI não espera input  
3. **JSON + schema** — pipeline não parseia prosa  
4. **PREV findings** — dedupe entre runs (artifact)  
5. **Tests existentes** — não reabre cobertura já assertada  
6. **Instances separadas** — correctness ≠ security ≠ author session  
7. **Gate em código** — `gate_reviews.py`, não “confie no modelo”

## Como instalar no repo

```text
.claude/ci/
  finding-schema.json
  PROMPT_CORRECTNESS.md
  PROMPT_SECURITY.md
  gate_reviews.py
.github/workflows/pr-claude-review.yml  ← copiar de ci-pr-claude.yml
```

Ajuste paths de testes e o `sed` do prompt (diffs grandes podem precisar de arquivo temp em vez de inline).

## Exemplo de saída esperada

```json
{
  "run_meta": { "pass": "correctness", "commit": "abc123" },
  "findings": [
    {
      "rule_id": "refund-limit-op",
      "category": "payment_side_effects",
      "severity": "high",
      "file": "src/billing/refund.py",
      "line": 88,
      "message": "Boundary amount uses < instead of <= for AUTO_REFUND_LIMIT",
      "evidence": "if amount < AUTO_REFUND_LIMIT:",
      "status": "new"
    }
  ]
}
```
