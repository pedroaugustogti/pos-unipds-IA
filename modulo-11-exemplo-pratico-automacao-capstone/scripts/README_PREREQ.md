# Scripts — eliminar pré-requisitos

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone

# Instalações pendentes (pnpm11, firebase, uv, playwright, vector, sql-proxy)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_pending.ps1
# uv PATH (nova sessão):
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

# Orquestrador (P1 → P6 → P3 → P5-AR → P4 → P9)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_prereq_plan.ps1 -Until P6

# Stack local (precisa Docker Desktop ligado)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_prereq_plan.ps1 -Until P4 -DemoOnly

# Cloud SQL (custo — HITL explícito)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\gcp_fundacao.ps1 -Phase sql -ConfirmSql
```

| Script | Fase |
|--------|------|
| `bootstrap_local.ps1` | P1 |
| `check_env_keys.ps1` | P6 |
| `setup_mcp_skills.ps1` | P3 |
| `gcp_fundacao.ps1` | P5 |
| `up_local.ps1` | P4 |
| `run_prereq_plan.ps1` | orquestra |
| `gcloud_env.ps1` | SSL/auth helper |

Estado: `evidencias/preflight/state.json`
