# Memoria de calculo ? RICE e WSJF

## Convencoes adotadas

### RICE
- Reach: familias impactadas no trimestre.
- Impact: 0.25, 0.5, 1, 2 ou 3.
- Confidence: 0.5, 0.8 ou 1.0.
- Effort: story points totais da entrega.

### WSJF
- Cost of Delay = valor de negocio + urgencia temporal + reducao de risco/oportunidade.
- Cada componente de CoD usa escala de 1 a 13.
- Job Size = story points.

## Itens priorizados para o horizonte de 6 meses

| Item | Reach | Impact | Conf. | Effort | RICE | CoD | WSJF | Motivo resumido |
|------|-------|--------|-------|--------|------|-----|------|-----------------|
| AWS Fargate foundation | 600 | 3 | 0.8 | 13 | 110.77 | 34 | 2.62 | sem plataforma estavel nao ha release confiavel |
| Bundling sons push parent/child | 500 | 3 | 1.0 | 5 | 300.00 | 39 | 7.80 | fecha gap critico conhecido de SOS/geofence |
| SOS E2E iOS/Android | 500 | 3 | 0.8 | 8 | 150.00 | 39 | 4.88 | core de seguranca infantil |
| Geofence alert E2E | 420 | 2 | 0.8 | 8 | 84.00 | 31 | 3.88 | alto valor e dependencia moderada |
| Pedido tempo extra E2E | 300 | 2 | 0.8 | 5 | 96.00 | 24 | 4.80 | valor de uso recorrente e menor risco que SOS |
| LGPD audit flows | 600 | 2 | 0.8 | 8 | 120.00 | 34 | 4.25 | protege release e compliance de menores |
| Store readiness | 500 | 2 | 0.8 | 8 | 100.00 | 34 | 4.25 | sem assets/privacy/builds nao ha publicacao |
| App child polish O5/O6 | 260 | 1 | 0.8 | 8 | 26.00 | 18 | 2.25 | importante, mas abaixo de blockers |
| Parent relatorios + IA MVP | 220 | 1 | 0.8 | 8 | 22.00 | 17 | 2.12 | valor de experiencia, nao de sobrevivencia |
| Backoffice suporte live | 180 | 1 | 0.8 | 5 | 28.80 | 22 | 4.40 | necessario para operacao beta e suporte |

## Motivos dos inputs

- Reach alto em AWS, LGPD e release porque impactam todas as familias do rollout e toda a operacao.
- Impact maximo nos fluxos de SOS e push porque afetam seguranca infantil imediata.
- Confidence 1.0 apenas para bundling sons push, porque o gap ja esta bem descrito e a API esta pronta.
- Esforco 13 usado somente para fundacao AWS; o restante fica <= 8 para manter stories/epicos sprintaveis.

## Leitura recomendada

- Use **WSJF** para ordenar entrada de sprint.
- Use **RICE** para validar se o ranking faz sentido em valor ao usuario.
- Em empate, prefira item que desbloqueia release ou reduz risco juridico/operacional.
