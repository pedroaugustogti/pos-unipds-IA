# Workflow board — referência para todos os agentes

Cada `.agent.md` deve seguir esta matriz de **status GitHub Project #2**.

**Fonte de verdade local:** [`08-board/github-project-2-import.json`](../../08-board/github-project-2-import.json) → `items[].fields.Status`  
**Online:** [orgs/guardiaofamilia/projects/2](https://github.com/orgs/guardiaofamilia/projects/2) via `gh`

Doc completa: [`11-workflow/AGENT_BOARD_STAGES.md`](../../11-workflow/AGENT_BOARD_STAGES.md)

## Status (ordem)

`Todo` → `In Progress` → `Ready for Code Review` → `In Code Review` → `Ready for Test` → `In Test` → `In Pull Request` → `Done`

## Seleção de task

1. Orchestrator lê `TASK_AGENT_MAP.csv` + **Status do JSON local** (`board_status`).
2. Criadores só claimem cards com `board_status == Todo`.
3. Toda transição grava **JSON local** e **Project online** (`gh project item-edit` / `gh api graphql`).

```powershell
# Selecionar (dry)
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent backend --json

# Claim = In Progress (local + gh)
python docs/02-criacao-board/10-agents/scripts/agent_orchestrator.py --agent backend --claim --json

# Evento de workflow
python docs/02-criacao-board/10-agents/scripts/task_status_cli.py --task T-P05-001 --event open_pr --json
```

## Criadores (backend, frontend-*, cloud-infra, database, devops-cicd*, stores-release*)

| Momento | Status | Ação board |
|---------|--------|------------|
| Claim | **In Progress** | `claim_task_on_board` / orchestrator `--claim` |
| PR aberto | **Ready for Code Review** | `mark_task_in_review` |
| CR pediu mudanças | **In Progress** | aguardar `request_changes` |
| Correção enviada | **In Code Review** | `resubmit_after_review` |

\* devops-cicd e stores-release também atuam como **creator** nas tasks do seu papel.

## Revisores (*-reviewer)

| Momento | Status | Ação board |
|---------|--------|------------|
| Assume review | **In Code Review** | `start_code_review` |
| Aprovado | **Ready for Test** | `finalize_review_on_board --verdict approved` |
| Changes requested | **In Progress** | `finalize_review_on_board --verdict changes_requested` |

Fila: `board_status` ∈ `Ready for Code Review` \| `In Code Review`.

## QA (agent-qa)

| Momento | Status | Ação board |
|---------|--------|------------|
| Pega da fila | **In Test** | `start_qa_on_board` |
| Testes OK | **In Pull Request** | `complete_qa_pass_on_board` |
| Bug encontrado | **In Progress** + `type:bug` | `report_qa_bug_on_board` |

Trigger: `board_status == Ready for Test` (ou tasks com `agent_role=qa` ainda em **Todo**).

## DevOps / Stores-release (merge)

| Momento | Status | Ação board |
|---------|--------|------------|
| Merge queue | **In Pull Request** | (entrada automática após QA) |
| Merged | **Done** | `complete_merge_on_board` |

Trilha **stores** → owner merge = `stores-release`. Demais → `devops-cicd`.
 
## Eventos no Crew 
 
Toda transicao deve passar por evento (claim, open_pr, 	est_failed_bug, ...): 
 
1. list_idle_crew_agents - quem pode assumir 
2. esolve_agent_for_board_event / emit_status_event - chama o agente ocioso certo 
3. Se o agente estiver busy  dispatch_queue 
4. **3 bugs** na mesma task (	est_failed_bug)  **BLOCKER** com motivo + skill impactada (skills/{role}/SKILL.md) 
 
`powershell 
cd docs/02-criacao-board/10-agents/crew 
python main.py --mode events 
`
