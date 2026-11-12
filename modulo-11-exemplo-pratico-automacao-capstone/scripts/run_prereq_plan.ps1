# Orquestrador pré-requisitos Capstone
param(
  [ValidateSet('P1','P3','P4','P5','P6','P9')]
  [string]$Until = 'P6',
  [switch]$DemoOnly,
  [switch]$ConfirmSql,
  [switch]$SkipSeed
)
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir

$order = @('P1','P6','P3','P5','P4','P9')
$stopAt = [array]::IndexOf($order, $Until)
if ($stopAt -lt 0) { throw "Unknown phase $Until" }

Write-Host "=== Capstone prereq plan until $Until ==="

for ($i = 0; $i -le $stopAt; $i++) {
  $phase = $order[$i]
  Write-Host "`n----- $phase -----"
  switch ($phase) {
    'P1' {
      & "$PSScriptRoot\bootstrap_local.ps1"
      if ($LASTEXITCODE -notin @(0,1)) { throw "P1 failed $LASTEXITCODE" }
    }
    'P6' {
      & "$PSScriptRoot\check_env_keys.ps1"
      # continue even if Serper missing
    }
    'P3' {
      & "$PSScriptRoot\setup_mcp_skills.ps1"
    }
    'P5' {
      $gcpArgs = @('-Phase','all-safe')
      if ($ConfirmSql) { $gcpArgs += '-ConfirmSql' }
      & "$PSScriptRoot\gcp_fundacao.ps1" @gcpArgs
    }
    'P4' {
      $a = @()
      if ($DemoOnly) { $a += '-DemoOnly' }
      if ($SkipSeed) { $a += '-SkipSeed' }
      & "$PSScriptRoot\up_local.ps1" @a
      if ($LASTEXITCODE -eq 2) {
        Write-Host 'P4 blocked on Docker — fix daemon and re-run -Until P4'
      }
    }
    'P9' {
      Push-Location $Script:RepoRoot
      python (Join-Path $Script:PraticoRoot 'scripts\run_evidencias_capstone.py')
      Pop-Location
      Update-State 'P9' $(if ($LASTEXITCODE -eq 0) { 'ok' } else { 'partial' })
    }
  }
}

Write-Host "`n=== state ==="
if (Test-Path $Script:StatePath) { Get-Content $Script:StatePath }
Write-Host "Done until $Until"
