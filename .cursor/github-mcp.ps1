$ErrorActionPreference = 'Stop'

$configPath = Join-Path $PSScriptRoot 'github-mcp.config.json'
$config = if (Test-Path $configPath) {
    Get-Content $configPath -Raw | ConvertFrom-Json
} else {
    [pscustomobject]@{ toolsets = 'repos,issues,pull_requests,orgs,projects' }
}

$token = [Environment]::GetEnvironmentVariable('CURSOR_GITHUB_TOKEN', 'User')
if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Error 'CURSOR_GITHUB_TOKEN is not set in the user environment.'
    exit 1
}

$env:GITHUB_PERSONAL_ACCESS_TOKEN = $token.Trim()
$binary = Join-Path $PSScriptRoot 'bin/github-mcp-server.exe'

if (-not (Test-Path $binary)) {
    Write-Error "GitHub MCP binary missing. Run .cursor/setup-github-mcp.cmd first."
    exit 1
}

& $binary stdio --toolsets $config.toolsets
