# OKRs — Guardião Família v2 (horizonte 6 meses)

## O1 — Garantir segurança confiável da criança

| KR | Métrica | Meta |
|----|---------|------|
| KR1 | SOS E2E (trigger → push → ack) | Validado iOS + Android, P95 < 30s |
| KR2 | Geofence alert E2E | Entrada/saída com push customizado, P95 < 30s |
| KR3 | Sons push nativos | Bundlados e homologados parent + child |

**Épicos vinculados:** E-P03, E-P04, E-P05, E-P02 (localização)

## O2 — Prontidão operacional e compliance para release

| KR | Métrica | Meta |
|----|---------|------|
| KR1 | LGPD fluxos críticos | Exportação, exclusão, consentimento auditados + DPO sign-off |
| KR2 | AWS ECS Fargate prod-like | Staging + produção estáveis, CI/CD verde |
| KR3 | Stores checklist | 4 apps submetidos (Apple + Google × parent + child) |

**Épicos vinculados:** E-P11, E-I01–E-I06, E-S01–E-S05, E-P12

## O3 — Experiência familiar completa e utilizável

| KR | Métrica | Meta |
|----|---------|------|
| KR1 | Tempo extra E2E | Pedido → decisão → notificação child |
| KR2 | Child app beta aberto | UX polish, gamificação, estabilidade |
| KR3 | Parent MVP | Mapa, relatórios básicos, assistente IA |

**Épicos vinculados:** E-P06, E-P07, E-P08, E-P09, E-P10, E-P13

## Perguntas usadas na definição estratégica

1. **O que impede publicação amanhã?** → O2 + stores + infra (blockers)
2. **O que coloca a criança em risco real se falhar?** → O1 SOS/geofence/push
3. **O que já existe no código (commits)?** → baseline `done`/`partial` vs `todo`
4. **O que gera retenção pós-release?** → O3 tempo extra, gamificação, IA
5. **O que fica explicitamente fora?** → Rebrand Vínculo, paywall, comunidade

## Regra de desempate entre OKRs

```
Prioridade = WSJF×0.6 + RICE×0.4 + boost_OKR + boost_blocker − penalidade_done
```

O1 > O2 > O3 quando CoD equivalente.
