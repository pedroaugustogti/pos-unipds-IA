# Briefing inicial ? Guardiao Familia

## Resumo executivo

O Guardiao Familia e uma plataforma multi-superficie de seguranca e vinculo familiar formada por apps mobile para responsavel e crianca, API central NestJS, backoffice operacional e site institucional. A proposta de valor combina localizacao, SOS, cercas virtuais, tempo de tela, IA de apoio e compliance LGPD para dados de menores.

O board atual possui 238 itens organizados por ondas de entrega, mas ainda sem a governanca necessaria para um planejamento de 6 meses orientado a resultado. Este trabalho reorganiza o board como se o projeto estivesse no ponto zero de gestao, sem apagar a maturidade tecnica ja existente.

## Estado atual resumido

- API com modulos relevantes prontos para auth, localizacao, SOS, notificacoes, tempo de tela, gamificacao, IA e compliance.
- App parent com mapa, familia, alertas, IA e CI iOS EAS.
- App child com SOS, localizacao e readiness parcial para App Store.
- Backoffice e site em operacao, mas com alto volume de issues abertas.
- Gap critico conhecido: sons push nativos ainda nao bundlados nos apps, embora a API ja envie payloads customizados.

## Problema de gestao atual

O board por ondas ajuda no contexto funcional, mas nao responde quatro perguntas executivas:

1. O que move os resultados do negocio primeiro?
2. O que bloqueia release?
3. O que cabe em 6 meses com esse time?
4. Qual a probabilidade de cumprir o prazo?

## Objetivo deste planejamento

Responder essas quatro perguntas por meio de:

- OKRs de 6 meses.
- Priorizacao por RICE e WSJF.
- Planejamento de sprints por capacidade realista.
- Forecast probabilistico via PERT e Monte Carlo.
- Estrutura do GitHub Project preparada para reset e reescrita dos cards.

## Escopo de 6 meses

### Resultado esperado ao final do periodo

- Infraestrutura AWS em ECS Fargate, com RDS PostgreSQL, ElastiCache Redis, ALB, ECR, Secrets Manager e CloudWatch.
- Fluxos criticos E2E validos: SOS, geofence alert e pedido de tempo extra.
- Apps prontos para App Store e Google Play, incluindo assets, privacy labels e push nativo.
- Backoffice suficientemente estavel para suporte operacional de um beta/release.
- Conjunto minimo de evidencias LGPD para release responsavel.

### Fora de escopo

- Rebrand Vinculo.
- Paywall e monetizacao como meta de release.
- Reestruturacao para EKS/Kubernetes.

## Macro-riscos

- Risco de atraso por dependencias cross-repo mobile + API.
- Risco de review de stores e privacidade infantil.
- Risco de variacao de escopo se marketing/rebrand entrar no release.
- Risco operacional se o board nao for reescrito com campos de decisao.

## Recomendacao inicial

Tratar o projeto em tres trilhas paralelas:

1. **Release foundation:** AWS, CI/CD, compliance, stores.
2. **Critical child safety:** push nativo, SOS e geofence.
3. **Family experience:** tempo extra, app child polish e relatorios/IA no app parent.
