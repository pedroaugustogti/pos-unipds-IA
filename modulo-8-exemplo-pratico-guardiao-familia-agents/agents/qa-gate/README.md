# qa-gate

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


Gate de qualidade da pipeline — executa testes e evidências após review.

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do gate |
| `SKILL.md` | Procedimentos QA |
| `MOBILE_SETUP_EVIDENCE.md` | Setup emuladores/Appium |
| `scripts/` | CLIs evidência (ver README local) |

## Decisões

- **MCP:** `on_status_event` → `qa_validate` → `execute` — suites em `KNOWLEDGE.md`
- Não iniciar harness em Todo — responsabilidade do `qa-author` (`orchestrator_enter_in_progress`)
- Mobile child: **seed parent** (`basic_parent`/`parent_home`) → `qa_appium_suite_child(child_only=true)` → evidência → cleanup
- Mobile parent UI: sem seed → `qa_appium_suite_parent(feature=...)`
- Status: eventos role-based `qa-gate_in_test`, `qa-gate_in_pull_request`, `qa-gate_return_in_progress`