# Classificação dos cálculos de priorização

## Tabela de métodos

| Método | Fórmula | Escala | Uso no board | Peso ranking |
|--------|---------|--------|--------------|--------------|
| **RICE** | (Reach × Impact × Confidence) / Effort_SP | Reach 1–10, Impact 0.5–3, Confidence 0–1, SP Fibonacci | Valor vs esforço | 40% |
| **WSJF** | Cost_of_Delay / Job_Size_SP | CoD 1–13, SP Fibonacci | Urgência SAFe | 60% |
| **PERT** | (O + 4M + P) / 6 | Dias por task | Forecast Monte Carlo | Capacidade |
| **Story Points** | Fibonacci senior | 1≈0.5d, 2–3 story, 5 feature, 8 E2E, 13=quebrar | Sprint planning | Job size |
| **Priority Rank** | WSJF×0.6 + RICE×0.4 + boosts | Ordinal 1–N | Ordem final backlog | — |

## Boosts e penalidades

| Condição | Ajuste |
|----------|--------|
| `release_blocker=true` | +50 |
| OKR O1 | +15 |
| OKR O2 | +12 |
| OKR O3 | +5 |
| `status_baseline=partial` | +5 |
| `status_baseline=done` | −100 (backlog histórico) |

## Classificação por faixa RICE

| Faixa | RICE | Interpretação |
|-------|------|---------------|
| Crítica | ≥ 6.0 | Fazer imediatamente (push, blockers) |
| Alta | 4.0–5.9 | Próximo sprint |
| Média | 2.0–3.9 | Planejado |
| Baixa | < 2.0 | Backlog ou pós-release |

## Classificação por faixa WSJF

| Faixa | WSJF | Interpretação |
|-------|------|---------------|
| Crítica | ≥ 3.0 | Blocker release / segurança |
| Alta | 2.0–2.9 | Infra + compliance |
| Média | 1.0–1.9 | Features O3 |
| Baixa | < 1.0 | Nice-to-have |

## Planilhas geradas

| Arquivo | Conteúdo |
|---------|----------|
| `07-planilhas/calc_rice.csv` | Reach, Impact, Confidence, Effort, RICE |
| `07-planilhas/calc_wsjf.csv` | CoD, Job Size, WSJF |
| `07-planilhas/calc_pert.csv` | O, M, P, Expected days |
| `07-planilhas/calc_story_points.csv` | SP por task e sprint |
| `07-planilhas/calc_epicos_resumo.csv` | Agregado por épico |
| `07-planilhas/BACKLOG_PRIORIZADO_FINAL.csv` | **Consolidado final** |

## Totais consolidados (272 tasks)

- **SP total:** 831
- **PERT total:** 444.2 dias
- **Release blockers:** 36
- **Done / Partial / Todo:** 61 / 80 / 131
