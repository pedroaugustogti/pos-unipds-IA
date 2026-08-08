# Libera RAM para Minikube Dashboard (Windows + Docker Desktop/WSL2)
# Uso: .\scripts\optimize-docker-for-minikube.ps1 [-MemoryGB 4] [-ApplyWslShutdown]

param(
    [int]$MemoryGB = 4,
    [switch]$ApplyWslShutdown
)

$ErrorActionPreference = "Continue"
. (Join-Path $PSScriptRoot "minikube-common.ps1")

Write-Host ""
Write-Host "=== Otimizacao de memoria para Minikube Dashboard ===" -ForegroundColor Cyan
Write-Host ""

# 1) Parar clusters K8s redundantes (k3d compete com minikube)
Write-Host "[1/5] Parando containers k3d (cluster paralelo ao minikube)..." -ForegroundColor Yellow
$k3d = docker ps -q --filter "name=k3d-nexus-lab" 2>$null
if ($k3d) {
    docker stop $k3d 2>$null | Out-Null
    Write-Host "  Parados: k3d-nexus-lab" -ForegroundColor Green
} else {
    Write-Host "  Nenhum container k3d ativo." -ForegroundColor DarkGray
}

# 2) Remover containers parados (grafana, nodejs labs antigos)
Write-Host "[2/5] Removendo containers parados..." -ForegroundColor Yellow
$exited = docker ps -aq --filter "status=exited" 2>$null
if ($exited) {
    docker rm $exited 2>$null | Out-Null
    Write-Host "  Removidos containers exited." -ForegroundColor Green
} else {
    Write-Host "  Nenhum container parado." -ForegroundColor DarkGray
}

# 3) Limpar cache de build Docker (disco + pressao no daemon)
Write-Host "[3/5] Limpando build cache Docker..." -ForegroundColor Yellow
docker builder prune -f 2>$null | Out-Null
Write-Host "  Build cache limpo." -ForegroundColor Green

# 4) Atualizar .wslconfig (limite de RAM do Docker Desktop)
Write-Host "[4/5] Atualizando $env:USERPROFILE\.wslconfig para ${MemoryGB}GB..." -ForegroundColor Yellow
$wslConfig = @"
[wsl2]
# Ajustado para Minikube Dashboard (modulo 13.2)
memory=${MemoryGB}GB
processors=4
swap=2GB
localhostForwarding=true
"@
Set-Content -Path "$env:USERPROFILE\.wslconfig" -Value $wslConfig -Encoding utf8
Write-Host "  .wslconfig atualizado: memory=${MemoryGB}GB, processors=4" -ForegroundColor Green

# 5) Reiniciar WSL para aplicar novo limite
Write-Host "[5/5] Reiniciando WSL para aplicar nova memoria..." -ForegroundColor Yellow
if ($ApplyWslShutdown) {
    wsl --shutdown 2>$null | Out-Null
    Start-Sleep -Seconds 3
    Write-Host "  WSL reiniciado. Abra o Docker Desktop e aguarde ficar Ready." -ForegroundColor Green
} else {
    Write-Host "  Execute manualmente (fecha Docker brevemente):" -ForegroundColor Yellow
    Write-Host "    wsl --shutdown" -ForegroundColor White
    Write-Host "  Depois reabra o Docker Desktop." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Proximo passo apos Docker Ready:" -ForegroundColor Cyan
Write-Host "  .\scripts\minikube-dashboard-lite.ps1 -Recreate" -ForegroundColor White
Write-Host ""
