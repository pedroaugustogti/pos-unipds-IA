---
name: guardiao-reviewer-devops-cicd
description: >-
  Revisor CI/CD e observabilidade. Pareado com devops-cicd. Valida workflows,
  finaliza PR e board.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor DevOps CI/CD — par de `../devops-cicd`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `devops-cicd` | `devops-cicd-reviewer` |

Skill criador: [../devops-cicd/SKILL.md](../devops-cicd/SKILL.md)

## Quando usar

- `agent_role == devops-cicd-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [STATEGRAPH_FLOW.md](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`devops-cicd-reviewer`) |
|--------------|-----|---------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — workflows, OIDC, veredito |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| Todos os 5 repos | `.github/workflows/` em cada | `GUARDAO_*_PATH` |

Paths: api, parent, child, backoffice, site — ver `lib/repo_paths.py`.

Escopo: GitHub Actions, OIDC, ECR/ECS deploy, observabilidade — E-I02, E-I03, T-I08-*.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| `infra/**/*.tf` | `cloud-infra` |
| `src/` NestJS ou UI apps | `backend`, `frontend-mobile`, `frontend-web` |
| `migrations/` | `database` |
| EAS submit / store config | `stores-release` |

Referência: [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Workflow testavel; triggers corretos
- [ ] Deploy API via **ECR + ECS** (nao SSM/EC2 para API)
- [ ] OIDC / permissions minimas (`id-token`, ECR, ecs:UpdateService)
- [ ] Smoke test pos-deploy staging antes de prod gate
- [ ] Cache deps / jobs paralelos onde seguro
- [ ] Sem credenciais hardcoded; sem terraform apply no workflow
- [ ] Notificacao falha deploy
- [ ] Documentacao secrets (nomes only)

## Veredito

| Situacao | Veredito |
|----------|----------|
| Pipeline seguro e funcional | `approved` → Done |
| Pipeline quebrado ou inseguro | `changes_requested` |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Módulos Terraform no PR CI — comentar issue e redirecionar para `cloud-infra`, não implementar
