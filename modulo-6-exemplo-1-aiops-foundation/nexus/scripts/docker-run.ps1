# Módulo 13.1 — execução local (slides131.md)
# Uso: .\scripts\docker-run.ps1
# Requer GROQ_API_KEY no ambiente ou em nexus/.env

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $Root ".env"

if (-not $env:GROQ_API_KEY -and (Test-Path $EnvFile)) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*GROQ_API_KEY\s*=\s*(.+)\s*$') {
            $env:GROQ_API_KEY = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
}

if (-not $env:GROQ_API_KEY) {
    Write-Host "❌ Defina GROQ_API_KEY no .env ou no ambiente antes de rodar." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Executando nexus-bot:v1 (Lab 12 - Game Day)..." -ForegroundColor Cyan
Write-Host ""
docker run --rm `
    -e GROQ_API_KEY="$env:GROQ_API_KEY" `
    -e CREWAI_TRACING_ENABLED=false `
    -e NEXUS_IN_DOCKER=1 `
    -e NEXUS_SSL_INSECURE=1 `
    -e NEXUS_GROQ_RETRY_ATTEMPTS=5 `
    -e NEXUS_GROQ_RETRY_DELAY_SECONDS=45 `
    -e NEXUS_AGENT_MAX_ITER=2 `
    nexus-bot:v1
