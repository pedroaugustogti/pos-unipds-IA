# Para o Minikube e restaura Docker Desktop (libera RAM/CPU)
# Uso: .\scripts\minikube-stop.ps1

. (Join-Path $PSScriptRoot "minikube-common.ps1")

Ensure-MinikubePath
Reset-DockerEnv

Write-Host "Parando minikube..." -ForegroundColor Yellow
$prev = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
minikube stop *> $null
minikube pause *> $null
$ErrorActionPreference = $prev

Reset-DockerEnv
Write-Host "[OK] Minikube parado. Docker Desktop restaurado." -ForegroundColor Green
Write-Host "Para reabrir o dashboard: .\scripts\minikube-dashboard-lite.ps1" -ForegroundColor DarkGray
