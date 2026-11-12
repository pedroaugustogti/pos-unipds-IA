# Evidência — Aula 7: Walking Skeleton e Deploy Zero

- **Status:** `parcial`
- **Ferramenta (vídeo-aula):** Docker + Actions + Cloud Run/Firebase
- **Timestamp UTC:** 2026-11-11T220837Z

## Checks

| Check | OK | Detalhe |
|-------|----|---------|
| apps/api | ✅ | API Fastify |
| apps/web | ✅ | Angular |
| capstone:check script | ✅ | validação pós-deploy |
| docker CLI | ✅ | presente |
| docker compose up postgres | ❌ | pgvector local |
| compose ps | ❌ |  |

## Notas

Postgres local via compose quando Docker disponível; deploy cloud = HITL/Actions.

## Raw

```json
[
  {
    "nome": "docker compose up postgres",
    "ok": false,
    "detalhe": "pgvector local",
    "cmd": [
      "docker",
      "compose",
      "up",
      "-d",
      "postgres"
    ],
    "exit": 1,
    "stdout": "",
    "stderr": "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.\n"
  },
  {
    "nome": "compose ps",
    "ok": false,
    "detalhe": "",
    "cmd": [
      "docker",
      "compose",
      "ps"
    ],
    "exit": 1,
    "stdout": "",
    "stderr": "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.\n"
  }
]
```
