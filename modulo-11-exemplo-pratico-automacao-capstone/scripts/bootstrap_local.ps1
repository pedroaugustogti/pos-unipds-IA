# P1 — bootstrap local
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir

$checks = [ordered]@{}
function Set-Check($k, $ok, $detail) { $checks[$k] = @{ ok = [bool]$ok; detail = "$detail" } }

try { Set-Check 'node' ((node -v) -match 'v(2[4-9]|[3-9])') (node -v) } catch { Set-Check 'node' $false $_.Exception.Message }
try {
  corepack enable 2>$null | Out-Null
  corepack prepare pnpm@11.20.0 --activate 2>$null | Out-Null
} catch {}
try { Set-Check 'pnpm' $true (& (Get-Pnpm) -v) } catch { Set-Check 'pnpm' $false $_.Exception.Message }
try { Set-Check 'git' $true (git --version) } catch { Set-Check 'git' $false $_.Exception.Message }
try { Set-Check 'gh' ((gh auth status 2>&1 | Out-String) -match 'Logged in') ((gh auth status 2>&1 | Select-Object -First 3) -join ' ') } catch { Set-Check 'gh' $false $_.Exception.Message }
try {
  Use-GcloudEnv
  $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  $gv = (& gcloud --version 2>&1 | Where-Object { $_ -match 'Google Cloud SDK' } | Select-Object -First 1)
  $ErrorActionPreference = $prev
  Set-Check 'gcloud' ([bool]$gv) "$gv"
} catch { Set-Check 'gcloud' $false $_.Exception.Message }

$dockerOk = $false
$dockerDetail = 'daemon off'
try {
  $info = docker info 2>&1 | Out-String
  if ($info -match 'Server Version') { $dockerOk = $true; $dockerDetail = 'daemon up' }
  else { $dockerDetail = ($info -split "`n" | Select-Object -First 2) -join ' ' }
} catch { $dockerDetail = $_.Exception.Message }
if (-not $dockerOk) {
  $dd = @(
    "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
    "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($dd) {
    Start-Process $dd | Out-Null
    $dockerDetail = 'Docker Desktop start requested — wait and re-run'
  }
}
Set-Check 'docker' $dockerOk $dockerDetail
Set-Check 'seed' (Test-Path $Script:SeedRoot) $Script:SeedRoot
Set-Check 'full' (Test-Path $Script:CapstoneRoot) $Script:CapstoneRoot

$allCritical = $checks.node.ok -and $checks.pnpm.ok -and $checks.git.ok -and $checks.gcloud.ok -and $checks.seed.ok -and $checks.full.ok
$status = if ($allCritical -and $dockerOk) { 'ok' } elseif ($allCritical) { 'ok_docker_pending' } else { 'action_required' }
Update-State 'P1' $status
Write-PhaseEvidence 'P1-bootstrap' @{ status = $status; checks = $checks } | Out-Null
$checks.GetEnumerator() | ForEach-Object { Write-Host ("{0}: {1} — {2}" -f $_.Key, $(if($_.Value.ok){'OK'}else{'FAIL'}), $_.Value.detail) }
Write-Host "P1=$status"
exit $(if ($allCritical) { 0 } else { 1 })
