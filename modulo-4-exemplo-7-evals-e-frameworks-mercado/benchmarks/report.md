# Relatorio Comparativo de Arquiteturas

Benchmark do `monitor-agent` contra 5 cenarios de incidente.

| Metrica | padrao | react | plan_execute | reflect |
|---------|------|------|------|------|
| taxa_conclusao | **100.0** | 100.0 | 100.0 | 100.0 |
| media_etapas | **5** | 5 | 5 | 6 |
| media_tokens | **0** | 0 | 0 | 0 |
| tokens_planejamento | **0** | 0 | 0 | 0 |
| media_tempo_segundos | **0.0** | 0.0 | 0.0 | 0.0 |
| taxa_sucesso_ferramentas | **100.0** | 100.0 | 100.0 | 100.0 |
| circuit_breaker_total | **0** | 0 | 0 | 0 |
| reflexoes_total | **0** | 0 | 0 | 10 |
| cobertura_ferramentas | **100.0** | 100.0 | 100.0 | 100.0 |

## Violacoes de Limiar

- **padrao**: nenhuma violacao
- **react**: nenhuma violacao
- **plan_execute**: nenhuma violacao
- **reflect**: nenhuma violacao

## Veredito

- **Maior cobertura de ferramentas:** padrao
- **Menor custo em tokens:** padrao
- **Mais rapido:** padrao
- **Menos etapas:** padrao

> Nao existe melhor absoluta. A escolha depende do que importa: custo, cobertura ou auditabilidade.