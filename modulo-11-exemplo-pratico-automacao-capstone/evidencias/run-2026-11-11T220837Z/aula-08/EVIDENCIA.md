# Evidência — Aula 8: pgvector, seed

- **Status:** `parcial`
- **Ferramenta (vídeo-aula):** Postgres + pgvector + Vertex embeddings
- **Timestamp UTC:** 2026-11-11T220837Z

## Checks

| Check | OK | Detalhe |
|-------|----|---------|
| clone full | ✅ | clonado |
| docker-compose pgvector | ✅ | extensão via image |
| slides 2.1a-c | ✅ | C:\Users\Pedro Augusto\Documents\pos-unipds-IA\modulo-11-exemplo-2-orquestracao-cognitiva\materiais_aula |
| CREATE EXTENSION vector | ❌ | failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if th |

## Notas

Extensão validada no container local quando possível; seed CVM/Vertex = etapa seguinte.

## Raw

```json
[
  {
    "nome": "clone full",
    "ok": true,
    "detalhe": "clonado",
    "cmd": [
      "git",
      "clone",
      "--depth",
      "1",
      "https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher.git",
      "C:\\Users\\Pedro Augusto\\Documents\\pos-unipds-IA\\modulo-11-exemplo-pratico-automacao-capstone\\workspace\\capstone-project-ai-researcher"
    ],
    "exit": 0,
    "stdout": "",
    "stderr": "Cloning into 'C:\\Users\\Pedro Augusto\\Documents\\pos-unipds-IA\\modulo-11-exemplo-pratico-automacao-capstone\\workspace\\capstone-project-ai-researcher'...\n"
  },
  {
    "nome": "CREATE EXTENSION vector",
    "ok": false,
    "detalhe": "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot f",
    "cmd": [
      "docker",
      "compose",
      "exec",
      "-T",
      "postgres",
      "psql",
      "-U",
      "postgres",
      "-d",
      "ai_researcher",
      "-c",
      "CREATE EXTENSION IF NOT EXISTS vector; SELECT extname FROM pg_extension WHERE extname='vector';"
    ],
    "exit": 1,
    "stdout": "",
    "stderr": "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.\n"
  }
]
```
