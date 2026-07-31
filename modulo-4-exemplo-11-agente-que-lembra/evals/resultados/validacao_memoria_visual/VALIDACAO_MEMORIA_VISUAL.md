# Validacao visual — tipos de memoria (Ex. 11)

- Execucao 1: `alerta de latencia no servico de pagamentos`
- Execucao 2: `erro 500 no servico de pagamentos`

## Resumo

| Tipo | Persiste? | Arquivos gerados |
|------|-----------|------------------|
| Curta | Nao (RAM) | snapshot JSON |
| Longa | Sim (YAML) | 7 |
| Episodica | Sim (YAML) | 2 |
| Contextual | Aula 14 | 0 (placeholder) |

## Recuperacao na execucao 2

```
--- Conhecimento previo (memoria) ---
Fatos conhecidos (memoria longa):
- [buscar_logs] entrada={janela_tempo_minutos=78, nivel_minimo=nivel_minimo_sem_api_key, nome_servico=pagamentos} | contagem_total=3, eventos=[{'mensagem': 'timeout conectando a upstream-payments: 30s exceeded', 'nivel': 'ERROR', 'servico': 'pagamentos', 'timestamp': '2026-07-31T08:59:25.962356'}, {'mensagem': 'circuit breaker aberto para upstream-payments', 'nivel': 'ERROR', 'servico': 'pagamentos', 'timestamp': '2026-07-31T09:03:25.962356'}, {'mensagem': 'latencia p99 acima do SLO: 342ms > 200ms', 'nivel': 'WARN', 'servico': 'pagamentos', 'timestamp': '2026-07-31T09:06:25.962356'}]
- [buscar_logs_historico] entrada={janela_tempo_horas=319, nivel_minimo=nivel_minimo_sem_api_key, nome_servico=pagamentos} | contagem_total=3, eventos=[{'mensagem': 'connection timeout em pagamentos', 'nivel': 'ERROR', 'servico': 'pagamentos', 'timestamp': '2024-01-15T10:32:00Z'}, {'mensagem': 'pool de conexoes esgotado em pagamentos', 'nivel': 'WARN', 'servico': 'pagamentos', 'timestamp': '2024-01-15T10:28:00Z'}, {'mensagem': 'query lenta detectada em pagamentos: 4500ms', 'nivel': 'ERROR', 'servico': 'pagamentos', 'timestamp': '20
```
