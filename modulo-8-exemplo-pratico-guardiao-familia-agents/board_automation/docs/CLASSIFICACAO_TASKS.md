# Classificação de tasks para roteamento de agentes

Cada task do backlog recebe um `agent_role` primário e opcionalmente `agent_role_secondary` (colaboração).

Implementação: `lib/core/agent_registry.classify_task` · roteamento LangGraph: [`../../agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](../../agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Prioridade de matching

Regras avaliadas **em ordem** — primeira match vence:

| # | Condição | Agent Role |
|---|----------|------------|
| 1 | `track == stores` | `stores-release` |
| 2 | Título contém `teste`, `test`, `e2e`, `spec`, `qa` (case insensitive) | `qa-author` |
| 3 | `epic_id == E-I04` OU título contém `migration`, `postgres`, `redis`, `schema`, `RDS` | `database` |
| 4 | `epic_id in (E-I02, E-I03)` OU título contém `CI/CD`, `pipeline`, `GitHub Actions`, `Sentry`, `observabilidade` | `devops-cicd` |
| 5 | `track == infraestrutura` | `cloud-infra` |
| 6 | `repo in (guardiao-familia-parent, guardiao-familia-child)` | `frontend-mobile` |
| 7 | `repo in (guardiao-familia-backoffice, guardiao-familia-site)` | `frontend-web` |
| 8 | `repo == guardiao-familia-api` AND `track == produto` | `backend` |
| 9 | Fallback | `backend` |

> CSV antigo pode conter `agent_role=qa`; `normalize_creator_role` mapeia para `qa-author`.

## Secondary roles (colaboração em PR)

| Situação | Secondary |
|----------|-----------|
| Task QA em repo mobile | `frontend-mobile` ou `backend` conforme `repo` |
| Task infra com migration | `database` |
| Task produto API com testes explícitos | `qa-author` |
| Task stores com alteração de código | `frontend-mobile` |

## Labels GitHub sugeridas

```
agent:backend
agent:frontend-mobile
agent:frontend-web
agent:cloud-infra
agent:database
agent:devops-cicd
agent:qa-author
agent:qa-gate
agent:stores-release
agent:ready          # Todo — elegível para dispatch
agent:in-progress    # In Progress
agent:ready-for-review  # Ready for Code Review
agent:in-review      # In Code Review
agent:ready-for-test # Ready for Test
agent:in-test        # In Test
agent:in-pr          # In Pull Request
agent:done           # Done
agent:blocked        # dependência externa (fora do pipeline)
type:bug             # fluxo alternativo bug
review:approved
review:changes-requested
reviewer:{role}-reviewer   # par do criador
```

## Score de adequação (orquestrador)

Fonte de status: import JSON do GitHub Project → `fields.Status` (campo `board_status` após `load_tasks()`).

Criadores só dispatcham a partir de `board_status == Todo`. Não usar `status_baseline` para elegibilidade.

Para desempate quando múltiplas tasks têm o mesmo `priority_rank`:

```
score = (1000 - priority_rank)
      + (50 if repo matches agent default repo)
      + (30 if sprint == sprint_atual)
      + (20 if board_status == Todo)
      + (40 if QA fila Ready for Test | merge In Pull Request)
      - (100 if agent_role_secondary != null and agent != secondary)
```

Agente só seleciona tasks onde `agent_role == <agent>` OR `agent_role_secondary == <agent>` com score > 0
(ou filas de etapa: qa-gate em Ready for Test/In Test; devops/stores em In Pull Request).

## Dependências

Respeitar épicos do backlog (ver catálogo no repo de planilhas):

- Não dispatch task com `release_blocker=True` se épico dependente ainda `partial/todo` no baseline.
- Orquestrador consulta `status_baseline` no CSV antes do dispatch.

## OKR infra (O2) — Terraform only

Tasks com `track=infraestrutura`, épico `E-I*` ou OKR **O2** (`agent_role` tipicamente `cloud-infra`, `database`, `devops-cicd`):

| Escopo | Detalhe |
|--------|---------|
| **Entrega** | Alterar estrutura em `infra/terraform` (HCL, módulos, vars) |
| **Evidência PR** | Diff + `terraform plan` opcional (sem apply) |
| **Proibido agora** | `terraform apply/destroy`, deploy AWS, cutover ECS/RDS |

Implementação em código: `board_automation/board/infra_policy.py`. LangGraph e agentes `cloud-infra` respeitam esta política no nó `implement`/`qa_validate`.

## Backlog Fargate (O2)

Migração EC2 → ECS: **`BACKLOG_INFRA_FARGATE.md`** + `data/maps/TASK_AGENT_MAP_FARGATE.csv`.

## Regenerar mapa

```powershell
python board_automation/scripts/cli/classify_tasks.py
```

Saída: [`../data/maps/TASK_AGENT_MAP.csv`](../data/maps/TASK_AGENT_MAP.csv)

## Eventos board (v2)

Transições **somente** via eventos role-based (`{role}_{status_slug}`). Gateway rejeita nomes v1 (`claim`, `open_pr`, …).

Catálogo: `board/task_status_workflow.py` · [`../../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md`](../../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md)
