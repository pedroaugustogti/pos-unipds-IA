$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$CursorDir = Join-Path $Root '.cursor'
$ConfigPath = Join-Path $CursorDir 'github-mcp.config.json'
$BinDir = Join-Path $CursorDir 'bin'
$BinaryPath = Join-Path $BinDir 'github-mcp-server.exe'
$McpJsonPath = Join-Path $CursorDir 'mcp.json'

function Write-Step([string]$Message) {
    Write-Host ">> $Message"
}

function Read-Config {
    if (-not (Test-Path $ConfigPath)) {
        throw "Config not found: $ConfigPath"
    }
    return Get-Content $ConfigPath -Raw | ConvertFrom-Json
}

function Ensure-Binary([object]$Config) {
    if (Test-Path $BinaryPath) {
        Write-Step "CLI binary already present"
        return
    }

    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
    $version = $Config.binaryVersion
    $zipName = 'github-mcp-server_Windows_x86_64.zip'
    $zipUrl = "https://github.com/github/github-mcp-server/releases/download/$version/$zipName"
    $zipPath = Join-Path $env:TEMP $zipName

    Write-Step "Downloading GitHub MCP CLI $version"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $BinDir -Force
    Remove-Item $zipPath -Force

    if (-not (Test-Path $BinaryPath)) {
        throw "Binary not found after install: $BinaryPath"
    }
}

function Get-GithubToken {
    $token = [Environment]::GetEnvironmentVariable('CURSOR_GITHUB_TOKEN', 'User')
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw 'CURSOR_GITHUB_TOKEN is not set in the user environment.'
    }
    return $token.Trim()
}

function Invoke-GithubGraphql([string]$Token, [string]$Query) {
    $body = @{ query = $Query } | ConvertTo-Json -Compress
    return Invoke-RestMethod `
        -Uri 'https://api.github.com/graphql' `
        -Method Post `
        -Headers @{
            Authorization = "Bearer $Token"
            'User-Agent' = 'pos-unipds-github-mcp-setup'
        } `
        -ContentType 'application/json' `
        -Body $body
}

function Test-GithubAccess([string]$Token, [object]$Config) {
    Write-Step 'Validating GitHub user'
    $user = Invoke-RestMethod `
        -Uri 'https://api.github.com/user' `
        -Headers @{
            Authorization = "Bearer $Token"
            'User-Agent' = 'pos-unipds-github-mcp-setup'
        }
    Write-Host "   user: $($user.login)"

    Write-Step "Validating org access: $($Config.org)"
    $repos = Invoke-RestMethod `
        -Uri "https://api.github.com/orgs/$($Config.org)/repos?per_page=5" `
        -Headers @{
            Authorization = "Bearer $Token"
            'User-Agent' = 'pos-unipds-github-mcp-setup'
        }
    Write-Host "   repos visible: $($repos.Count)"

    Write-Step "Validating project access: $($Config.org)/projects/$($Config.projectNumber)"
    $query = @"
query {
  organization(login: "$($Config.org)") {
    projectV2(number: $($Config.projectNumber)) {
      id
      title
      url
      items(first: 5) {
        totalCount
        nodes {
          content {
            __typename
            ... on Issue { title number }
            ... on PullRequest { title number }
            ... on DraftIssue { title }
          }
        }
      }
    }
  }
}
"@

    $response = Invoke-GithubGraphql -Token $Token -Query $query
    if ($response.errors) {
        $message = ($response.errors | ForEach-Object { $_.message }) -join '; '
        throw "Project access failed: $message"
    }

    $project = $response.data.organization.projectV2
    if (-not $project) {
        throw "Project #$($Config.projectNumber) not found or not accessible."
    }

    Write-Host "   project: $($project.title)"
    Write-Host "   url: $($project.url)"
    Write-Host "   items: $($project.items.totalCount)"
    foreach ($node in $project.items.nodes) {
        $content = $node.content
        if ($content.title) {
            Write-Host "   - $($content.title)"
        }
    }
}

function Ensure-McpConfig {
    if (-not (Test-Path $McpJsonPath)) {
        throw "mcp.json not found: $McpJsonPath"
    }

    $raw = Get-Content $McpJsonPath -Raw | ConvertFrom-Json
    if (-not $raw.mcpServers.'github-cli') {
        throw 'github-cli entry missing from .cursor/mcp.json'
    }

    Write-Step 'mcp.json already contains github-cli'
}

Write-Host '=== GitHub MCP setup ===' -ForegroundColor Cyan
$config = Read-Config
Ensure-Binary -Config $config
Ensure-McpConfig
$token = Get-GithubToken
Test-GithubAccess -Token $token -Config $config
Write-Host ''
Write-Host 'Setup OK. Reload Cursor: Ctrl+Shift+P -> Developer: Reload Window' -ForegroundColor Green
Write-Host 'Then enable github-cli in Customize if it is not already green.' -ForegroundColor Green
