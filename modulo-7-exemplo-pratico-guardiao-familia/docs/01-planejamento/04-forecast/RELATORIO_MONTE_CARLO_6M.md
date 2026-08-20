# Forecast probabilistico ? 6 meses

Este forecast usa entradas PERT por epico e simulacao Monte Carlo para estimar a chance de concluir o plano dentro da janela de 6 meses.

## Parametros da simulacao

- Runs: 10.000
- Seed: 42
- Metodo: triangular por epico com PERT como referencia de media
- Janela executiva comparada: 180 dias

## Resultado consolidado

| Medida | Dias |
|--------|------|
| PERT total | 134.83 |
| P50 | 141.48 |
| P80 | 149.45 |
| P95 | 157.35 |
| Min observado | 108.70 |
| Max observado | 175.57 |

## Leitura gerencial

- O plano **cabe em 6 meses no P80** (`149.45 <= 180`).
- O intervalo entre P50 e P80 e relativamente controlado, sugerindo escopo plausivel se o time mantiver disciplina de corte.
- O risco maior esta concentrado em infraestrutura inicial, flows E2E mobile e review das stores.

## Buffers adotados

- App Store review: 10 a 15 dias corridos adicionais.
- Google Play review: 3 a 7 dias corridos adicionais.
- Acoplamento cross-repo mobile + API: refletido no `p_dias` mais alto de `E4` e `E1R`.

## Recomendacao executiva

- Compromisso publico: usar leitura entre **P80 e P95**.
- Compromisso interno: operar com **P50** como alvo de acompanhamento.
- Se algum release blocker de O1/O2 escapar de sua sprint, reduzir O3 antes de alongar a janela de release.
