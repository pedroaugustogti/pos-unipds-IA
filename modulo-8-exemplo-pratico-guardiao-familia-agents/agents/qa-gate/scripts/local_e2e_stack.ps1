# local_e2e_stack.ps1 - Orquestra Docker, emuladores, Metro e Appium
param(
    [ValidateSet("Check", "ApiOnly", "Full")]
    [string]$Mode = "ApiOnly",
    [switch]$SingleEmulator,
    [switch]$SkipDockerStart
)

$ErrorActionPreference = "Stop"
$ModuleRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$Root = $ModuleRoot
$ApiPath = if ($env:GUARDAO_API_PATH) { $env:GUARDAO_API_PATH } else { "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api" }
$MobileSetupPath = if ($env:GUARDAO_MOBILE_SETUP_PATH) { $env:GUARDAO_MOBILE_SETUP_PATH } else { "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-mobile-setup" }
$ParentPath = if ($env:GUARDAO_PARENT_PATH) { $env:GUARDAO_PARENT_PATH } else { "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent" }
$ChildPath = if ($env:GUARDAO_CHILD_PATH) { $env:GUARDAO_CHILD_PATH } else { "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child" }

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

function Ensure-Docker {
    if ($SkipDockerStart) { return }
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Iniciando Docker Desktop..."
        $candidates = @(
            "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
            "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
        )
        $started = $false
        foreach ($exe in $candidates) {
            if (Test-Path $exe) {
                Start-Process $exe | Out-Null
                $started = $true
                break
            }
        }
        if (-not $started) { throw "Docker Desktop nao encontrado." }
        $deadline = (Get-Date).AddMinutes(3)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Seconds 5
            docker info 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { return }
        }
        throw "Docker daemon nao respondeu a tempo."
    }
}

function Ensure-ApiEnv {
    $envFile = Join-Path $ApiPath ".env"
    $dockerEnv = Join-Path $ApiPath ".env.docker"
    $example = Join-Path $ApiPath ".env.example"
    if (-not (Test-Path $envFile) -and (Test-Path $example)) {
        Copy-Item $example $envFile
        Write-Host "Criado .env a partir de .env.example"
    }
    if (-not (Test-Path $dockerEnv)) {
        Set-Content $dockerEnv "# Overrides Docker (opcional)`n"
        Write-Host "Criado .env.docker vazio"
    }
}

function Wait-ApiHealth {
    param([int]$TimeoutSec = 180)
    $url = "http://127.0.0.1:3000/api/v1/health"
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            if ($r.StatusCode -eq 200) { return $true }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $false
}

function Invoke-ApiBootstrap {
    Ensure-ApiEnv
    Write-Step "Docker Compose (Postgres + Redis)"
    Push-Location $ApiPath
    try {
        docker compose -f docker-compose.dev.yml up -d postgres redis
        if ($LASTEXITCODE -ne 0) { throw "docker compose postgres/redis falhou" }

        Write-Step "Aguardando Postgres..."
        $deadline = (Get-Date).AddMinutes(2)
        while ((Get-Date) -lt $deadline) {
            docker exec guardiao-postgres-dev pg_isready -U guardiao_admin -d guardiao_familia 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { break }
            Start-Sleep -Seconds 2
        }

        if (-not (Test-Path (Join-Path $ApiPath "node_modules"))) {
            Write-Step "npm ci (primeira vez - pode demorar)"
            npm ci
            if ($LASTEXITCODE -ne 0) { throw "npm ci falhou" }
        }

        Write-Step "Migrations + seed"
        $env:DATABASE_URL = "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia"
        $env:REDIS_URL = "redis://127.0.0.1:6379"
        npm run migration:run
        if ($LASTEXITCODE -ne 0) { throw "migration:run falhou" }
        npm run seed
        if ($LASTEXITCODE -ne 0) { throw "seed falhou" }

        if (-not (Wait-ApiHealth -TimeoutSec 5)) {
            Write-Step "API no host (nest start:dev) - fallback quando build Docker falha"
            $apiJob = Start-Job -ScriptBlock {
                param($Path)
                Set-Location $Path
                $env:DATABASE_URL = "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia"
                $env:REDIS_URL = "redis://127.0.0.1:6379"
                $env:PORT = "3000"
                npm run start:dev 2>&1
            } -ArgumentList $ApiPath
            Start-Sleep -Seconds 3
            if (-not (Wait-ApiHealth -TimeoutSec 120)) {
                Stop-Job $apiJob -ErrorAction SilentlyContinue
                Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
                throw "API /health nao respondeu (host mode)"
            }
            Write-Host "API OK (host): http://127.0.0.1:3000/api/v1/health" -ForegroundColor Green
        } else {
            Write-Host "API OK: http://127.0.0.1:3000/api/v1/health" -ForegroundColor Green
        }

        docker image inspect guardiao-familia-api:dev 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Step "Container API (imagem existente)"
            docker compose -f docker-compose.dev.yml up -d api 2>$null
        }
    } finally {
        Pop-Location
    }
}

