# P4 — stack local
param(
  [switch]$DemoOnly,
  [switch]$SkipSeed,
  [switch]$SkipInstall
)
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir
Set-Location $Script:CapstoneRoot

$pnpm = Get-Pnpm
$result = [ordered]@{ docker = $false; install = $false; migrate = $false; seed = $false; note = @() }

$info = docker info 2>&1 | Out-String
if ($info -notmatch 'Server Version') {
  Update-State 'P4' 'blocked:docker'
  Write-PhaseEvidence 'P4-local' @{ status = 'blocked:docker'; detail = 'Start Docker Desktop and re-run' } | Out-Null
  Write-Host 'P4=blocked:docker'
  exit 2
}
$result.docker = $true

if (-not $SkipInstall) {
  & $pnpm install --frozen-lockfile
  if ($LASTEXITCODE -ne 0) {
    & $pnpm install
  }
  if ($LASTEXITCODE -ne 0) { throw "pnpm install failed: $LASTEXITCODE" }
  $result.install = $true
}

# Só Postgres local — api/web sobem via pnpm dev (compose build de imagem falha sem turbo no prune)
docker compose up -d postgres
$deadline = (Get-Date).AddMinutes(2)
do {
  Start-Sleep -Seconds 2
  $hc = docker compose exec -T postgres pg_isready -U postgres 2>&1 | Out-String
} while ($hc -notmatch 'accepting' -and (Get-Date) -lt $deadline)
if ($hc -notmatch 'accepting') { throw "postgres not healthy: $hc" }

# migrate.ts lê process.env.DATABASE_URL — carregar do .env sem imprimir
$envFile = Join-Path $Script:CapstoneRoot '.env'
Get-Content $envFile | ForEach-Object {
  if ($_ -match '^\s*([A-Z0-9_]+)=(.*)$') {
    $k = $Matches[1]; $v = $Matches[2].Trim().Trim('"').Trim("'")
    if ($k -and $v) { Set-Item -Path "Env:$k" -Value $v }
  }
}
if (-not $env:DATABASE_URL) {
  $env:DATABASE_URL = 'postgresql://postgres:postgres@localhost:5434/ai_researcher'
}

& $pnpm db:migrate
if ($LASTEXITCODE -ne 0) { throw "db:migrate failed" }
$result.migrate = $true

if ($DemoOnly) {
  $result.note += 'DEMO mode — skip seed'
  $result.seed = $false
} elseif (-not $SkipSeed) {
  if (-not (Test-EnvKeySet 'GOOGLE_CLOUD_PROJECT_ID')) { throw 'GOOGLE_CLOUD_PROJECT_ID missing in .env' }
  & $pnpm seed
  $result.seed = ($LASTEXITCODE -eq 0)
  if (-not $result.seed) { $result.note += 'seed failed — Vertex/ADC?' }
}

# Playwright browsers (best effort)
Push-Location (Join-Path $Script:CapstoneRoot 'apps\web')
try { & $pnpm exec playwright install 2>$null | Out-Null } catch { $result.note += 'playwright install skipped' }
Pop-Location

$status = if ($result.migrate) { 'ok' } else { 'partial' }
Update-State 'P4' $status
Write-PhaseEvidence 'P4-local' @{ status = $status; result = $result } | Out-Null
Write-Host "P4=$status"
exit 0
