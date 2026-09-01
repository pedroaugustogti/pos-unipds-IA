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

- Não claimar harness em Todo (`qa-author`)
- Mobile child: **seed parent** (`basic_parent`/`parent_home`) → `qa_appium_suite_child(child_only=true)` → evidência → cleanup
- Mobile parent UI: sem seed → `qa_appium_suite_parent(feature=...)`
- Status: `start_test`, `test_passed`, `test_failed_bug` via gateway