# Relatorio: Com Framework vs Sem Framework

Comparacao entre o baseline **padrao** (Unidade 1, sem arquitetura cognitiva)
e a media das arquiteturas cognitivas (**react**, **plan_execute**, **reflect**).

| Metrica | Sem framework (padrao) | Com framework (media) | Diferenca | Melhoria |
|---------|------------------------|----------------------|-----------|----------|
| taxa_conclusao | 100.0 | 100.0 | 0.0 | igual |
| media_etapas | 5 | 5.33 | +0.33 | nao |
| media_tokens | 0 | 0 | 0 | igual |
| tokens_planejamento | 0 | 0 | 0 | igual |
| media_tempo_segundos | 0.0 | 0.0 | 0.0 | igual |
| taxa_sucesso_ferramentas | 100.0 | 100.0 | 0.0 | igual |
| circuit_breaker_total | 0 | 0 | 0 | igual |
| reflexoes_total | 0 | 3.33 | +3.33 | nao |
| cobertura_ferramentas | 100.0 | 100.0 | 0.0 | igual |

## O que o framework adiciona

| Capacidade | padrao | react | plan_execute | reflect |
|------------|--------|-------|--------------|---------|
| Raciocinio explicito no trace | nao | sim | parcial | sim |
| Plano upfront (tokens=0 nas etapas seguintes) | nao | nao | sim | nao |
| Autocritica antes de finalizar | nao | nao | nao | sim (10 reflexoes) |
| Cobertura media de ferramentas | 100.0% | 100.0% | 100.0% | 100.0% |

## O que o eval framework adiciona

- **Dataset com gabarito** (`ferramentas_esperadas`) — mede cobertura objetiva
- **Suite YAML com limiares** — contrato de qualidade automatizado
- **Benchmark engine** — 20 execucoes em batch, sem interpretacao subjetiva
- **Relatorio comparativo** — evidencia para escolher arquitetura em producao

## Resumo executivo

- Violacoes de limiar **sem framework**: 0
- Violacoes de limiar **com framework** (soma): 0
- O framework cognitivo **melhora ou mantem** a cobertura de ferramentas esperadas.
