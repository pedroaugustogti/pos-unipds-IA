---
name: guardiao-reviewer-frontend-mobile
description: >-
  Revisor Mobile Expo/RN. Pareado com frontend-mobile. Revisa PRs parent/child,
  push, SOS, Mapbox. Finaliza PR e board.
---

# Revisor Frontend Mobile — par de `skills/frontend-mobile`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `frontend-mobile` | `frontend-mobile-reviewer` |

Skill criador: [../frontend-mobile/SKILL.md](../frontend-mobile/SKILL.md)

## Checklist

- [ ] Plataforma correta (iOS/Android/both) conforme task
- [ ] Permissoes location/notifications declaradas
- [ ] Tratamento erro rede em SOS/mapa
- [ ] Assets push bundled quando E-P05
- [ ] Sem regressao acessibilidade basica
- [ ] PR documenta plataforma e fluxos testados

## Veredito e board

- `approved` -> Done
- `changes_requested` -> In Progress (devolve ao criador)

## Foco de review

Mapbox, expo-notifications, hold SOS 3s, background location, bundles nativos.
