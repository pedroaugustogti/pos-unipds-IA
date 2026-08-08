# Configura TLS para kubectl/minikube/k3d em Windows (inspeção TLS corporativa).
# Uso:
#   . .\scripts\Configure-K8sTls.ps1              # sessão atual
#   . .\scripts\Configure-K8sTls.ps1 -Persist     # variável de usuário permanente
#   . .\scripts\Configure-K8sTls.ps1 -ForceInsecure  # só insecure (lab)

param(
    [switch]$Persist,
    [switch]$ForceInsecure,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$NexusRoot = Split-Path -Parent $PSScriptRoot
$CertsDir = Join-Path $NexusRoot "certs"
$CaBundle = Join-Path $CertsDir "k8s-ca-bundle.pem"
$KubeConfig = Join-Path $env:USERPROFILE ".kube\config"
$MinikubeCa = Join-Path $env:USERPROFILE ".minikube\ca.crt"

function Write-Info([string]$Message) {
    if (-not $Quiet) { Write-Host $Message }
}

function Export-CaBundle {
    New-Item -ItemType Directory -Force -Path $CertsDir | Out-Null
    $blocks = [System.Collections.Generic.List[string]]::new()

    foreach ($store in @("Cert:\LocalMachine\Root", "Cert:\CurrentUser\Root")) {
        if (-not (Test-Path $store)) { continue }
        Get-ChildItem -Path $store -ErrorAction SilentlyContinue | ForEach-Object {
            $b64 = [Convert]::ToBase64String($_.RawData, [Base64FormattingOptions]::InsertLineBreaks)
            $blocks.Add("-----BEGIN CERTIFICATE-----`n$b64`n-----END CERTIFICATE-----")
        }
    }

    if (Test-Path $MinikubeCa) {
        $blocks.Add((Get-Content $MinikubeCa -Raw).Trim())
    }

    if ($blocks.Count -eq 0) {
        throw "Nenhum certificado encontrado para exportar."
    }

    ($blocks -join "`n`n") | Set-Content -Path $CaBundle -Encoding ascii
    return $CaBundle
}

function Get-KubeClusters {
    if (-not (Test-Path $KubeConfig)) { return @() }
    $names = kubectl config get-clusters 2>$null
    if (-not $names) { return @() }
    return $names | Where-Object { $_ -and $_ -ne "NAME" }
}

function Set-ClusterTls([string]$ClusterName, [string]$CaPath, [bool]$Insecure) {
    if ($Insecure) {
        kubectl config set-cluster $ClusterName --insecure-skip-tls-verify=true | Out-Null
        kubectl config unset "clusters.$ClusterName.certificate-authority" 2>$null | Out-Null
        kubectl config unset "clusters.$ClusterName.certificate-authority-data" 2>$null | Out-Null
        return "insecure"
    }

    kubectl config set-cluster $ClusterName --certificate-authority=$CaPath | Out-Null
    kubectl config unset "clusters.$ClusterName.insecure-skip-tls-verify" 2>$null | Out-Null
    return "ca-bundle"
}

function Test-ClusterTls([string]$ClusterName) {
    $ctx = kubectl config current-context 2>$null
    kubectl config use-context $ClusterName 2>$null | Out-Null
    $ok = $false
    try {
        kubectl get --raw=/healthz 2>$null | Out-Null
        $ok = ($LASTEXITCODE -eq 0)
    } catch {
        $ok = $false
    }
    if ($ctx) { kubectl config use-context $ctx 2>$null | Out-Null }
    return $ok
}

# 1) Variável global usada por kubectl e por k8s_ops.py
$env:KUBE_INSECURE_SKIP_TLS_VERIFY = "true"
if ($Persist) {
    [Environment]::SetEnvironmentVariable("KUBE_INSECURE_SKIP_TLS_VERIFY", "true", "User")
    Write-Info "[OK] KUBE_INSECURE_SKIP_TLS_VERIFY=true (usuario, permanente)"
} else {
    Write-Info "[OK] KUBE_INSECURE_SKIP_TLS_VERIFY=true (sessao atual)"
}

# 2) Bundle de CAs do Windows + minikube no path do projeto
$caPath = Export-CaBundle
Write-Info "[OK] CA bundle: $caPath"

# 3) Patch kubeconfig por cluster
$clusters = Get-KubeClusters
if ($clusters.Count -eq 0) {
    Write-Info "[INFO] Nenhum cluster no kubeconfig ainda (rode minikube/k3d start antes)."
    return
}

foreach ($cluster in $clusters) {
    if ($ForceInsecure) {
        Set-ClusterTls -ClusterName $cluster -CaPath $caPath -Insecure $true | Out-Null
        Write-Info "  - $cluster : insecure-skip-tls-verify"
        continue
    }

    Set-ClusterTls -ClusterName $cluster -CaPath $caPath -Insecure $false | Out-Null
    if (Test-ClusterTls -ClusterName $cluster) {
        Write-Info "  - $cluster : certificate-authority ($caPath)"
    } else {
        Set-ClusterTls -ClusterName $cluster -CaPath $caPath -Insecure $true | Out-Null
        Write-Info "  - $cluster : insecure-skip-tls-verify (fallback lab)"
    }
}

Write-Info ""
Write-Info "Teste: kubectl get nodes"
