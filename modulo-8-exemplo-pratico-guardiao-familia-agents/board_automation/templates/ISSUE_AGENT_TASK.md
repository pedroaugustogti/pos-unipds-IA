# Template de issue — Agent Task (enxuto)

Gerador: `board_automation/board/issue_task_body.py`  
Formulário: `board_automation/templates/.github/ISSUE_TEMPLATE/agent-task.yml`

Título: **`[T-XXX-NNN] Título curto`**

---

## Estrutura do corpo

| Bloco | Público | Conteúdo |
|-------|---------|----------|
| **Meta** | Orquestração | task_id, roles, repo, branch, eventos de saída |
| **Refinamento** | Todos | contexto, user story, estado antes/depois, escopo, notas técnicas |
| **Implementação — `{creator}`** | Creator | responsabilidades, branch, passos, arquivos sugeridos |
| **QA — `qa-gate`** | QA | cenários, AC, verificação, evidências, user flow mobile |
| **Review — `{reviewer}`** | Reviewer | foco em diff/PR — sem implementação nem QA |
| **Payload `agent-task`** | Parsers | JSON completo para `enrich_task_ticket` |

Sem anexos A–E, templates de comentário sec. 10 ou tabelas MCP duplicadas no refinamento.

---

## Slice por agente (`on_status_event`)

| Agente | Campos em `ticket_slice` |
|--------|--------------------------|
| **creator** | refinamento + `implementation_steps` + `suggested_files` + handoff |
| **reviewer** | `review_focus` (AC, arquivos, state_before/after) |
| **qa-gate** | `qa` (scenarios, evidence, db_seed) + AC + `user_flow` mobile |

---

## Payload `agent-task`

```agent-task
{
  "task_id": "T-XXX-NNN",
  "agent_role": "frontend-mobile",
  "refinement": { "context_summary": "", "in_scope": [], "implementation_steps": [] },
  "qa": { "scenarios": [], "evidence": {}, "how_to_run": "" },
  "handoff_expectations": {}
}
```

---

## Sincronizar issue existente

```powershell
python board_automation/scripts/seeds/patch_project3_issues.py --task T-P3-009
```

Recriar issue (novo número):

```powershell
python board_automation/scripts/seeds/seed_project3_sandbox.py --task T-P3-009 --force
```
