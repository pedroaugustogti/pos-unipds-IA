# Report executivo — Escopo implementação até produção

**Projeto:** Guardião Família  
**Board:** GitHub Project #2 (replano do zero)  
**Horizonte:** 6 meses · 13 sprints · 7 seniors  
**Data:** 2026-08-19

---

## 1. Sumário

Replano completo abandonando as 238 tasks do Project #1. Novo backlog com **272 tasks granulares**, **24 épicos** em 3 trilhas (produto, infraestrutura, stores), priorizado por RICE + WSJF com baseline derivado de **análise de commits** nos 6 repositórios.

| Métrica | Valor |
|---------|-------|
| Tasks totais | 272 |
| Já entregues (done) | 61 (22%) |
| Parciais | 80 (29%) |
| A fazer (todo) | 131 (48%) |
| Story Points total | 831 |
| PERT total (dias) | 444 |
| Release blockers | 36 |
| SP restante estimado | ~400 |

**Conclusão:** Com velocity 40 SP/sprint e 51 tasks já concluídas, o escopo **cabe no horizonte de 180 dias** se blockers (push nativo, ECS prod, stores) forem atacados nos sprints S1–S3 e S11–S13.

---

## 2. Objetivos de negócio (OKRs)

### O1 — Segurança da criança
SOS, geofences e push nativo. **Gap #1:** sons push não bundlados nos apps.

### O2 — Release e compliance
AWS ECS Fargate, LGPD, submissão App Store + Google Play (4 apps).

### O3 — Experiência familiar
Tempo extra E2E, polish child, parent com IA MVP e relatórios.

---

## 3. Épicos (24)

### Produto (13)
E-P01 Auth · E-P02 Localização · E-P03 Geofences · E-P04 SOS · E-P05 Push nativo · E-P06 Tempo de tela · E-P07 Gamificação · E-P08 Família · E-P09 Parent app · E-P10 Child app · E-P11 LGPD · E-P12 Backoffice · E-P13 Site

### Infraestrutura (6)
E-I01 ECS Fargate · E-I02 CI/CD · E-I03 Observabilidade · E-I04 PostgreSQL/Redis · E-I05 Segurança · E-I06 Staging/Prod

### Stores (5)
E-S01 Apple parent · E-S02 Apple child · E-S03 Google parent · E-S04 Google child · E-S05 Coordenação release

---

## 4. Top 10 prioridades (ranking)

1. T-P05-001 — Bundlar sons push iOS parent
2. T-P05-002 — Bundlar sons push iOS child
3. T-P05-003/004 — Sons Android parent/child
4. T-I01-001–004 — AWS ECS foundation
5. T-I04-001/003 — RDS + Redis
6. T-P04-005/006 — Push SOS <30s iOS/Android
7. T-P03-005/006 — Geofence E2E iOS/Android
8. T-P11-009 — DPO sign-off LGPD
9. T-S01-006 / T-S02-005 — Submit Apple
10. T-S03-005 / T-S04-005 — Production Google Play

---

## 5. Cronograma macro

| Fase | Sprints | Entrega |
|------|---------|---------|
| Fundação cloud | S1–S2 | ECS, RDS, CI/CD |
| Segurança core | S3–S6 | Push, SOS, geofence E2E |
| Produto completo | S7–S10 | ST, child polish, parent IA |
| Compliance | S8 | LGPD + pen test |
| Lojas | S11–S12 | Apple + Google 4 apps |
| Go-live | S13 | Beta 100, release, monitor 72h |

---

## 6. Estado do código (commits)

**Pronto:** localização Mapbox matched, offline sync, support AI, backoffice live, site prod, TestFlight ambos apps, LGPD parcial, paywall desabilitado.

**Pendente crítico:** push nativo, geofence/SOS E2E timing, ECS prod completo, Google Play submit, DPO sign-off.

---

## 7. Riscos

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Review Apple background location | Média | Alto | Review notes + vídeo demo (T-S01-005) |
| ECS migration downtime | Média | Alto | Blue/green eval (T-I07-008), rollback doc |
| Push SOS P95 > 30s | Média | Crítico | Sprint S3 dedicado push nativo |
| Capacidade 831 SP | Baixa | Médio | 61 done + parallel 7 devs |
| LGPD menores | Baixa | Crítico | Sprint S8 + DPO blocker |

---

## 8. Artefatos entregues

```
docs/criacao-board/
├── 01-okrs/ … 09-report/
├── 07-planilhas/
│   ├── calc_rice.csv
│   ├── calc_wsjf.csv
│   ├── calc_pert.csv
│   ├── calc_story_points.csv
│   ├── calc_epicos_resumo.csv
│   └── BACKLOG_PRIORIZADO_FINAL.csv
├── 08-board/github-project-2-import.json
└── scripts/
    ├── generate_board_v2.py
    └── import_github_project_v2.py
```

---

## 9. Próximos passos operacionais

1. Criar GitHub Project #2 "Guardião Família v2"
2. Configurar campos custom (Trilha, OKR, Epic, Sprint, SP, RICE, WSJF, Blocker)
3. Executar `import_github_project_v2.py` (272 draft issues)
4. Iniciar Sprint S1 — épicos E-I01 + E-I04
5. Daily tracking release blockers (36 items)

---

## 10. Fora de escopo confirmado

Rebrand Vínculo · Paywall release · Comunidade · EKS · Tasks Project #1
