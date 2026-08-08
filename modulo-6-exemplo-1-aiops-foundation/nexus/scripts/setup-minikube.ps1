# Modulo 13.2 - Minikube local (slides132.md)
# Uso: .\scripts\setup-minikube.ps1 [-SkipBuild] [-JobOnly] [-SmokeTest]

param(
    [switch]$SkipBuild,
    [switch]$JobOnly,
    [switch]$SmokeTest
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
. (Join-Path $PSScriptRoot "minikube-common.ps1")

function Apply-NexusSecret {
    $envFile = Join-Path $Root ".env"
    if (-not (Test-Path $envFile)) {
        throw "Arquivo .env nao encontrado em $Root"
    }
    kubectl create secret generic nexus-secrets `
        --from-env-file=$envFile `
        --dry-run=client -o yaml | kubectl apply -f -
    Write-Host "[OK] Secret nexus-secrets aplicado via kubectl (sem arquivo em disco)" -ForegroundColor Green
}

Ensure-MinikubePath

Write-Host ""
Write-Host "Modulo 13.2 - Minikube + Nexus-Bot" -ForegroundColor Cyan
Write-Host ""

Write-Host "1/5 Iniciando cluster (driver=docker, 2048MB)..." -ForegroundColor Yellow
. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure
Start-MinikubeLite -MemoryMB 2048 -Cpus 2

Write-Host ""
Write-Host "2/5 Build da imagem..." -ForegroundColor Yellow
if (-not $SkipBuild) {
    minikube docker-env --shell powershell | Invoke-Expression
    docker build -t nexus-bot:v1 .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Build no daemon do minikube falhou (TLS). Host Docker + image load..." -ForegroundColor Yellow
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
Write-Host "3/5 Aplicando Secret K8s..." -ForegroundColor Yellow
Apply-NexusSecret

Write-Host ""
Write-Host "4/5 Aplicando manifestos..." -ForegroundColor Yellow
if ($SmokeTest) {
    kubectl delete job nexus-bot-smoke --ignore-not-found
    kubectl apply -f k8s/job-smoke.yaml
} elseif ($JobOnly) {
    kubectl delete job nexus-bot-run --ignore-not-found
    kubectl apply -f k8s/job.yaml
} else {
    kubectl apply -f k8s/deploy.yml
    kubectl delete job nexus-bot-run --ignore-not-found
    kubectl apply -f k8s/job.yaml
}

Write-Host ""
Write-Host "5/5 Status..." -ForegroundColor Yellow
kubectl get pods,jobs

Write-Host ""
Write-Host "[OK] Cluster pronto." -ForegroundColor Green
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "  kubectl get pods" -ForegroundColor White
Write-Host "  kubectl logs -f job/nexus-bot-run" -ForegroundColor White
Write-Host "  kubectl logs job/nexus-bot-smoke" -ForegroundColor White
Write-Host "  .\scripts\minikube-dashboard-lite.ps1" -ForegroundColor White
Write-Host "  .\scripts\minikube-stop.ps1" -ForegroundColor White
Write-Host ""
