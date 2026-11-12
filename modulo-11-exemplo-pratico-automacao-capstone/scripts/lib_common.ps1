$ErrorActionPreference = 'Stop'
$Script:PraticoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Script:RepoRoot = (Resolve-Path (Join-Path $Script:PraticoRoot '..')).Path
$Script:CapstoneRoot = Join-Path $Script:PraticoRoot 'workspace\capstone-project-ai-researcher'
$Script:SeedRoot = Join-Path $Script:PraticoRoot 'workspace\ai-researcher-seed'
$Script:Preflight = Join-Path $Script:PraticoRoot 'evidencias\preflight'
$Script:StatePath = Join-Path $Script:Preflight 'state.json'
$Script:PemPath = Join-Path $Script:PraticoRoot 'config\windows-roots.pem'

function Ensure-PreflightDir {
  New-Item -ItemType Directory -Force -Path $Script:Preflight | Out-Null
}

function Write-PhaseEvidence([string]$Phase, [hashtable]$Data) {
  Ensure-PreflightDir
  $Data.phase = $Phase
  $Data.updated = (Get-Date).ToUniversalTime().ToString('o')
  $path = Join-Path $Script:Preflight "$Phase.json"
  $Data | ConvertTo-Json -Depth 8 | Set-Content -Path $path -Encoding UTF8
  return $path
}

function Update-State([string]$Phase, [string]$Status) {
  Ensure-PreflightDir
  $state = @{ updated = (Get-Date).ToUniversalTime().ToString('o'); phases = @{} }
  if (Test-Path $Script:StatePath) {
    $raw = Get-Content $Script:StatePath -Raw | ConvertFrom-Json
    $state.phases = @{}
    foreach ($p in $raw.phases.PSObject.Properties) { $state.phases[$p.Name] = $p.Value }
  }
  $state.phases[$Phase] = $Status
  $state.updated = (Get-Date).ToUniversalTime().ToString('o')
  $state | ConvertTo-Json -Depth 5 | Set-Content -Path $Script:StatePath -Encoding UTF8
}

function Use-GcloudEnv {
  # gcloud writes "Updated property" to stderr; don't treat as terminating error
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  if (Test-Path $Script:PemPath) {
    $env:SSL_CERT_FILE = $Script:PemPath
    $env:REQUESTS_CA_BUNDLE = $Script:PemPath
    & gcloud config set core/custom_ca_certs_file $Script:PemPath 2>&1 | Out-Null
  }
  $py = 'C:\Users\Pedro Augusto\AppData\Local\Programs\Python\Python311\python.exe'
  if (Test-Path $py) { $env:CLOUDSDK_PYTHON = $py }
  & gcloud config set account pedroaugusto.gti@gmail.com 2>&1 | Out-Null
  $ErrorActionPreference = $prev
}

function Invoke-Gcloud {
  param([Parameter(ValueFromRemainingArguments=$true)][string[]]$GcloudArgs)
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  $output = & gcloud @GcloudArgs 2>&1
  $code = $LASTEXITCODE
  $ErrorActionPreference = $prev
  return [pscustomobject]@{ ExitCode = $code; Output = $output }
}

function Test-EnvKeySet([string]$Name) {
  $envFile = Join-Path $Script:CapstoneRoot '.env'
  if (-not (Test-Path $envFile)) { return $false }
  $hit = Get-Content $envFile | Where-Object { $_ -match "^$Name=(.+)$" } | Select-Object -Last 1
  if (-not $hit) { return $false }
  $v = ($hit -split '=', 2)[1].Trim().Trim('"').Trim("'")
  return ($v.Length -gt 0 -and $v -notmatch '^(REPLACE_ME|pk-lf-|sk-lf-|seu-project-id)$')
}

function Get-Pnpm {
  $cmd = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $cmd = Get-Command pnpm -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  throw 'pnpm not found'
}
