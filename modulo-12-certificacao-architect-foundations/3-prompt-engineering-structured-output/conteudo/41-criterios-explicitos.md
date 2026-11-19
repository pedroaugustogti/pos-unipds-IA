# 4.1 — Criterios explicitos

## Objetivo
Trocar "seja conservador" por include / exclude / exemplos de fronteira.

## Analogia
Juiz com codigo penal claro vs "use o bom senso".

## Estrutura
1. O que **qualifica**
2. O que **nao** qualifica
3. Exemplos I/O na borda

## Exemplo — review de comentario vs codigo

**Ruim:** "So reporte alta confianca."

**Bom:**
```text
Flag SECURITY quando:
- Input do user vai a SQL sem parameterizacao
- HTML sem escape
- Credencial hardcoded

NAO flag:
- ORM ja parameterizado
- Template com auto-escape
- Segredo via env var
```

**FP:** categoria barulhenta derruba confianca em todas → desligar, melhorar criterio, religar.

## Mini-lab
Reescreva: "Seja rigoroso com bugs de concorrencia" em include/exclude + 1 exemplo.

## Checkpoint
- [ ] Prompt com include/exclude
- [ ] Plano anti-FP

← [ESTUDO](./ESTUDO.md) · → [4.2](./42-few-shot.md)
