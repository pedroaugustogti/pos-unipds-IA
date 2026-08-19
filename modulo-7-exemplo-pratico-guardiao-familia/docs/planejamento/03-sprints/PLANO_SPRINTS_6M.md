# Plano de sprints ? 6 meses

| Sprint | Objetivo | SP alvo | Entregas principais |
|--------|----------|---------|---------------------|
| S1 | Fundacao AWS 1 | 40 | VPC, ECS cluster, ECR, pipeline base |
| S2 | Fundacao AWS 2 | 40 | RDS PostgreSQL, Redis, deploy staging, observabilidade |
| S3 | Push nativo | 38 | `.wav` nos apps, validacao payload FCM/APNs, smoke test |
| S4 | SOS E2E iOS | 40 | fluxo child -> api -> parent homologado em iOS |
| S5 | SOS E2E Android | 40 | fluxo homologado em Android e ajuste de notificacoes |
| S6 | Geofence E2E | 40 | cercas, alertas e SLA de notificacao |
| S7 | Tempo extra E2E | 38 | pedido de tempo extra completo |
| S8 | LGPD e auditoria | 40 | consentimento parental, purge e trilha minima |
| S9 | Child polish | 40 | Onda 5/6, UX e confiabilidade do app crianca |
| S10 | Parent IA e relatorios | 40 | MVP de relatorios e assistente |
| S11 | Store readiness | 42 | assets, privacy labels, builds e checklist |
| S12 | Beta e suporte | 40 | backoffice live estavel e beta controlado |
| S13 | Hardening e release | 38 | runbook, buffers finais e publicacao |

## Regras de alocacao

- Nenhum sprint deve carregar mais de um release blocker grande alem da sua trilha principal.
- Cross-repo E2E deve ter QA envolvido desde o inicio da sprint.
- Itens `post-release` nao entram antes do fechamento de S13.
