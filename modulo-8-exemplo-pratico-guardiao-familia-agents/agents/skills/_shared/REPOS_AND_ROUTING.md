# Repositórios e roteamento — Guardião Família

Base local: `C:\Users\pedro\Documents\guardiao-familia`

| Repo GitHub | Path local | Stack principal | Agente primário |
|-------------|------------|-----------------|-----------------|
| `guardiao-familia-api` | `...\guardiao-familia-api` | NestJS, PostgreSQL, Redis | `backend` |
| `guardiao-familia-parent` | `...\guardiao-familia-parent` | Expo/RN parent | `frontend-mobile` |
| `guardiao-familia-child` | `...\guardiao-familia-child` | Expo/RN child | `frontend-mobile` |
| `guardiao-familia-backoffice` | `...\guardiao-familia-backoffice` | Next.js | `frontend-web` |
| `guardiao-familia-site` | `...\guardiao-familia-site` | HTML/Cloudflare | `frontend-web` |
| `infra/` (dentro da API) | `...\guardiao-familia-api\infra` | Terraform AWS | `cloud-infra` |
| `.github/workflows/` (todos) | por repo | GitHub Actions | `devops-cicd` |
| migrations / schema | API `src/database` | TypeORM | `database` |
| `test/`, Appium, Playwright | por repo | QA harness | `qa-author` |
| Gate In Test | orquestrador | evidências | `qa-gate` |
| track `stores` | parent + child | EAS / stores | `stores-release` |

## Regra de redirecionamento (todas as skills)

Se a task estiver **fora do escopo** do agente atual:

1. **Não implementar** — comentar na issue com agente sugerido (`lib/agent_registry.py`).
2. Citar repo correto e path local da tabela acima.
3. LangGraph (`route_task`) reclassifica via `resolve_agent_for_task` antes de `implement`.
4. Labels: trocar `agent:*` para o agente classificado.

## Matriz rápida «fora do escopo → agente»

| Situação | Agente |
|----------|--------|
| Terraform, VPC, ECS, ECR módulos | `cloud-infra` |
| GitHub Actions, deploy pipeline | `devops-cicd` |
| Migration PostgreSQL / Redis RDS | `database` |
| Endpoint/service NestJS | `backend` |
| Tela parent/child mobile | `frontend-mobile` |
| Backoffice ou site | `frontend-web` |
| Escrever/atualizar specs | `qa-author` |
| Validar PR em In Test | `qa-gate` |
| Submit App Store / Play | `stores-release` |

Implementação: `lib/agent_registry.classify_task`, `board_automation/scripts/cli/classify_tasks.py`, `board_automation/data/maps/TASK_AGENT_MAP.csv`.

Fluxo LangGraph (nós, status, eventos): [_shared/STATEGRAPH_FLOW.md](STATEGRAPH_FLOW.md)
