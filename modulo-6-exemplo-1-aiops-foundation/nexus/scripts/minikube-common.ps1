# Funcoes compartilhadas para scripts Minikube (nexus)

function Ensure-MinikubePath {
    if (Get-Command minikube -ErrorAction SilentlyContinue) { return }
    $local = Join-Path $env:USERPROFILE "bin\minikube.exe"
    if (Test-Path $local) {
        $env:Path = "$(Split-Path $local);$env:Path"
        return
    }
    throw "minikube nao encontrado. Instale: winget install Kubernetes.minikube --source winget"
}

function Reset-DockerEnv {
    Remove-Item Env:DOCKER_HOST -ErrorAction SilentlyContinue
    Remove-Item Env:DOCKER_CERT_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:DOCKER_TLS_VERIFY -ErrorAction SilentlyContinue
    Remove-Item Env:DOCKER_MACHINE_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:MINIKUBE_ACTIVE_DOCKERD -ErrorAction SilentlyContinue
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    docker context use desktop-linux *> $null
    $ErrorActionPreference = $prev
}

function Get-MinikubeStatus {
    $raw = minikube status --format='{{.Host}}|{{.Kubelet}}|{{.APIServer}}' 2>$null
    if (-not $raw) { return @{ Host = "Unknown"; Kubelet = "Unknown"; APIServer = "Unknown" } }
    $parts = $raw -split '\|'
    return @{
        Host     = $parts[0]
        Kubelet  = $parts[1]
        APIServer = $parts[2]
    }
}

function Start-MinikubeLite {
    param(
        [int]$MemoryMB = 1800,
        [int]$Cpus = 2,
        [string]$Profile = "minikube",
        [switch]$Recreate
    )

    Reset-DockerEnv

    if ($Recreate) {
        Write-Host "Recriando profile $Profile com ${MemoryMB}MB..." -ForegroundColor Yellow
        $prev = $ErrorActionPreference
        $ErrorActionPreference = "SilentlyContinue"
        minikube delete -p $Profile --purge *> $null
        $ErrorActionPreference = $prev
        Start-Sleep -Seconds 2
    }

    $status = Get-MinikubeStatus
    if (-not $Recreate -and $status.APIServer -eq "Running" -and $status.Host -eq "Running") {
        Write-Host "[OK] Cluster ja em execucao." -ForegroundColor Green
        return
    }

    if ($status.Host -eq "Running" -and $status.APIServer -ne "Running") {
        Write-Host "[WARN] Cluster inconsistente. Reiniciando..." -ForegroundColor Yellow
        $prev = $ErrorActionPreference
        $ErrorActionPreference = "SilentlyContinue"
        minikube stop -p $Profile *> $null
        $ErrorActionPreference = $prev
        Start-Sleep -Seconds 3
    }

    Write-Host "Iniciando minikube leve (${MemoryMB}MB RAM, ${Cpus} CPU)..." -ForegroundColor Cyan
    minikube start `
        -p $Profile `
        --driver=docker `
        --memory=$MemoryMB `
        --cpus=$Cpus `
        --disk-size=16g `
        --addons=dashboard `
        --wait=none `
        --wait-timeout=3m

    # Recria kubeconfig com nova porta — reaplica TLS fix
    . (Join-Path $PSScriptRoot "Configure-K8sTls.ps1") -Quiet -ForceInsecure

    $ready = $false
    for ($i = 0; $i -lt 45; $i++) {
        kubectl get nodes 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) {
        throw "API server nao respondeu. Rode: . .\scripts\Configure-K8sTls.ps1 -Persist -ForceInsecure"
    }

    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    minikube addons disable metrics-server -p $Profile *> $null
    minikube addons enable auto-pause -p $Profile *> $null
    $ErrorActionPreference = $prev
}
