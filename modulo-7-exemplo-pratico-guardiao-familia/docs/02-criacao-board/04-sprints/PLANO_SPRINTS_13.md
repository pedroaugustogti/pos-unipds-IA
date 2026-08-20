# Plano de sprints S1–S13 (6 meses)

Capacidade: **7 seniors × 10 dias úteis × 0.7 foco = ~49 dev-dias/sprint**  
Velocity alvo: **40 SP/sprint** → **520 SP** no horizonte (trabalho restante ~400 SP cabe com buffer)

| Sprint | Foco principal | Épicos | SP alocado | Entregável |
|--------|----------------|--------|------------|------------|
| S1 | AWS foundation | E-I01, E-I04 | 40 | VPC, ECS cluster, RDS staging |
| S2 | CI/CD + DB prod | E-I02, E-I04 | 40 | Pipelines verdes, Redis |
| S3 | Push nativo + observability | E-P05, E-I03 | 40 | Sons iOS/Android bundlados |
| S4 | Localização hardening | E-P02 | 40 | Histórico, SLA, testes batch |
| S5 | SOS E2E | E-P04, E-P05 | 40 | Push SOS <30s ambas plataformas |
| S6 | Geofences E2E | E-P03, E-P09 | 40 | UI cercas + alertas iOS/Android |
| S7 | Tempo de tela | E-P06, E-P10 | 40 | Pedido extra E2E, ST visível parent |
| S8 | LGPD + segurança | E-P11, E-I05 | 40 | Export/delete, pen test checklist |
| S9 | Child polish | E-P07, E-P10 | 40 | Gamificação, UX, acessibilidade |
| S10 | Parent IA + relatórios | E-P09, E-P08 | 40 | IA MVP, família, relatórios |
| S11 | Stores Apple | E-S01, E-S02, E-P12 | 40 | TestFlight → submit |
| S12 | Stores Google + staging prod | E-S03, E-S04, E-I06 | 40 | Play rollout, cutover staging |
| S13 | Release | E-S05, E-P13 | 40 | Beta 100, go-live, monitor 72h |

## Distribuição por trilha

| Trilha | Sprints dominantes |
|--------|-------------------|
| Infra | S1, S2, S3, S8, S12 |
| Produto | S4–S10 |
| Stores | S11–S13 |

## Riscos de capacidade

- PERT total backlog: **444 dias** vs **180 dias** calendário → paralelismo 7 devs + 51 tasks já `done`
- Release blockers (36): concentrados S3, S5, S6, S11–S13
- Buffer implícito: tasks `partial` (80) têm SP menor efetivo
