# Módulo 13.1 — build local (slides131.md)
# Uso: .\scripts\docker-build.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ""
Write-Host "Construindo nexus-bot:v1 (python:3.12-slim)..." -ForegroundColor Cyan
Write-Host ""
docker build -t nexus-bot:v1 .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Imagem pronta: nexus-bot:v1`n" -ForegroundColor Green
    Write-Host "Execute com:" -ForegroundColor Yellow
    Write-Host '  .\scripts\docker-run.ps1' -ForegroundColor White
    Write-Host '  # ou: docker run --rm -e GROQ_API_KEY="gsk_..." nexus-bot:v1' -ForegroundColor DarkGray
}
