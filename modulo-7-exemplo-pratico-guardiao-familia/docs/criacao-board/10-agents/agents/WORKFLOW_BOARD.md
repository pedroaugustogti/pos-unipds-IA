# Workflow board — referência para todos os agentes

Cada `.agent.md` deve seguir esta matriz de **status GitHub Project #2**.

Doc completa: [`11-workflow/AGENT_BOARD_STAGES.md`](../../11-workflow/AGENT_BOARD_STAGES.md)

## Status (ordem)

`Todo` → `In Progress` → `Ready for Code Review` → `In Code Review` → `Ready for Test` → `In Test` → `In Pull Request` → `Done`

## Criadores (backend, frontend-*, cloud-infra, database, devops-cicd*, stores-release*)

| Momento | Status | Ação board |
|---------|--------|------------|
| Claim | **In Progress** | `claim_task_on_board` / orchestrator |
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

## QA (agent-qa)

| Momento | Status | Ação board |
|---------|--------|------------|
| Pega da fila | **In Test** | `start_qa_on_board` |
| Testes OK | **In Pull Request** | `complete_qa_pass_on_board` |
| Bug encontrado | **In Progress** + `type:bug` | `report_qa_bug_on_board` |

## DevOps / Stores-release (merge)

| Momento | Status | Ação board |
|---------|--------|------------|
| Merge queue | **In Pull Request** | (entrada automática após QA) |
| Merged | **Done** | `complete_merge_on_board` |

Trilha **stores** → owner merge = `stores-release`. Demais → `devops-cicd`.
