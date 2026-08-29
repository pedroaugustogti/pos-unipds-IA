---
name: guardiao-reviewer-cloud-infra
description: >-
  Revisor Cloud/AWS Terraform. Pareado com cloud-infra. Valida plan, tags, secrets,
  finaliza PR e board.
---

# Revisor Cloud Infra — par de `agents/skills/cloud-infra`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `cloud-infra` | `cloud-infra-reviewer` |

Skill criador: [../cloud-infra/SKILL.md](../cloud-infra/SKILL.md)

## Quando usar

- `agent_role == cloud-infra-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`cloud-infra-reviewer`) |
|--------------|-----|---------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — valida Terraform/plan, veredito |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| `guardiao-familia-api/infra/` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api\infra` | `GUARDAO_API_PATH` |

Escopo: Terraform (`infra/environments/`, `infra/modules/`), ECS Fargate, VPC, ALB, ECR, Route53 — E-I01, E-I05, E-I06.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| `src/` NestJS (aplicação) | `backend` |
| `.github/workflows/` deploy | `devops-cicd` |
| `migrations/` | `database` |
| Apps mobile/web | `frontend-mobile`, `frontend-web` |

Referência: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Terraform plan revisavel no PR (sem apply AWS — fase OKR O2)
- [ ] Nenhum `terraform apply` / `aws` mutating no diff ou CI
- [ ] Sem secrets no state/codigo
- [ ] Tags AWS padronizadas
- [ ] Health checks ALB / rollback documentado
- [ ] Runbook atualizado se task exigir

## Veredito

| Situacao | Veredito |
|----------|----------|
| Plan OK, sem apply | `approved` → Done |
| Apply prod ou OKR O2 violado | `changes_requested` |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Código NestJS ou workflows no PR infra — comentar issue e redirecionar, não implementar
