# P3 — merge MCP Capstone into workspace .cursor/mcp.json
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir

$mcpPath = Join-Path $Script:RepoRoot '.cursor\mcp.json'
$examplePath = Join-Path $Script:PraticoRoot 'config\mcp.capstone.example.json'
if (-not (Test-Path $mcpPath)) { throw "Missing $mcpPath" }
if (-not (Test-Path $examplePath)) { throw "Missing $examplePath" }

$backup = "$mcpPath.bak-$(Get-Date -Format 'yyyyMMddHHmmss')"
Copy-Item $mcpPath $backup -Force

$current = Get-Content $mcpPath -Raw | ConvertFrom-Json
$example = Get-Content $examplePath -Raw | ConvertFrom-Json

# Convert to mutable hashtables
$servers = @{}
foreach ($p in $current.mcpServers.PSObject.Properties) { $servers[$p.Name] = $p.Value }

$capstoneRootSlash = $Script:CapstoneRoot -replace '\\', '/'
$added = @()

# playwright MCP for Capstone automation
if (-not $servers.ContainsKey('playwright-capstone')) {
  $outDir = Join-Path $Script:PraticoRoot '.playwright-mcp'
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  $servers['playwright-capstone'] = @{
    command = 'npx'
    args = @('-y', '@playwright/mcp@latest', '--isolated', '--save-session', '--output-dir', $outDir)
  }
  $added += 'playwright-capstone'
}

if (-not $servers.ContainsKey('langfuse-docs')) {
  $servers['langfuse-docs'] = @{ url = 'https://langfuse.com/api/mcp' }
  $added += 'langfuse-docs'
}

if (-not $servers.ContainsKey('angular-cli-capstone')) {
  $servers['angular-cli-capstone'] = @{
    command = 'npx'
    args = @('-y', '@angular/cli', 'mcp')
    cwd = (Join-Path $Script:CapstoneRoot 'apps\web')
  }
  $added += 'angular-cli-capstone'
}

# Rebuild JSON preserving github-cli etc.
$outObj = [ordered]@{ mcpServers = [ordered]@{} }
foreach ($k in ($servers.Keys | Sort-Object)) {
  $outObj.mcpServers[$k] = $servers[$k]
}
($outObj | ConvertTo-Json -Depth 10) | Set-Content -Path $mcpPath -Encoding UTF8

$skillsOk = (Test-Path (Join-Path $Script:CapstoneRoot 'CLAUDE.md')) -or (Test-Path (Join-Path $Script:CapstoneRoot '.agents\skills'))
Update-State 'P3' 'ok'
Write-PhaseEvidence 'P3-mcp' @{
  status = 'ok'
  backup = $backup
  added = $added
  skills_present = $skillsOk
  note = 'Restart Cursor MCP servers after merge. Langfuse MCP with secrets: set via user env, not mcp.json.'
} | Out-Null
Write-Host "P3=ok added=$($added -join ',') backup=$backup skills=$skillsOk"
