# QA Scenario Worker (Docker full-stack)

Imagem por cenário: emulador Android + Appium + Python worker (`lib.mobile.qa_scenario_worker`).

## Requisitos

- Docker Desktop (Windows) com **WSL2** e suporte a **KVM** no distro Linux, **ou** Linux host com `/dev/kvm`
- Sem KVM o orquestrador retorna `DOCKER_KVM_UNAVAILABLE` (exceto spawn no Windows, onde o check de KVM fica a cargo do runtime WSL)

## Build

```bash
cd modulo-8-exemplo-pratico-guardiao-familia-agents
docker build -t guardiao-qa-scenario-worker:latest -f docker/qa-scenario-worker/Dockerfile .
```

## Run (manual)

```bash
docker run --rm --privileged --device /dev/kvm \
  -v "$PWD:/workspace:ro" \
  -v "$PWD/agents/00-runtime/output/T-P3-009/qa-gate-(1)/status:/status" \
  -v "$PWD/agents/00-runtime/output/T-P3-009/qa-gate-(1)/evidence/greeting-morning-08h:/evidence" \
  -v "$PWD/agents/00-runtime/output/T-P3-009/qa-gate-(1)/scenarios:/ctx:ro" \
  -e GF_TASK_ID=T-P3-009 \
  -e GF_SCENARIO_ID=greeting-morning-08h \
  -e GF_ACTUATION_CONTEXT_PATH=/ctx/actuation_context.json \
  -e GF_STATUS_DIR=/status \
  -e GF_SUITES_MOBILE_JSON='{"parent":false,"child":true}' \
  -e PYTHONPATH=/workspace \
  guardiao-qa-scenario-worker:latest
```

## Orquestração

`qa_validate` → `run_scenario_orchestrator`:

| Env | Default | Efeito |
|-----|---------|--------|
| `GF_QA_SCENARIO_WORKER` | `local` | `docker` para fan-out em containers |
| `GF_QA_SCENARIO_IMAGE` | `guardiao-qa-scenario-worker:latest` | imagem |
| `GF_QA_SCENARIO_MAX_PARALLEL` | N cenários | paralelismo |

Status por cenário: `status/{scenario_id}.json` (`phase=done`, `ok`, `blocking_reason`).

Gate: **PASS somente se todos** os cenários `ok=true`.
