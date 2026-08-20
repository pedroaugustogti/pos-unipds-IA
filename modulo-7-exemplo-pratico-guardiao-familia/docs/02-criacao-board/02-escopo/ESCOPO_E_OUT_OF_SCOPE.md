# Escopo e out-of-scope — 6 meses

## Dentro do escopo

### Produto (120+ tasks)
- Auth, pareamento, família, mensagens
- Localização Mapbox, offline sync, geofences
- SOS com áudio, escalation, push nativo
- Tempo de tela + pedido extra
- Gamificação child, polish UX ambos apps
- LGPD export/delete/consentimento
- Backoffice suporte mínimo release
- Site + campanha pré-lançamento

### Infraestrutura (53 tasks)
- AWS ECS Fargate (VPC, ALB, ECR, autoscaling)
- RDS PostgreSQL multi-AZ, ElastiCache Redis
- CI/CD 6 repos, smoke tests, OIDC
- Observabilidade, WAF, secrets, staging/prod

### Stores (36 tasks)
- App Store parent + child (metadata, TestFlight, submit)
- Google Play parent + child (data safety, rollout)
- Beta 100 famílias, monitoramento 72h pós-release

## Fora do escopo

| Item | Motivo |
|------|--------|
| Rebrand Vínculo | Decisão usuário — horizonte 6M |
| Paywall/monetização | Pós-release; flag desabilitada |
| Comunidade familiar | Backlog v2 |
| EKS/microserviços Java | ECS Fargate decidido |
| Project #1 tasks | Substituído por board v2 |

## Premissas

- Time: 7 seniors (2 FE, 2 BE, 1 DBA, 1 arquiteto AWS, 1 QA)
- 13 sprints × 2 semanas = 180 dias
- Velocity alvo: 38–42 SP/sprint (~520 SP úteis; backlog 831 SP inclui done/partial)
- Trabalho restante estimado: ~131 tasks todo + partial ≈ 400 SP

## Baseline técnico (commits mai/2026)

Código **já entregue** refletido como `status_baseline=done`:
- Rotas Mapbox matched, offline sync idempotente
- LGPD hardening parcial, SOS/device sync
- Support AI + live board backoffice
- TestFlight parent/child, site/BO em prod Cloudflare

Gap crítico documentado: **sons push nativos nos apps** (API pronta).