function Invoke-PairingApiSmoke {
    Write-Step "Smoke API pareamento (Python + task36 fallback)"
    Push-Location $Root
    try {
        python -c "from lib.mobile.local_e2e import run_pairing_smoke_python; import json,sys; r=run_pairing_smoke_python(); print(json.dumps(r, default=str)); sys.exit(0 if r.get('ok') else 1)"
        if ($LASTEXITCODE -ne 0) {
            Push-Location $ApiPath
            try {
                $env:GF_API_BASE_URL = "http://127.0.0.1:3000/api/v1"
                npm run test:prototipo_v2:task36
                if ($LASTEXITCODE -ne 0) { throw "pairing smoke FAIL" }
            } finally {
                Pop-Location
            }
        }
        Write-Host "Pairing API smoke PASS" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

function Resolve-AndroidHome {
    foreach ($c in @($env:ANDROID_HOME, $env:ANDROID_SDK_ROOT, "$env:LOCALAPPDATA\Android\Sdk", "$env:USERPROFILE\AppData\Local\Android\Sdk")) {
        if ($c -and (Test-Path "$c\platform-tools\adb.exe")) {
            $env:ANDROID_HOME = $c
            $env:ANDROID_SDK_ROOT = $c
            return $c
        }
    }
    return $null
}

function Start-MetroJobs {
    Write-Step "Metro parent (8082) e child (9090)"
    $parentEnv = @{ EXPO_PUBLIC_API_BASE_URL = "http://10.0.2.2:3000/api/v1" }
    $childEnv = @{
        EXPO_PUBLIC_API_BASE_URL = "http://localhost:3000/api/v1"
        EXPO_PUBLIC_API_BASE_URL_EMULATOR = "http://10.0.2.2:3000/api/v1"
    }
    $parentJob = Start-Job -ScriptBlock {
        param($Path, $EnvMap)
        Set-Location $Path
        foreach ($k in $EnvMap.Keys) { Set-Item -Path "env:$k" -Value $EnvMap[$k] }
        npx expo start --port 8082 --non-interactive 2>&1
    } -ArgumentList $ParentPath, $parentEnv

    $childJob = Start-Job -ScriptBlock {
        param($Path, $EnvMap)
        Set-Location $Path
        foreach ($k in $EnvMap.Keys) { Set-Item -Path "env:$k" -Value $EnvMap[$k] }
        npx expo start --port 9090 --non-interactive 2>&1
    } -ArgumentList $ChildPath, $childEnv

    Start-Sleep -Seconds 15
    return @{ Parent = $parentJob; Child = $childJob }
}

function Invoke-FullMobile {
    $sdk = Resolve-AndroidHome
    if (-not $sdk) { throw "ANDROID_HOME nao configurado. Instale Android Studio SDK." }

    Write-Step "Emuladores Android"
    Push-Location $MobileSetupPath
    try {
        $emuArgs = @("-ExecutionPolicy", "Bypass", "-File", ".\scripts\start-emulators.ps1", "-WaitBoot")
        if ($SingleEmulator) { $emuArgs += "-Single" }
        powershell @emuArgs
        if ($LASTEXITCODE -ne 0) { throw "start-emulators falhou" }
    } finally {
        Pop-Location
    }

    $metros = Start-MetroJobs
    try {
        Write-Step "Appium pairing E2E (mobile-setup)"
        Push-Location $MobileSetupPath
        try {
            $env:GF_API_BASE_URL = "http://127.0.0.1:3000/api/v1"
            python .\appium\pairing\run.py
            if ($LASTEXITCODE -ne 0) { throw "Appium pairing FAIL" }
            Write-Host "Appium pairing PASS" -ForegroundColor Green
        } finally {
            Pop-Location
        }
    } finally {
        Stop-Job $metros.Parent, $metros.Child -ErrorAction SilentlyContinue
        Remove-Job $metros.Parent, $metros.Child -Force -ErrorAction SilentlyContinue
    }
}

Write-Step "Modo: $Mode"
Set-Location $Root

switch ($Mode) {
    "Check" {
        python agents/qa-gate/scripts/local_e2e_smoke.py check
        exit $LASTEXITCODE
    }
    "ApiOnly" {
        Ensure-Docker
        Invoke-ApiBootstrap
        Invoke-PairingApiSmoke
    }
    "Full" {
        Ensure-Docker
        Invoke-ApiBootstrap
        Invoke-PairingApiSmoke
        Invoke-FullMobile
    }
}

Write-Host "`nConcluido com sucesso." -ForegroundColor Green
