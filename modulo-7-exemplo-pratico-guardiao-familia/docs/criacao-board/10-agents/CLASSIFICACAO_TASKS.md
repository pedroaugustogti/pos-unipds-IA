# Classificação de tasks para roteamento de agentes

Cada task do backlog recebe um `agent_role` primário e opcionalmente `agent_role_secondary` (colaboração).

## Prioridade de matching

Regras avaliadas **em ordem** — primeira match vence:

| # | Condição | Agent Role |
|---|----------|------------|
| 1 | `track == stores` | `stores-release` |
| 2 | Título contém `teste`, `test`, `e2e`, `spec`, `qa` (case insensitive) | `qa` |
| 3 | `epic_id == E-I04` OU título contém `migration`, `postgres`, `redis`, `schema`, `RDS` | `database` |
| 4 | `epic_id in (E-I02, E-I03)` OU título contém `CI/CD`, `pipeline`, `GitHub Actions`, `Sentry`, `observabilidade` | `devops-cicd` |
| 5 | `track == infraestrutura` | `cloud-infra` |
| 6 | `repo in (guardiao-familia-parent, guardiao-familia-child)` | `frontend-mobile` |
| 7 | `repo in (guardiao-familia-backoffice, guardiao-familia-site)` | `frontend-web` |
| 8 | `repo == guardiao-familia-api` AND `track == produto` | `backend` |
| 9 | Fallback | `backend` |

## Secondary roles (colaboração em PR)

| Situação | Secondary |
|----------|-----------|
| Task QA em repo mobile | `frontend-mobile` ou `backend` conforme `repo` |
| Task infra com migration | `database` |
| Task produto API com testes explícitos | `qa` |
| Task stores com alteração de código | `frontend-mobile` |

## Labels GitHub sugeridas

```
agent:backend
agent:frontend-mobile
agent:frontend-web
agent:cloud-infra
agent:database
agent:devops-cicd
agent:qa
agent:stores-release
agent:ready          # Todo — elegível para claim
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

Para desempate quando múltiplas tasks têm o mesmo `priority_rank`:

```
score = (1000 - priority_rank)
      + (50 if repo matches agent default repo)
      + (30 if sprint == sprint_atual)
      + (20 if status_baseline == todo)
      - (100 if agent_role_secondary != null and agent != secondary)
```

Agente só claim tasks onde `agent_role == <agent>` OR `agent_role_secondary == <agent>` com score > 0.

## Dependências

Respeitar [EPICOS_CATALOGO.md](../03-epicos/EPICOS_CATALOGO.md):

- Não claim task com `release_blocker=True` se épico dependente ainda `partial/todo` no baseline.
- Orquestrador consulta `status_baseline` no CSV antes do claim.

## Regenerar mapa

```powershell
python scripts/classify_tasks.py
```

Saída: [TASK_AGENT_MAP.csv](TASK_AGENT_MAP.csv)
