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
- Mobile: seed DB → Appium → evidência → cleanup
- Status: `start_test`, `test_passed`, `test_failed_bug` via gateway