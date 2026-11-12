$ErrorActionPreference = 'Continue'
$Root = Split-Path $PSScriptRoot -Parent
$Capstone = Join-Path $Root 'workspace\capstone-project-ai-researcher'
$Preflight = Join-Path $Root 'evidencias\preflight'
New-Item -ItemType Directory -Force -Path $Preflight | Out-Null

$report = [ordered]@{}

function Step($name, $scriptBlock) {
  Write-Host "`n===== $name ====="
  try {
    $out = & $scriptBlock 2>&1 | Out-String
    Write-Host $out
    $report[$name] = @{ ok = $true; detail = ($out.Trim() -replace '\s+', ' ').Substring(0, [Math]::Min(300, ($out.Trim().Length))) }
  } catch {
    Write-Host "FAIL: $($_.Exception.Message)"
    $report[$name] = @{ ok = $false; detail = $_.Exception.Message }
  }
}

Step 'pnpm11' {
  corepack enable
  corepack prepare pnpm@11.20.0 --activate
  "pnpm=$(pnpm.cmd -v)"
}

Step 'firebase-tools' {
  npm.cmd install -g firebase-tools
  "firebase=$(firebase --version)"
}

Step 'uv' {
  # Official Windows install
  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
  $env:Path = "$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:Path"
  "uv=$(uv --version)"; "uvx=$(uvx --version)"
}

Step 'playwright' {
  Push-Location (Join-Path $Capstone 'apps\web')
  try {
    if (-not (Test-Path (Join-Path $Capstone 'node_modules'))) {
      Push-Location $Capstone; pnpm.cmd install; Pop-Location
    }
    pnpm.cmd exec playwright install
    pnpm.cmd exec playwright --version
  } finally { Pop-Location }
}

Step 'postgres-vector' {
  $running = docker ps --filter 'name=capstone-project-ai-researcher-postgres' --format '{{.Names}}'
  if (-not $running) {
    Push-Location $Capstone
    docker compose up -d postgres
    Pop-Location
    Start-Sleep -Seconds 5
  }
  docker compose -f (Join-Path $Capstone 'docker-compose.yml') exec -T postgres `
    psql -U postgres -d ai_researcher -c 'CREATE EXTENSION IF NOT EXISTS vector;'
  docker compose -f (Join-Path $Capstone 'docker-compose.yml') exec -T postgres `
    psql -U postgres -d ai_researcher -c '\dx'
}

Step 'gcloud-sql-proxy' {
  $pem = Join-Path $Root 'config\windows-roots.pem'
  if (Test-Path $pem) {
    $env:SSL_CERT_FILE = $pem
    $env:REQUESTS_CA_BUNDLE = $pem
  }
  $env:CLOUDSDK_PYTHON = 'C:\Users\Pedro Augusto\AppData\Local\Programs\Python\Python311\python.exe'
  $ErrorActionPreference = 'Continue'
  # Prefer component; fallback to documented binary note
  $list = gcloud components list --format='value(id,state.name)' 2>&1 | Out-String
  if ($list -match 'cloud-sql-proxy') {
    gcloud components install cloud-sql-proxy --quiet 2>&1 | Out-String
  } else {
    "cloud-sql-proxy component not in list; use Cloud SQL Auth Proxy separately if needed"
  }
  "gcloud=$(gcloud --version 2>&1 | Select-Object -First 1)"
}

$reportPath = Join-Path $Preflight 'install-pending.json'
$report.updated = (Get-Date).ToUniversalTime().ToString('o')
($report | ConvertTo-Json -Depth 6) | Set-Content $reportPath -Encoding UTF8
Write-Host "`nWrote $reportPath"
$report.GetEnumerator() | ForEach-Object {
  if ($_.Key -eq 'updated') { return }
  Write-Host ("{0}: {1}" -f $_.Key, $(if ($_.Value.ok) {'OK'} else {'FAIL'}))
}
