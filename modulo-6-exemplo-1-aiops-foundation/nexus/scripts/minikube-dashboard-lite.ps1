# Dashboard Minikube otimizado (baixo consumo de RAM/CPU no Windows)
# Uso:
#   .\scripts\minikube-dashboard-lite.ps1           # abre dashboard
#   .\scripts\minikube-dashboard-lite.ps1 -StopOnExit  # para cluster ao sair (Ctrl+C)
#   .\scripts\minikube-dashboard-lite.ps1 -MemoryMB 1536 -Cpus 1  # maquina fraca

param(
    [int]$MemoryMB = 1800,
    [int]$Cpus = 2,
    [switch]$StopOnExit,
    [switch]$UrlOnly,
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "minikube-common.ps1")
. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure

Ensure-MinikubePath
Start-MinikubeLite -MemoryMB $MemoryMB -Cpus $Cpus -Recreate:$Recreate

Write-Host ""
Write-Host "Abrindo Kubernetes Dashboard (sem metrics-server)..." -ForegroundColor Cyan
Write-Host "Dica: ao terminar, rode .\scripts\minikube-stop.ps1 para liberar RAM." -ForegroundColor DarkGray
Write-Host ""

try {
    if ($UrlOnly) {
        minikube dashboard --url
    } else {
        # Abre o navegador; mantem proxy ativo ate Ctrl+C
        minikube dashboard
    }
} finally {
    if ($StopOnExit) {
        Write-Host ""
        Write-Host "Parando minikube para liberar memoria..." -ForegroundColor Yellow
        minikube stop
        Reset-DockerEnv
        Write-Host "[OK] Cluster parado." -ForegroundColor Green
    }
}
