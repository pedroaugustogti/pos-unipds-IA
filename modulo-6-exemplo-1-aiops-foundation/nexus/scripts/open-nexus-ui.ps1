# Abre Nexus UI (Streamlit) no host Windows (M13.4)
# Slides: minikube service nexus-ui

param(
    [switch]$MinikubeTunnel
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
. (Join-Path $PSScriptRoot "minikube-common.ps1")

Ensure-MinikubePath
. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure

$ready = kubectl get pods -l app=nexus-ui -o jsonpath='{.items[0].status.phase}' 2>$null
if ($ready -ne "Running") {
    throw "Pod nexus-ui nao esta Running. Rode: .\scripts\setup-nexus-ui.ps1"
}

Write-Host ""
Write-Host "Nexus UI - Streamlit no host (Windows)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Dentro do cluster:  http://nexus-ui:8501" -ForegroundColor DarkGray
Write-Host "  No host:            http://localhost:8501" -ForegroundColor White
Write-Host ""

if ($MinikubeTunnel) {
    Write-Host "Tunel minikube (slides134 - terminal aberto no driver docker):" -ForegroundColor Yellow
    minikube service nexus-ui
    exit 0
}

Write-Host "Port-forward: http://localhost:8501" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para encerrar." -ForegroundColor DarkGray
kubectl port-forward svc/nexus-ui 8501:8501
