# qa-gate

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

Gate de qualidade da pipeline — executa testes e evidências após review.

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do gate |
| `SKILL.md` | Procedimentos QA |
| `MOBILE_SETUP_EVIDENCE.md` | Setup emuladores/Appium + fluxo MCP |
| `scripts/` | CLIs evidência (ver README local) |

## Fluxo MCP (In Test)

```
on_status_event → hitl_guard_actuation → qa_validate(mode=live) → execute_agent_actuation_tool
```

**`qa_validate`** resolve `ticket.qa.scenarios` e, **por cenário**, executa:

1. **`qa_init_suite_mobile`** — `apps_ready_ok` (stack + Metro + APK + Appium)
2. **`qa_pipeline_evidence`** — pipeline Appium + `device` (launch/reload)
3. **`qa_generate_evidence`** — seed (se ticket), fluxo, PNG/MP4

`worker_mode`: `local` (host) ou `docker` (1 container/cenário). **PASS** só se todos os cenários `ok=true`.

## Metro e código atualizado

- Check **metro**: HTTP `/status` **e** fingerprint do repo (`lib/mobile/metro_bundle_state.py`).
- Bundle **stale** (sem registro ou git dirty) → init reinicia Metro e grava fingerprint.
- Pipeline aplica **`reload_mode=hard`** no launch quando Metro foi refrescado ou há alterações locais no app — evita PNG com JS antigo no emulador.

## Decisões

- Não iniciar harness em Todo — responsabilidade do `qa-author` (`orchestrator_enter_in_progress`)
- Massa (`qa.db_seed`) e cleanup vêm do ticket; inferidos em `qa_generate_evidence`
- Evidências: `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/{scenario}/`
- Status: `qa-gate_in_test`, `qa-gate_in_pull_request`, `qa-gate_return_in_progress`
- Não rodar `fast-stack.ps1` nem `qa_appium_suite_*` fora do envelope `qa_validate`

## Ver também

- [`../../../lib/mobile/README.md`](../../../lib/mobile/README.md) — mapa de módulos Python
- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
