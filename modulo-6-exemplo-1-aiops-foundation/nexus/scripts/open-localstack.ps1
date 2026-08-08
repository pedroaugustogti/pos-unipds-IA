# Abre LocalStack no host Windows (M13.3)
# O hostname "localstack" so existe DENTRO do cluster K8s (CoreDNS).
# No host use localhost via port-forward ou minikube service.

param(
    [switch]$MinikubeTunnel
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
. (Join-Path $PSScriptRoot "minikube-common.ps1")

Ensure-MinikubePath
. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure

$ready = kubectl get pods -l app=localstack -o jsonpath='{.items[0].status.phase}' 2>$null
if ($ready -ne "Running") {
    throw "Pod localstack nao esta Running. Rode: .\scripts\setup-localstack.ps1"
}

Write-Host ""
Write-Host "LocalStack — acesso do HOST (Windows)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  DENTRO do cluster (Pods):  http://localstack:4566" -ForegroundColor DarkGray
Write-Host "  NO HOST (browser/curl):    http://localhost:4566" -ForegroundColor White
Write-Host ""

if ($MinikubeTunnel) {
    Write-Host "Tunel minikube (terminal precisa ficar aberto no driver docker):" -ForegroundColor Yellow
    minikube service localstack
    exit 0
}

Write-Host "Port-forward ativo: http://localhost:4566" -ForegroundColor Green
Write-Host "Health: curl.exe http://localhost:4566/_localstack/health" -ForegroundColor DarkGray
Write-Host "Pressione Ctrl+C para encerrar." -ForegroundColor DarkGray
kubectl port-forward svc/localstack 4566:4566
