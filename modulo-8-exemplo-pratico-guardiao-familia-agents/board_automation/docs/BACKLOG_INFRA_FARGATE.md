# Backlog infra — migração ECS Fargate (O2)

Reorganização em **26 tasks ativas** (`T-I08-*` + remanescentes).  
Gerado por: `python board_automation/scripts/seeds/reprioritize_infra_fargate.py`

Artefatos:
- `BACKLOG_INFRA_FARGATE.csv` — RICE/WSJF/priority_rank
- `TASK_AGENT_MAP_FARGATE.csv` — roteamento agentes
- `BACKLOG_INFRA_FARGATE.json` — superseded + tasks

## Fórmulas (CLASSIFICACAO_CALCULOS)

- **RICE** = (Reach × Impact × Confidence) / Effort_SP
- **WSJF** = Cost_of_Delay / Effort_SP
- **Priority score** = WSJF×0.6 + RICE×0.4 + 50 (release_blocker) + 12 (OKR O2)

## Ignorados (já compatíveis com TF EC2 atual)

| ID | Motivo |
|----|--------|
| T-I01-001 | `modules/networking` |
| T-I01-004 | `modules/alb` (retarget em T-I08-004) |
| T-I01-007 | `modules/kms_secrets` → migrar T-I08-006 |
| T-I01-009 | ACM em `modules/alb` |
| T-I04-001/003 | `modules/rds`, `elasticache` |
| T-I05-004 | `modules/s3_ses` |
| T-I07-003 | OIDC em `prod/main.tf` |
| T-I02-002…007 | done |

## Substituídos por onda T-I08

T-I01-002/003/005/006/008/010, T-I02-001/010, T-I07-002/008 → ver coluna `notes` no CSV.

## Top 10 por priority score

| Rank | ID | RICE | WSJF | Agente | Sprint |
|------|-----|------|------|--------|--------|
| 1 | T-I08-003 | 6.0 | 3.67 | cloud-infra | 1 |
| 2 | T-I08-006 | 5.67 | 3.33 | cloud-infra | 2 |
| 3 | T-I08-009 | 5.1 | 3.0 | cloud-infra | 4 |
| 4 | T-I08-019 | 5.1 | 3.0 | devops-cicd | 7 |
| 5 | T-I08-010 | 4.8 | 2.67 | cloud-infra | 5 |
| 6 | T-I08-001 | 4.8 | 2.6 | cloud-infra | 1 |
| 7 | T-I08-012 | 5.1 | 2.4 | devops-cicd | 4 |
| 8 | T-I08-004 | 4.8 | 2.4 | cloud-infra | 3 |
| 9 | T-I08-002 | 2.81 | 1.62 | cloud-infra | 2 |
| 10 | T-I08-011 | 2.81 | 1.62 | devops-cicd | 3 |

**Ordem de execução:** respeitar `depends_on` e `sprint` (fundação ECS antes de deploy CI).

## Validação SKILL devops-cicd

| Task remanescente | Coberta na SKILL? |
|-------------------|-------------------|
| T-I08-011 build→ECR→ECS | ✅ Escopo + tasks |
| T-I08-012 OIDC prod | ✅ Auth CI→AWS |
| T-I08-013 smoke test | ✅ Critérios aceite |
| T-I08-014 Container Insights | ✅ Observabilidade ECS |
| T-I08-015 circuit breaker | ✅ Rollback/deploy |
| T-I08-019 rollback doc | ✅ Workflow PR |
| T-I07-004 branch protection | ✅ Critérios (branch protection) |
| T-I07-005 log retention | ✅ Observabilidade |
| T-I03-004 PagerDuty | ✅ Alertas |
| T-I03-005 OTel | ✅ Stack alvo |

**Gap corrigido:** SKILL anterior citava deploy EC2/SSM e não ECR/ECS Fargate — atualizada em `agents/skills/devops-cicd/SKILL.md`.

## Sincronização GitHub (2026-08-26)

26 issues criadas em `guardiao-familia-api` (#287–#312), **Todo** no Project #2.  
Log: `agents/00-runtime/system/board/seed_infra_fargate_log.jsonl` · Script: `board_automation/scripts/seeds/seed_infra_fargate_tickets.py`

10 issues superseded fechadas (#123, #124, #135, #136, #138, #140, #157, #179, #198, #204).  
Compatíveis TF marcados **Done** no `github-project-2-import.json`.  
`TASK_AGENT_MAP.csv` mesclado (283 linhas).

| Rank | ID | Issue |
|------|-----|-------|
| 1 | T-I08-003 | [#287](https://github.com/guardiaofamilia/guardiao-familia-api/issues/287) |
| 6 | T-I08-001 | [#292](https://github.com/guardiaofamilia/guardiao-familia-api/issues/292) |
| 7 | T-I08-012 | [#293](https://github.com/guardiaofamilia/guardiao-familia-api/issues/293) |
| 16 | T-I08-011 | [#302](https://github.com/guardiaofamilia/guardiao-familia-api/issues/302) |

## Política OKR O2

Tickets `cloud-infra`: só alteração Terraform (`plan`, sem apply).  
Tickets `devops-cicd`: workflows e validação; deploy ECS staging via CI; prod com gate humano (`T-I08-018`).
