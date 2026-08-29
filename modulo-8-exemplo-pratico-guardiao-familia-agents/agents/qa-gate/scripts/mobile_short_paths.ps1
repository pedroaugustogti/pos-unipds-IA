# Paths curtos via junction (C:\gf\r\*) — env referencial GUARDAO_*_PATH aponta para o link.
param(
    [switch]$Unset,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$Script:GfLinkRoot = if ($env:GF_LINK_ROOT) { $env:GF_LINK_ROOT } else { "C:\gf\r" }

$Script:GfPathRegistry = @(
    @{
        LinkName   = "p"
        EnvKey     = "GUARDAO_PARENT_PATH"
        SourceEnv  = "GF_SOURCE_PARENT"
        DefaultSource = "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent"
    },
    @{
        LinkName   = "c"
        EnvKey     = "GUARDAO_CHILD_PATH"
        SourceEnv  = "GF_SOURCE_CHILD"
        DefaultSource = "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child"
    },
    @{
        LinkName   = "a"
        EnvKey     = "GUARDAO_API_PATH"
        SourceEnv  = "GF_SOURCE_API"
        DefaultSource = "C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api"
    }
)

$Script:GfShortDirs = @{
    GRADLE_USER_HOME = if ($env:GF_GRADLE_HOME) { $env:GF_GRADLE_HOME } else { "C:\gf\.gradle" }
    GF_NPM_CACHE     = if ($env:GF_NPM_CACHE) { $env:GF_NPM_CACHE } else { "C:\gf\.npm" }
}

function Write-GfLog($m) {
    if (-not $Quiet) { Write-Host $m -ForegroundColor DarkGray }
}

function Get-GfSourcePath($entry) {
    $fromEnv = [Environment]::GetEnvironmentVariable($entry.SourceEnv, "Process")
    if (-not $fromEnv) { $fromEnv = [Environment]::GetEnvironmentVariable($entry.SourceEnv, "User") }
    if ($fromEnv) {
        $resolved = Resolve-Path $fromEnv -ErrorAction SilentlyContinue
        if ($resolved) { return $resolved.Path }
        return $fromEnv
    }
    return $entry.DefaultSource
}

function Get-JunctionTarget($linkPath) {
    if (-not (Test-Path $linkPath)) { return $null }
    $item = Get-Item $linkPath -Force -ErrorAction SilentlyContinue
    if ($item.LinkType -eq "Junction") { return $item.Target }
    return $null
}

function Ensure-GfJunction($entry) {
    $source = (Get-GfSourcePath $entry).TrimEnd('\')
    if (-not (Test-Path $source)) {
        throw "Origem inexistente para $($entry.EnvKey): $source"
    }
    $source = (Resolve-Path $source).Path

    if (-not (Test-Path $Script:GfLinkRoot)) {
        New-Item -ItemType Directory -Path $Script:GfLinkRoot -Force | Out-Null
    }

    $linkPath = Join-Path $Script:GfLinkRoot $entry.LinkName
    $existing = Get-JunctionTarget $linkPath

    if ($existing) {
        $target = ($existing | Select-Object -First 1)
        if ($target -ieq $source) {
            Write-GfLog "junction $linkPath -> $source (ok)"
        } else {
            Write-GfLog "junction $linkPath removendo target $target"
            cmd /c rmdir "$linkPath" 2>$null
            cmd /c mklink /J "$linkPath" "$source" | Out-Null
        }
    } elseif (Test-Path $linkPath) {
        throw "Path existe e nao e junction: $linkPath"
    } else {
        Write-GfLog "junction $linkPath -> $source"
        cmd /c mklink /J "$linkPath" "$source" | Out-Null
    }

    Set-Item -Path "env:$($entry.EnvKey)" -Value $linkPath
    Set-Item -Path "env:$($entry.SourceEnv)" -Value $source
    return $linkPath
}

function Ensure-GfShortDirs {
    foreach ($kv in $Script:GfShortDirs.GetEnumerator()) {
        if (-not (Test-Path $kv.Value)) {
            New-Item -ItemType Directory -Path $kv.Value -Force | Out-Null
        }
        Set-Item -Path "env:$($kv.Key)" -Value $kv.Value
    }
}

function Remove-GfJunctions {
    foreach ($entry in $Script:GfPathRegistry) {
        $linkPath = Join-Path $Script:GfLinkRoot $entry.LinkName
        if (Get-JunctionTarget $linkPath) {
            cmd /c rmdir "$linkPath" 2>$null
            Write-GfLog "removed junction $linkPath"
        }
    }
}

function Remove-LegacySubst {
    foreach ($letter in @("P", "Y", "A", "X")) {
        $out = subst 2>&1 | Where-Object { $_ -like "${letter}:\:*" }
        if ($out) { subst "${letter}:" /d 2>$null }
    }
}

if ($Unset) {
    Remove-GfJunctions
    Remove-LegacySubst
    if (-not $Quiet) { Write-Host "GF short paths removidos." -ForegroundColor Yellow }
    return
}

Remove-LegacySubst
Ensure-GfShortDirs
$resolved = @{}
foreach ($entry in $Script:GfPathRegistry) {
    $resolved[$entry.EnvKey] = Ensure-GfJunction $entry
}

if (-not $Quiet) {
    Write-Host "`nGF short paths (junction + env):" -ForegroundColor Cyan
    Write-Host "  GF_LINK_ROOT=$Script:GfLinkRoot"
    foreach ($kv in $resolved.GetEnumerator() | Sort-Object Name) {
        $src = Get-GfSourcePath ($Script:GfPathRegistry | Where-Object { $_.EnvKey -eq $kv.Key })
        Write-Host "  $($kv.Key)=$($kv.Value)  <=  $src"
    }
    Write-Host "  GRADLE_USER_HOME=$env:GRADLE_USER_HOME"
}

return $resolved
