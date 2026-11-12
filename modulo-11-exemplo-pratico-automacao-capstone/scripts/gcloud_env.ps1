# Carregar antes de comandos gcloud neste monorepo (Windows + SSL local).
# Uso: . .\scripts\gcloud_env.ps1

$ErrorActionPreference = 'Stop'
$pem = Join-Path $PSScriptRoot '..\config\windows-roots.pem' | Resolve-Path
$py = 'C:\Users\Pedro Augusto\AppData\Local\Programs\Python\Python311\python.exe'

$env:CLOUDSDK_PYTHON = $py
$env:SSL_CERT_FILE = $pem.Path
$env:REQUESTS_CA_BUNDLE = $pem.Path

gcloud config set core/custom_ca_certs_file $pem.Path | Out-Null
gcloud config set account pedroaugusto.gti@gmail.com | Out-Null

Write-Host "gcloud env OK — account=$(gcloud config get-value account 2>$null) ca=$($pem.Path)"
