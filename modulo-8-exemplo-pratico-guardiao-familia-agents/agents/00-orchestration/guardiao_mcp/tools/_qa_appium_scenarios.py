"""Fragmento de prompt compartilhado entre suites Appium parent/child."""

QA_APPIUM_SCENARIOS = """\
## Como escolher seed + suite

| Objetivo | Seed? | Tool | Flags |
|----------|-------|------|-------|
| Cadastro/família **na UI parent** | Não | `qa_appium_suite_parent` | `feature=create_account` ou `config_family` |
| Login→home com massa no DB | Sim `parent_home` | `qa_appium_suite_parent` | `from_db_seed=true`, `task_id` |
| AC no **app child** | Sim `basic_parent`/`parent_home` | `qa_appium_suite_child` | `from_db_seed=true`, **`child_only=true`** |
| Pairing dual | Sim `child_home` | `qa_appium_suite_child` | `child_only=false`, `feature=pairing` |
| Child pareado (permissões+home) | Sim `permissions_resume` | `qa_appium_suite_child` | `from_db_seed=true` |

**Infra:** parent=5554/8082 · child=5556/9090 · `phase=All` · `reset_handoff_after=true` (padrão com seed).
**Evidências:** `output/{task_id}/qa-gate-({N})/evidence/` · cite paths no `emit_status_event` role-based.
**Cleanup:** `qa_db_cleanup(task_id)` antes de outro ticket.
"""
