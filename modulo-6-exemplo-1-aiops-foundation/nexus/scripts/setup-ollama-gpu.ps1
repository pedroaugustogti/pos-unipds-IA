# Modulo 13.5 - Ollama offline com GPU (slides135.md)
# Modelo leve llama3.2:3b + RTX 4050 via Docker --gpus all
# Uso: .\scripts\setup-ollama-gpu.ps1 [-Model llama3.2:3b] [-SkipPull]

param(
    [string]$Model = "llama3.2:3b",
    [switch]$SkipPull
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ContainerName = "nexus-ollama-gpu"
$VolumeName = "nexus-ollama-data"
$Port = 11434
$CaBundle = Join-Path $Root "certs\k8s-ca-bundle.pem"

function Test-DockerGpu {
    docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi 2>$null | Out-Null
    return $LASTEXITCODE -eq 0
}

function Wait-OllamaReady {
    param([int]$TimeoutSec = 60)
    for ($i = 0; $i -lt $TimeoutSec; $i++) {
        try {
            Invoke-RestMethod -Uri "http://localhost:$Port/api/tags" -TimeoutSec 3 | Out-Null
            return $true
        } catch { }
        Start-Sleep -Seconds 2
    }
    return $false
}

Write-Host ""
Write-Host "Modulo 13.5 - Ollama offline (GPU + modelo leve)" -ForegroundColor Cyan
Write-Host "Modelo: $Model" -ForegroundColor DarkGray
Write-Host ""

Write-Host "1/5 Verificando GPU (Docker --gpus all)..." -ForegroundColor Yellow
$gpuOk = Test-DockerGpu
if ($gpuOk) {
    Write-Host "[OK] GPU disponivel no Docker." -ForegroundColor Green
} else {
    Write-Host "[WARN] GPU nao disponivel - inferencia em CPU." -ForegroundColor Yellow
}

if (-not (Test-Path $CaBundle)) {
    Write-Host "[WARN] CA bundle nao encontrado. Rode: . .\scripts\Configure-K8sTls.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "2/5 Subindo Ollama (Docker GPU)..." -ForegroundColor Yellow
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
docker rm -f $ContainerName *> $null
$ErrorActionPreference = $prevEap

$caPath = $CaBundle -replace '\\', '/'
$dockerArgs = @(
    "run", "-d", "--name", $ContainerName,
    "-v", "${VolumeName}:/root/.ollama",
    "-p", "${Port}:11434",
    "-e", "OLLAMA_NUM_PARALLEL=1",
    "-e", "OLLAMA_MAX_LOADED_MODELS=1"
)
if ($gpuOk) { $dockerArgs += "--gpus=all" }
if (Test-Path $CaBundle) {
    $dockerArgs += "-v", "${caPath}:/certs/ca-bundle.pem:ro"
    $dockerArgs += "--entrypoint", "sh"
    $dockerArgs += "ollama/ollama:0.5.4"
    $dockerArgs += "-c", "cat /certs/ca-bundle.pem >> /etc/ssl/certs/ca-certificates.crt; exec ollama serve"
} else {
    $dockerArgs += "ollama/ollama:0.5.4"
}

docker @dockerArgs
if ($LASTEXITCODE -ne 0) { throw "Falha ao iniciar container Ollama" }

if (-not (Wait-OllamaReady)) {
    docker logs $ContainerName --tail 30
    throw "Ollama nao respondeu em http://localhost:$Port"
}
Write-Host "[OK] Ollama API em http://localhost:$Port" -ForegroundColor Green

Write-Host ""
Write-Host "3/5 Baixando modelo $Model..." -ForegroundColor Yellow
if (-not $SkipPull) {
    docker exec $ContainerName ollama pull $Model
    if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar modelo $Model" }
} else {
    Write-Host "Pull ignorado (-SkipPull)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "4/5 Smoke test (generate)..." -ForegroundColor Yellow
$body = @{
    model = $Model
    prompt = "Ola! Voce esta rodando no cluster da Camilla? Responda em uma linha."
    stream = $false
} | ConvertTo-Json
$gen = Invoke-RestMethod -Uri "http://localhost:$Port/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 180
Write-Host "Resposta: $($gen.response.Trim())" -ForegroundColor White

Write-Host ""
Write-Host "5/5 Teste DNS interno (Minikube -> host GPU)..." -ForegroundColor Yellow
. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure
kubectl run ollama-dns-test --rm -i --restart=Never --image=curlimages/curl:8.5.0 -- `
    curl -sf "http://host.docker.internal:$Port/api/tags" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Pods Minikube alcancam Ollama via host.docker.internal:$Port" -ForegroundColor Green
} else {
    Write-Host "[WARN] Teste Minikube falhou (cluster pode estar parado)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[OK] Ollama offline pronto." -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Host / CrewAI:  http://localhost:$Port" -ForegroundColor White
Write-Host "  OLLAMA_BASE_URL=http://localhost:$Port" -ForegroundColor White
Write-Host "  OLLAMA_MODEL=ollama/$Model" -ForegroundColor White
Write-Host "  Parar: docker stop $ContainerName" -ForegroundColor DarkGray
Write-Host ""
