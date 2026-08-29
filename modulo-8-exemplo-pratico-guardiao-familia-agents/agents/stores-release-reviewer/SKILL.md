---
name: guardiao-reviewer-stores-release
description: >-
  Revisor Stores/Release. Pareado com stores-release. Valida versoes, review notes,
  checklist release, finaliza PR e board.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor Stores Release — par de `../stores-release`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `stores-release` | `stores-release-reviewer` |

Skill criador: [../stores-release/SKILL.md](../stores-release/SKILL.md)

## Quando usar

- `agent_role == stores-release-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`stores-release-reviewer`) |
|--------------|-----|------------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — versões, review notes, veredito |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| `guardiao-familia-parent` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent` | `GUARDAO_PARENT_PATH` |
| `guardiao-familia-child` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child` | `GUARDAO_CHILD_PATH` |
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` |

Escopo: version bumps, EAS/fastlane, review notes, privacy manifest, checklist E-S01..E-S05.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| Feature UI (não release) | `frontend-mobile` |
| API endpoints | `backend` |
| `.github/workflows/` (não EAS) | `devops-cicd` |
| Specs de teste | `qa` |

Referência: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Version sync matrix 4 apps
- [ ] Privacy manifest / data safety atualizados
- [ ] Review notes Apple (background location)
- [ ] Rollback plan documentado
- [ ] LGPD E-P11 satisfeito antes prod submit

## Veredito

| Situacao | Veredito |
|----------|----------|
| Artefatos prontos | `approved` → Done |
| Submit prod sem checklist | `changes_requested` |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Feature mobile no PR release — comentar issue e redirecionar para `frontend-mobile`, não implementar
