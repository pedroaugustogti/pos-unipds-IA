# loop.md — delivery-agent

```yaml
objetivo: preparar_proxima_aula

ciclo:
  max_etapas: 20

condicoes_parada:
  - objetivo_alcancado
  - max_etapas_excedido
  - sem_progresso
  - limite_tempo_excedido
  - confirmacao_humana_negada
```