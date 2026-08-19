# OKRs e epicos

## Objectives para 6 meses

### O1 ? Garantir seguranca confiavel da crianca
- KR1: SOS E2E validado em iOS e Android.
- KR2: Geofence alert E2E com P95 abaixo de 30 segundos.
- KR3: Sons push nativos bundlados e homologados nos dois apps.

### O2 ? Garantir prontidao operacional e compliance para release
- KR1: Fluxos LGPD criticos auditados e documentados.
- KR2: Plataforma AWS prod-like em ECS Fargate estavel para staging/producao.
- KR3: Apps submetidos com checklist de stores completo.

### O3 ? Entregar experiencia familiar completa e utilizavel
- KR1: Pedido de tempo extra E2E.
- KR2: Onda 5/6 do app child polida para beta aberto.
- KR3: App parent com relatorios e assistente IA MVP.

## Mapeamento Onda -> Epico -> OKR

| Onda | Epico | OKR principal | Justificativa |
|------|-------|---------------|---------------|
| 0 + 10 | E1 Fundacao e release | O2 | release exige base de infraestrutura e hardening |
| 1 + 8 | E2 Identidade e familia | O3 | onboarding e familia sustentam experiencia completa |
| 2 + 3 | E3 Localizacao e cercas | O1 | geofence e tempo real sao seguranca central |
| 4 | E4 SOS e emergencia | O1 | item de maior severidade para crianca |
| 5 | E5 Tempo de tela | O3 | valor cotidiano e fluxo comercial/retencao |
| 6 | E6 Engajamento crianca | O3 | aumenta adesao sem competir com release blockers |
| 7 | E7 IA e conteudo | O3 | IA no parent tem valor, mas nao deve bloquear go-live |
| 9 | E8 Admin operacional | O2 | so o minimo operacional para suporte ao release |
| transversal | E9 Compliance LGPD | O2 | requisito mandatorio para tratar dados de menores |

## Regras de priorizacao de epicos

1. O1 domina tudo que afeta seguranca infantil real.
2. O2 domina tudo que bloqueia publicacao ou conformidade legal.
3. O3 entra quando nao compromete O1/O2 no mesmo sprint.
4. Onda 9 fica reduzida ao necessario para suporte; monetizacao vai para backlog pos-release.
