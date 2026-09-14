# mobile — QA Appium e evidências MCP

Orquestração canônica do gate mobile: tool MCP **`qa_validate`** (`lib/orchestrator/phase_qa_validate.py`) → **`qa_scenario_chain`** → por item em `ticket.qa.scenarios`:

```
qa_init_suite_mobile → qa_pipeline_evidence → qa_generate_evidence
```

Massa API (`qa.db_seed`) e `qa_db_cleanup` rodam **dentro** de `qa_generate_evidence` quando o ticket pede — não são tools separadas no gate.

## Fluxo qa-gate (manual ou LangGraph)

```
on_status_event(task_id, agent_role=qa-gate, board_status=In Test)
→ hitl_guard_actuation (live)
→ qa_validate(actuation_context, mode=live, worker_mode=local|docker)
→ execute_agent_actuation_tool (qa-gate_in_pull_request | qa-gate_return_in_progress)
```

Script de referência: `agents/00-runtime/system/observability/run_tp3010_qa_validate.py`

## Por etapa

| Etapa | Módulo / tool MCP | Função |
|-------|-------------------|--------|
| Init | `qa_init_suite_mobile.py` | Wave A: api ∥ adb ∥ emulator → Wave B: metro ∥ apk → Appium; recovery até 3×/check; `apps_ready_ok` |
| Metro | `metro_bundle_state.py` | Fingerprint git do repo (screens, App.tsx, …) vs último bundle servido; stale → reinicia Metro e grava estado em `agents/00-runtime/system/mobile/metro_bundle_state.json` |
| Pipeline | `qa_pipeline_evidence.py` | `scenario_pipeline` + `device.launch` (se Metro refrescou ou repo dirty → `reload_mode=hard`) |
| Evidência | `qa_generate_evidence.py` | Seed, Appium, PNG/MP4 por cenário |
| Orquestração | `qa_scenario_chain.py` | Encadeia as três tools; usado por `qa_validate` |

## Artefatos

| Tipo | Path |
|------|------|
| Evidência | `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/{scenario}/` |
| Status cenário | `.../qa-gate-({N})/status/{scenario}.json` |
| Log init | `agents/00-runtime/system/observability/qa_init_suite_mobile.jsonl` |

## Outros módulos

| Módulo | Função |
|--------|--------|
| `qa_appium_runtime_script.py` | Gera/executa script Appium a partir do pipeline |
| `mobile_runtime_config.py` | Ports Metro, emuladores, bundle ids parent/child |
| `mobile_flow_rag.py` | RAG de fluxos (lib; não exposto como tool MCP) |
| `mobile_flow_discovery.py` | Discovery 0→N para ingest |
| `qa_mobile_mcp.py` | Caminho legado ensure+suite (fallback interno — **não** documentar no gate) |
| `local_e2e.py` | Bootstrap API / paths locais |
| `scenario_evidence.py` | Helpers de captura |

Guias estáticos: `agents/00-runtime/system/mobile/guides/`.

Docs de papel: [`agents/01-role-based/qa-gate/MOBILE_SETUP_EVIDENCE.md`](../../agents/01-role-based/qa-gate/MOBILE_SETUP_EVIDENCE.md) · MCP: [`agents/00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../agents/00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md)
