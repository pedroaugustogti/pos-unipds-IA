# Modulo 13.3 - LocalStack no Minikube (slides133.md)
# Uso: .\scripts\setup-localstack.ps1 [-SkipCluster] [-SmokeOnly]

param(
    [switch]$SkipCluster,
    [switch]$SmokeOnly
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
. (Join-Path $PSScriptRoot "minikube-common.ps1")

Ensure-MinikubePath

Write-Host ""
Write-Host "Modulo 13.3 - LocalStack (cloud simulada)" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipCluster) {
    Write-Host "1/5 Garantindo cluster Minikube..." -ForegroundColor Yellow
    . (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure
    Start-MinikubeLite -MemoryMB 2048 -Cpus 2
} else {
    Write-Host "1/5 Cluster ignorado (-SkipCluster)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "2/5 Garantindo imagem localstack/localstack:3.0 no cluster..." -ForegroundColor Yellow
docker image inspect localstack/localstack:3.0 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    docker pull localstack/localstack:3.0
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
minikube image load localstack/localstack:3.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "3/5 Aplicando k8s/localstack.yaml..." -ForegroundColor Yellow
kubectl apply -f k8s/localstack.yaml

Write-Host ""
Write-Host "4/5 Aguardando pod localstack..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    $phase = kubectl get pods -l app=localstack -o jsonpath='{.items[0].status.phase}' 2>$null
    if ($phase -eq "Running") {
        kubectl wait --for=condition=ready pod -l app=localstack --timeout=30s 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    }
    if ($phase -eq "Failed" -or $phase -eq "Unknown") { break }
    Start-Sleep -Seconds 3
}
kubectl get pods -l app=localstack
if (-not $ready) {
    throw "Pod localstack nao ficou Ready. Verifique: kubectl describe pod -l app=localstack"
}

Write-Host ""
Write-Host "5/5 Smoke test S3 (awslocal)..." -ForegroundColor Yellow
kubectl exec deployment/localstack -- awslocal s3 ls
kubectl exec deployment/localstack -- awslocal s3 mb s3://nexus-logs
kubectl exec deployment/localstack -- sh -c "echo 'Relatorio Nexus v2' > teste.txt && awslocal s3 cp teste.txt s3://nexus-logs/teste.txt"
kubectl exec deployment/localstack -- awslocal s3 ls s3://nexus-logs/

Write-Host ""
Write-Host "[OK] LocalStack pronto." -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Dentro do cluster (Pods):  http://localstack:4566" -ForegroundColor White
Write-Host "  No host (Windows/browser): .\scripts\open-localstack.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "  kubectl get pods -l app=localstack" -ForegroundColor White
Write-Host "  kubectl exec -it deployment/localstack -- awslocal s3 ls" -ForegroundColor White
Write-Host "  kubectl exec deployment/localstack -- awslocal sqs list-queues" -ForegroundColor White
Write-Host ""

if ($SmokeOnly) { exit 0 }
