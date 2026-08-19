# Análise de commits — baseline para tasks

**Data:** 2026-08-19  
**Fonte:** `git log -50` em cada repo em `Documents/guardiao-familia`  
**Arquivo bruto:** [commits_por_repo.json](commits_por_repo.json)

## Metodologia

1. Extrair últimos 50 commits por repositório
2. Classificar por prefixo (`feat`, `fix`, `chore`, `ci`)
3. Mapear para épicos v2 e `status_baseline`:
   - **done** — evidência mergeada, task de validação/doc only
   - **partial** — implementado mas E2E/testes/release pendentes
   - **todo** — gap identificado sem commit correspondente

## guardiao-familia-api (50 commits)

| Tema | Commits exemplo | Épico | Baseline |
|------|-----------------|-------|----------|
| Localização Mapbox | cb9a003, fa32b83, 7d4995d | E-P02 | done/partial |
| Offline sync | b6702bf, 83156e6 | E-P02 | done |
| Geofence batch | aa7a914, 18d2dbf | E-P03 | partial |
| LGPD | 4c0102b | E-P11 | partial |
| Device/session | 0ff10dc, f39c9c6 | E-P01 | done |
| Infra/deploy | 5821a0a, 97946a2 | E-I01/E-I02 | partial |
| Support AI | e2c6ea8, fc17873 | E-P12 | done |
| AI provider | 1fc606d | E-P09 | done |

**Tasks geradas:** 39 módulos API expandidos (T-P14-*) + tasks core

## guardiao-familia-parent (20 commits)

| Tema | Commits | Épico | Baseline |
|------|---------|-------|----------|
| Map routes | f5047fa, 94559c0 | E-P09 | done |
| Offline route UI | aef5509 | E-P09 | done |
| Paywall off | c64e9f4 | E-P06 | done |
| ST hidden | bfb44c7 | E-P06 | partial |
| EAS iOS submit | ce8728d, c1bb681 | E-S01 | partial |
| Auth refresh | b535706 | E-P01 | partial |

**Tasks geradas:** 27 parent-specific (T-P09-*, T-S01-*)

## guardiao-familia-child (20 commits)

| Tema | Commits | Épico | Baseline |
|------|---------|-------|----------|
| Offline routes | 0dbbc08 | E-P02 | done |
| Privacy App Store | f26520e | E-S02 | partial |
| Background location | 3d58268, ed373a3 | E-P10 | done |
| Pairing | fd9882d, 26c519e | E-P01 | done |
| TestFlight | badaa4e, b099a45 | E-S02 | partial |
| GP submit CI | 3e37e38 | E-S04 | done |

**Tasks geradas:** 22 child-specific (T-P10-*, T-S02/S04-*)

## guardiao-familia-backoffice (20 commits)

| Tema | Commits | Épico | Baseline |
|------|---------|-------|----------|
| Live support | ff7ba8a, b870fd6 | E-P12 | done |
| Cloudflare stats | bf172e8 | E-I03 | partial |
| SSM deploy sa-east-1 | c23d55c | E-I02 | done |
| Fiscal/accounting | c407331, 945c666 | fora escopo release | — |

## guardiao-familia-site (15 commits)

| Tema | Commits | Épico | Baseline |
|------|---------|-------|----------|
| Landing completa | 5e76430 | E-P13 | done |
| Chatbot | 637dd2a | E-P13 | done |
| CNPJ legal | 8928a7e | E-P13 | done |
| Pre-launch links | a6fac08 | E-P13 | done |

## campanha (1 commit)

| Tema | Commits | Épico | Baseline |
|------|---------|-------|----------|
| Estrutura 30 dias | 2556642 | E-P13 | done |

## Gaps críticos (todo) derivados da análise

1. Sons push nativos — API tem soundId; apps não bundlam assets
2. Geofence/SOS E2E push timing — API melhorou delivery; apps sem validação P95
3. ECS Fargate prod — commits mencionam infra hardening mas Terraform incompleto
4. Google Play production — CI valida secret; listing/submit pendentes
5. DPO sign-off LGPD — docs existem em api/docs; sign-off release pendente

## Rastreabilidade commit → task

Cada task com `commit_evidence` preenchido referencia SHA curto do commit que motivou baseline `done`/`partial`. Ver coluna `commit_evidence` em `07-planilhas/BACKLOG_PRIORIZADO_FINAL.csv`.
