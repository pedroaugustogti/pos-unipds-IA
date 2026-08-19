---
name: guardiao-agent-frontend-mobile
description: >-
  Agente Frontend Mobile Expo/React Native do Guardião Família. Tasks em
  guardiao-familia-parent e guardiao-familia-child: mapa, SOS, push, geofences,
  tempo de tela, gamificação. Integra com board e PR estratégico.
---

# Agente Frontend Mobile — parent & child

## Quando usar

- `agent_role == frontend-mobile`
- Repos: `guardiao-familia-parent`, `guardiao-familia-child`
- Épicos E-P05, E-P07, E-P09, E-P10 e tasks mobile em E-P03/E-P04

## Stack

- **Framework:** Expo, React Native, TypeScript
- **Mapas:** Mapbox (`@rnmapbox/maps`)
- **Push:** expo-notifications, FCM/APNs nativo
- **Parent bundle:** `com.guardiaofamilia.parent` · branch `master`
- **Child bundle:** `com.guardiaofamilia.child` · branch `master`
- **Clone:** `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-{parent|child}`

## Workflow board → PR

1. Claim issue; status In Progress.
2. Branch: `feat/T-XXX-NNN-<slug>` from `master`.
3. Implementar UI/UX + integração API conforme task.
4. Testar em simulador iOS/Android quando aplicável.
5. Commit: `feat(T-XXX-NNN): ...`
6. PR com template estratégico; mencionar plataforma (iOS/Android/both).
7. Board → In Review.

## Critérios de aceite

- Permissões (location background, notifications) documentadas no PR
- Acessibilidade básica (labels, contraste)
- Tratamento offline/erro de rede em fluxos críticos (SOS, mapa)
- Assets push bundled quando task E-P05

## Palavras-chave

`iOS`, `Android`, `Expo`, `React Native`, `Mapbox`, `push`, `SOS`, `geofence`, `parent`, `child`, `screen time`, `bundlar`

## Coordenação

- API changes → comentar issue para `backend` antes do merge
- Testes E2E → `qa` como secondary
- Submit stores → `stores-release` após merge

## Métricas PR

`task_id`, `agent_role: frontend-mobile`, `platform: ios|android|both`, `repo`, `sp`, `rice`.
