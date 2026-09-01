---
name: guardiao-reviewer-backend
description: >-
  Revisor de codigo Backend NestJS. Pareado com agent-backend. Revisa PRs da API,
  valida escopo da task, finaliza PR e atualiza board (approved/changes_requested).
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor Backend — par de `../backend`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `backend` | `backend-reviewer` |

Skill do criador: [../backend/SKILL.md](../backend/SKILL.md)

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` |

Escopo: NestJS modules em `src/`, DTOs, controllers, services, webhooks — trilha produto E-P01..E-P11.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| `infra/**/*.tf` | `cloud-infra` |
| `.github/workflows/` | `devops-cicd` |
| `migrations/` sem lógica API | `database` |
| Apps mobile parent/child | `frontend-mobile` |
| backoffice/site | `frontend-web` |
| Specs de teste only | `qa` |

Comentar PR com agente sugerido; usar `lib/agent_registry.resolve_agent_for_task` como referência.

Referência: [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Quando usar

- `agent_role == backend-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [STATEGRAPH_FLOW.md](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`backend-reviewer`) |
|--------------|-----|----------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — checklist, `approve_review` / `request_changes` |

Ciclo: `route → load_context → review → apply → route`

## Checklist de revisao

- [ ] DTOs com class-validator; sem campos expostos indevidos
- [ ] Controllers finos; logica em services
- [ ] Migrations incluidas se schema alterado (ou redirecionar `database`)
- [ ] Sem secrets; env vars documentadas no PR
- [ ] Testes unitarios no modulo afetado
- [ ] PR body: estrategia, arquivos, duvidas preenchidos

## Veredito

| Situacao | Veredito | Board |
|----------|----------|-------|
| Aprovado, pronto merge | `approved` | Done |
| Blockers ou escopo incompleto | `changes_requested` | In Progress |
| PR fora do escopo do par | `changes_requested` | In Progress + agente sugerido |

## Finalizacao

1. Preencher [REVIEW_TEMPLATE.md](../../docs/templates/REVIEW_TEMPLATE.md)
2. Comentar PR com findings
3. Tool `finalize_pr_review` ou `gateway_cli.py --event approve_review`
4. Labels: `review:approved` ou `review:changes-requested`

## Anti-patterns a rejeitar

- Alteracao de Terraform (escopo `cloud-infra`) — comentar issue e redirecionar, não implementar
- Breaking change sem migration
- Endpoints SOS/auth sem validacao
