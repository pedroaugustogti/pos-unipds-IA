# Template de issue — Agent Task (Guardião Família)

Referência canônica: [issue #103 T-P3-009](https://github.com/guardiaofamilia/guardiao-familia-child/issues/103)  
Gerador automático: `board_automation/board/issue_task_body.py` · enrichment P3: `board_automation/data/imports/PROJECT3_REFINEMENT_EXTRA.json`

Título: **`[T-XXX-NNN] Título curto`** (obrigatório para `board_client.find_issue_number`).

**Regra GitHub:** não referenciar arquivos `.md` locais no corpo da issue (404 no repo de produto). Todo conteúdo necessário vai **inline** ou nos **Anexos A–E**.

Formulário interativo: `board_automation/templates/.github/ISSUE_TEMPLATE/agent-task.yml`

---

## Estrutura do corpo (secções 0–10 + anexos)

| Secção | Conteúdo |
|--------|----------|
| **0** | Tabela Fase · Status · Agente · **Responsabilidade** · Proibido |
| **0.1** | `agent_responsibilities` por papel (opcional, recomendado) |
| **1** | Identificação (task, roles, repo, branch, depends_on) |
| **2** | Estado antes/depois + contexto + user story |
| **2.1** | User flow mobile *(obrigatório se `frontend-mobile`)* |
| **3** | Escopo rígido + redirecionamento |
| **4** | Passo a passo creator + checklist pré-PR (`{creator}_ready_for_code_review`) |
| **5** | AC + tabela de verificação |
| **6** | QA qa-gate (suite, MCP mobile se aplicável, db_seed) |
| **7** | Parar e pedir ajuda (anti-alucinação) |
| **8** | Handoff / eventos board |
| **9** | Payload `agent-task` JSON |
| **10** | Templates de comentário por fase |
| **Anexos A–E** | Fluxo board, papéis, qa-gate, template PR *(inline, sem links)* |

---

## 0. Quem faz o quê

| Fase | Board Status | Agente | Responsabilidade | Proibido nesta fase |
|------|--------------|--------|------------------|---------------------|
| Dispatch | Todo → In Progress | **{creator}** | Branch, escopo sec. 3, testes | Review próprio código |
| Implementar | In Progress | **{creator}** | Diff no escopo + AC locais | Merge, QA E2E, fora do escopo |
| Review | In Code Review | **{reviewer}** | `{reviewer}_ready_for_test` / `{reviewer}_return_in_progress` | Implementar, rodar QA gate |
| QA | In Test | **qa-gate** | Suite sec. 6 + evidências (+ MCP se mobile) | Merge PR, alterar código |
| Merge | In Pull Request | **{merge_owner}** | `{merge_owner}_done` após HITL | Alterar código |

Fluxo board: **Anexo A** e sec. 8.

---

## 2.1 Fluxo do usuário *(frontend-mobile)*

Campos obrigatórios em `refinement.user_flow`:

`app` · `entry_point` · `preconditions` · `steps[]` · `target_screen` · `target_element` · `emulator` · `metro_port` · `qa_repro_steps[]`

Creator valida no emulador manualmente; **qa-gate** reproduz via **MCP** (sec. 2.1 → `Reproduzir (QA / Appium)` + sec. 6).

### Reproduzir (QA / Appium) — sempre MCP

- Servidor: `guardiao-familia-agents` (`list_mcp_tools`)
- Sequência: `get_handoff` → `qa-gate_in_test` → `query_mobile_flow_rag` → `qa_db_seed` → `qa_appium_suite_*` → evidências → `qa_db_cleanup` → `qa-gate_in_pull_request`|`qa-gate_return_in_progress`
- `qa_repro_steps[]` = cenários a validar **após** a suite MCP (não comandos CLI — stack/seed/Appium/evidências são tools MCP)
- Fallback CLI (`qa_mobile_evidence.py`) somente se MCP indisponível

---

## 6. QA (qa-gate)

| Campo | Exemplo |
|-------|---------|
| test_suite | `qa-mobile-child-appium` — Appium no app child (seed parent no DB; `child_only=true`) |
| Cenários | IDs ou slugs (`greeting-morning-08h`, …) |
| Evidências | `screenshot_png`, `video_mp4`, `json_report` |
| MCP | `guardiao-familia-agents` quando mobile |

### Mobile com `qa.db_seed` (child-only)

Sequência MCP (8 passos): `get_handoff` → `qa-gate_in_test` → `query_mobile_flow_rag` → `qa_db_seed(profile=basic_parent)` → `qa_appium_suite_child(from_db_seed=true, child_only=true)` → evidências → `qa_db_cleanup` → `qa-gate_in_pull_request`|`qa-gate_return_in_progress`

Profiles seed: `basic_parent` · `parent_home` · `child_home` · `permissions_resume` · `pairing_warm` (dual)

---

## 7. Parar e pedir ajuda (anti-alucinação)

Regras em `refinement.stop_and_redirect` — exemplos:

- Dependência não Done → não codar
- Escopo fora do ticket → redirecionar (sec. 3)
- Precisar alterar pairing parent / API health → outra task

---

## 9. Payload `agent-task`

```agent-task
{
  "task_id": "T-XXX-NNN",
  "title": "",
  "agent_role": "backend",
  "track": "produto",
  "repo": "guardiao-familia-api",
  "refinement": {
    "context_summary": "",
    "user_story": "",
    "suggested_files": [],
    "in_scope": [],
    "out_of_scope": [],
    "acceptance_hints": [],
    "ac_verification": [],
    "stop_and_redirect": [],
    "user_flow": {}
  },
  "qa": {
    "test_suite": "qa-custom",
    "scenarios": [],
    "evidence": { "screenshot_png": false, "video_mp4": false, "json_report": true },
    "db_seed": { "enabled": false },
    "how_to_run": ""
  },
  "agent_responsibilities": {},
  "handoff_expectations": {
    "creator_exit_event": "backend_ready_for_code_review",
    "reviewer_exit_event": "backend-reviewer_ready_for_test",
    "qa_exit_event": "qa-gate_in_pull_request",
    "merge_owner": "devops-cicd",
    "merge_exit_event": "devops-cicd_done"
  }
}
```

---

## 10. Comentários obrigatórios por agente (sec. 10)

Cada fase exige comentário na issue usando o template inline da sec. 10:

| Agente | Secção | Obrigatório no comentário |
|--------|--------|---------------------------|
| **frontend-mobile** | 10.1 | Estratégia de codificação · arquivos alterados · testes unitários (`npm test`) · handoff `{creator}_ready_for_code_review` |
| **frontend-mobile-reviewer** | 10.2 | Avaliação da implementação · qualidade de código · cobertura de testes · eventos reviewer v2 |
| **qa-gate** | 10.3 | Cenários de teste · critérios de aceite (tabela) · comandos MCP · mídias PNG/MP4/JSON anexadas |
| **devops-cicd** | 10.4 | PR merged · CI green · `devops-cicd_done` |

Preencher `agent_responsibilities` no backlog (sec. 0.1) para detalhar o escopo de cada papel na task.

---

## Anexos (gerados automaticamente)

| Anexo | Conteúdo |
|-------|----------|
| **A** | Tabela completa de eventos board |
| **B** | Resumo papel creator |
| **C** | Resumo papel reviewer |
| **D** | Resumo qa-gate (+ evidências mobile se aplicável) |
| **E** | Template PR antes de `{creator}_ready_for_code_review` |

---

## Sincronização com `TASK_AGENT_MAP.csv`

Ao criar issue manualmente, garantir linha no CSV e merge de `refinement` / `qa` em `load_tasks()`.

```powershell
python board_automation/scripts/seeds/patch_project3_issues.py --task T-P3-009 --dry-run
```
