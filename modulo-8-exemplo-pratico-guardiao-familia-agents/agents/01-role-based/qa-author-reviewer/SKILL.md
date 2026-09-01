---
name: guardiao-reviewer-qa-author
description: >-
  Revisor de testes QA Author. Alias do qa-reviewer. Pareado com qa (qa-author).
  Valida cobertura cenarios criticos, finaliza PR e board.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor QA Author — par de `../qa-author`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `qa` (qa-author) | `qa-author-reviewer` |

Skill criador: [../qa/SKILL.md](../qa/SKILL.md)

## Quando usar

- `agent_role == qa-author-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [STATEGRAPH_FLOW.md](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`qa-author-reviewer`) |
|--------------|-----|-------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — cobertura specs, veredito |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var | Harness |
|------|------------|---------|---------|
| `guardiao-familia-api` | `...\guardiao-familia-api` | `GUARDAO_API_PATH` | Jest, `test/appium/` |
| `guardiao-familia-parent` | `...\guardiao-familia-parent` | `GUARDAO_PARENT_PATH` | specs mobile |
| `guardiao-familia-child` | `...\guardiao-familia-child` | `GUARDAO_CHILD_PATH` | specs mobile |
| `guardiao-familia-backoffice` | `...\guardiao-familia-backoffice` | `GUARDAO_BACKOFFICE_PATH` | Playwright |
| `guardiao-familia-site` | `...\guardiao-familia-site` | `GUARDAO_SITE_PATH` | Playwright |

Escopo: specs, harness, evidências — não implementação de features prod.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| Feature prod (não teste) | `backend`, `frontend-mobile`, `frontend-web` |
| `infra/**/*.tf` | `cloud-infra` |
| `.github/workflows/` | `devops-cicd` |
| Gate In Test (evidências PR merged) | `qa-gate` |

Referência: [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Cenarios criticos: SOS <30s, geofence E2E, push emergencia, pareamento Appium/API
- [ ] Testes rodam localmente (`agents/01-role-based/qa-gate/scripts/local_e2e_smoke.py` / `agents/01-role-based/qa-gate/scripts/local_e2e_stack.ps1`)
- [ ] Sem flaky nao documentado
- [ ] Gaps listados no PR
- [ ] Evidencias na issue quando E2E mobile
- [ ] Nao alterou logica prod desnecessariamente

## Veredito

| Situacao | Veredito |
|----------|----------|
| Cobertura OK | `approved` → Done |
| Release blocker sem cobertura | `changes_requested` |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Implementação de feature disfarçada de teste — comentar issue e redirecionar, não implementar
