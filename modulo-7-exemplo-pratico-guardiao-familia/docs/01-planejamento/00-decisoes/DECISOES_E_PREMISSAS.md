# Decisoes e premissas

## Decisoes fechadas pelo usuario

1. **Marca:** Guardiao Familia only.
   - Motivo: reduzir variabilidade de copy, branding e risco de rejeicao nas stores dentro do horizonte de 6 meses.
2. **Simulacao de governanca:** resetar todos os cards para `Todo`.
   - Motivo: planejar como se o projeto nao tivesse iniciado, preservando o estado atual apenas como baseline tecnico.
3. **Visibilidade:** tornar os 6 repos e o Project publicos.
   - Motivo: transparencia, referencia academica e melhoria de colaboracao.
4. **Monetizacao:** pos-release.
   - Motivo: paywall ja aparece desabilitado no estado atual; seguranca, LGPD e stores tem prioridade maior.
5. **AWS:** ECS Fargate.
   - Motivo: menor carga operacional que EKS para um time pequeno e com foco em entrega funcional.

## Premissas do planejamento

- Horizonte: 6 meses.
- Cadencia: 13 sprints de 2 semanas.
- Equipe: 2 frontend senior, 2 backend senior, 1 DBA senior, 1 arquiteto cloud AWS, 1 QA.
- Objetivo do plano: chegar a release publico seguro, com infraestrutura prod-like, apps publicaveis e fluxos criticos E2E estaveis.
- Baseline tecnico: ha codigo relevante pronto em localizacao, SOS, geofences, LGPD parcial, apps em TestFlight e backoffice/site em producao.

## Fora do escopo nos 6 meses

- Rebrand Vinculo.
- Stripe/paywall como meta de release.
- Exploracao de microservicos Java/K8s.
- Expansao da comunidade familiar como prioridade principal.

## Consequencias praticas

- Onda 9 fica limitada a operacao/admin necessario para release, sem monetizacao.
- Onda 10 vira trilha de hardening e publicacao, nao de refinamentos amplos de UX.
- O board precisa de campos novos para separar historico (`Onda`) de planejamento (`OKR`, `Epic`, `Story Points`, `Sprint`, `RICE`, `WSJF`).
