# Artefato de aula — custo financeiro da IA

Governança sem número vira desejo. Este arquivo marca o que medir antes de publicar um sistema.

Referências sugeridas no README UNIPDS do módulo 10:

| Ferramenta | Uso |
|------------|-----|
| [Data Center Map](https://www.datacentermap.com/) | Onde a carga roda |
| [AI Data Center Map](https://aidatacentermap.org/map) | Capacidade dedicada a IA |
| [Submarine Cable Map](https://www.submarinecablemap.com/) | Caminho da latência e da transferência |
| [Electricity Maps](https://app.electricitymaps.com/) | Intensidade de carbono da energia |

## O que registrar

| Pergunta | O que anotar |
|----------|--------------|
| Quanto custa uma chamada? | Token de entrada, token de saída, retrys e tools |
| Quanto custa um incidente? | Reembolso, multa, reputação, tempo de Blue Team |
| Quanto custa o controle? | HITL, auditoria, índice RAG, review de skill |
| Quem paga o loop? | Agente que chama ferramenta em ciclo (OWASP consumo sem limite) |
| O que a energia implica? | Região do data center e preço da eletricidade |

## Três bolsos

| Bolso | Exemplo | Ligação com a aula |
|-------|---------|--------------------|
| Operação | Endpoint Vertex, `gemini-2.5-flash`, embedding do RAG | Job do módulo 9 e notebook do Ex.2 |
| Falha | Cupom indevido, fila enviesada, prompt vazado | Soft law alerta; hard law e o tribunal cobram |
| Governança | `hitl_guard_actuation`, reindex, eval com vs sem retrieval | Controle que parece “custo morto” até o incidente |

CapEx e OpEx: [`DILEMA_ECONOMICO_IA.md`](./DILEMA_ECONOMICO_IA.md). PUE e desmatamento: [`PUE_E_IMPACTO_AMBIENTAL.md`](./PUE_E_IMPACTO_AMBIENTAL.md). Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).
