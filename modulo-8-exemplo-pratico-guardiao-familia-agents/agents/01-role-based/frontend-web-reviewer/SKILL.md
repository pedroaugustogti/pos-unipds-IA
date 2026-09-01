---
name: guardiao-reviewer-frontend-web
description: >-
  Revisor Web Next.js/HTML. Pareado com frontend-web. Revisa backoffice e site,
  finaliza PR e board.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor Frontend Web — par de `../frontend-web`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `frontend-web` | `frontend-web-reviewer` |

Skill criador: [../frontend-web/SKILL.md](../frontend-web/SKILL.md)

## Quando usar

- `agent_role == frontend-web-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [STATEGRAPH_FLOW.md](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`frontend-web-reviewer`) |
|--------------|-----|----------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — `approve_review` / `request_changes` |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| `guardiao-familia-backoffice` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-backoffice` | `GUARDAO_BACKOFFICE_PATH` |
| `guardiao-familia-site` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-site` | `GUARDAO_SITE_PATH` |

Escopo: Next.js backoffice (E-P12), site HTML/Cloudflare (E-P13).

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| `guardiao-familia-api/` | `backend` |
| parent/child apps | `frontend-mobile` |
| `infra/**/*.tf` | `cloud-infra` |
| `.github/workflows/` | `devops-cicd` |

Referência: [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Backoffice: guards de role/auth nas rotas admin
- [ ] Site: links LGPD, SEO basico, responsivo
- [ ] Sem breaking URLs publicas
- [ ] Chatbot funcional se task envolver
- [ ] PR lista paginas afetadas

## Veredito

| Situacao | Veredito |
|----------|----------|
| Aprovado | `approved` → Done |
| Blockers | `changes_requested` → In Progress |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Código mobile ou API no PR web — comentar issue e redirecionar, não implementar
