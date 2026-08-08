# Modulo 13.4 - Streamlit UI no Minikube (slides134.md)
# Uso: .\scripts\setup-nexus-ui.ps1 [-SkipCluster] [-SkipBuild] [-SkipLocalstack]

param(
    [switch]$SkipCluster,
    [switch]$SkipBuild,
    [switch]$SkipLocalstack
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
. (Join-Path $PSScriptRoot "minikube-common.ps1")

Ensure-MinikubePath

Write-Host ""
Write-Host "Modulo 13.4 - Nexus UI (Streamlit)" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipCluster) {
    Write-Host "1/6 Garantindo cluster Minikube..." -ForegroundColor Yellow
    . (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure
    Start-MinikubeLite -MemoryMB 2048 -Cpus 2
} else {
    Write-Host "1/6 Cluster ignorado (-SkipCluster)" -ForegroundColor DarkGray
}

if (-not $SkipLocalstack) {
    Write-Host ""
    Write-Host "2/6 Garantindo LocalStack..." -ForegroundColor Yellow
  $lsPhase = kubectl get pods -l app=localstack -o jsonpath='{.items[0].status.phase}' 2>$null
    if ($lsPhase -ne "Running") {
        & (Join-Path $PSScriptRoot "setup-localstack.ps1") -SkipCluster -SmokeOnly
    } else {
        Write-Host "[OK] LocalStack ja em execucao." -ForegroundColor Green
    }
} else {
    Write-Host "2/6 LocalStack ignorado (-SkipLocalstack)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "3/6 Build da imagem nexus-bot:v1..." -ForegroundColor Yellow
if (-not $SkipBuild) {
    minikube docker-env --shell powershell | Invoke-Expression
    docker build -t nexus-bot:v1 .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Build no daemon do minikube falhou. Host Docker + image load..." -ForegroundColor Yellow
        Reset-DockerEnv
        docker build -t nexus-bot:v1 .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        minikube image load nexus-bot:v1
    }
    Reset-DockerEnv
} else {
    Write-Host "Build ignorado (-SkipBuild)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "4/6 Aplicando k8s/streamlit.yaml..." -ForegroundColor Yellow
kubectl apply -f k8s/streamlit.yaml

Write-Host ""
Write-Host "5/6 Aguardando pod nexus-ui..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    $phase = kubectl get pods -l app=nexus-ui -o jsonpath='{.items[0].status.phase}' 2>$null
    if ($phase -eq "Running") {
        kubectl wait --for=condition=ready pod -l app=nexus-ui --timeout=60s 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    }
    if ($phase -eq "Failed") { break }
    Start-Sleep -Seconds 3
}
kubectl get pods -l app=nexus-ui
if (-not $ready) {
    throw "Pod nexus-ui nao ficou Ready. Verifique: kubectl describe pod -l app=nexus-ui"
}

Write-Host ""
Write-Host "6/6 Smoke test (Streamlit health)..." -ForegroundColor Yellow
kubectl exec deployment/nexus-ui -- curl -sf http://localhost:8501/_stcore/health
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Health check falhou - UI pode estar iniciando. Tente: kubectl logs deployment/nexus-ui" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Streamlit respondendo." -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] Nexus UI pronto." -ForegroundColor Green
Write-Host ""
Write-Host "Abrir no browser (Windows):" -ForegroundColor Yellow
Write-Host "  .\scripts\open-nexus-ui.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Slides (tunel minikube):" -ForegroundColor Yellow
Write-Host "  .\scripts\open-nexus-ui.ps1 -MinikubeTunnel" -ForegroundColor White
Write-Host ""
