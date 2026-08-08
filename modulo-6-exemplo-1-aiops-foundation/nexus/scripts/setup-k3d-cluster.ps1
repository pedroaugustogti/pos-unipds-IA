# Setup cluster k3d local para Lab 3 (Windows)
# Corrige TLS x509 no containerd via k3d-registries.yaml

param(
    [string]$ClusterName = "nexus-lab"
)

$ErrorActionPreference = "Stop"
$NexusRoot = Split-Path -Parent $PSScriptRoot
$RegistriesConfig = Join-Path $NexusRoot "k8s\k3d-registries.yaml"

$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
    [System.Environment]::GetEnvironmentVariable("Path", "User")

if (-not (Get-Command k3d -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando k3d via winget..."
    winget install k3d --source winget --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
        [System.Environment]::GetEnvironmentVariable("Path", "User")
}

docker info | Out-Null

$clusters = k3d cluster list 2>&1 | Out-String
if ($clusters -notmatch $ClusterName) {
    Write-Host "Criando cluster $ClusterName..."
    k3d cluster create $ClusterName --agents 0 --wait --registry-config $RegistriesConfig
}
else {
    Write-Host "Cluster $ClusterName já existe."
}

k3d kubeconfig merge $ClusterName --kubeconfig-switch-context | Out-Null

. (Join-Path $PSScriptRoot "Configure-K8sTls.ps1")
Write-Host ""
kubectl get nodes
