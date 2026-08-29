# Instala dev clients Expo — parent e child em emuladores/Metro isolados
param(
    [ValidateSet("parent", "child", "both")]
    [string]$App = "both",
    [string]$ParentEmulator = $(if ($env:GF_PARENT_EMULATOR_SERIAL) { $env:GF_PARENT_EMULATOR_SERIAL } else { "emulator-5554" }),
    [string]$ChildEmulator = $(if ($env:GF_CHILD_EMULATOR_SERIAL) { $env:GF_CHILD_EMULATOR_SERIAL } else { "emulator-5556" }),
    [int]$ParentMetroPort = $(if ($env:GF_PARENT_METRO_PORT) { [int]$env:GF_PARENT_METRO_PORT } else { 8082 }),
    [int]$ChildMetroPort = $(if ($env:GF_CHILD_METRO_PORT) { [int]$env:GF_CHILD_METRO_PORT } else { 9090 }),
    [switch]$SkipPrebuild,
    [switch]$SkipEmulatorCheck,
    [switch]$Clean,
    # Legado: forçar um único serial (não recomendado)
    [string]$Emulator = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "mobile_short_paths.ps1") -Quiet

if (-not $env:ANDROID_HOME) {
    $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
    $env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
}

$adb = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"
if (-not (Test-Path $adb)) { throw "adb nao encontrado em $adb" }

if ($Emulator) {
    Write-Host "AVISO: -Emulator unico e legado; preferir ParentEmulator/ChildEmulator" -ForegroundColor Yellow
    $ParentEmulator = $Emulator
    $ChildEmulator = $Emulator
}

function Wait-EmulatorBoot([string]$serial) {
    $deadline = (Get-Date).AddMinutes(4)
    do {
        Start-Sleep -Seconds 4
        $ready = & $adb -s $serial shell getprop sys.boot_completed 2>$null
    } while ($ready -ne "1" -and (Get-Date) -lt $deadline)
    if ($ready -ne "1") { throw "Emulador $serial nao bootou a tempo" }
}

function Ensure-EmulatorOnline([string]$serial, [string]$mode) {
    $devices = & $adb devices 2>&1 | Select-String "device$"
    if ($devices -match [regex]::Escape($serial)) { return }
    if ($SkipEmulatorCheck) { throw "Emulador $serial offline" }
    Write-Host "Emulador $serial offline - iniciando via API repo ($mode)..." -ForegroundColor Yellow
    $apiPath = if ($env:GUARDAO_API_PATH) { $env:GUARDAO_API_PATH.TrimEnd('\') } else { "C:\gf\r\a" }
    if (-not (Test-Path $apiPath)) { throw "GUARDAO_API_PATH invalido: $apiPath" }
    Push-Location $apiPath
    try {
        if ($mode -eq "dual") {
            npm run emulators:start
        } else {
            npm run emulators:start:single
        }
    } finally {
        Pop-Location
    }
    Wait-EmulatorBoot $serial
}

function Normalize-GfDriveRoot($path) {
    $p = $path.Trim().TrimEnd('\')
    if ($p -match '^[A-Za-z]:$') { return "$p\" }
    return $p
}

function Ensure-AndroidProject($shortRoot, $label) {
    $shortRoot = Normalize-GfDriveRoot $shortRoot
    $androidDir = Join-Path $shortRoot "android"
    if ((Test-Path $androidDir) -and (Test-Path (Join-Path $androidDir "gradlew.bat"))) {
        return $androidDir
    }
    if ($SkipPrebuild) { throw "android/ ausente em $shortRoot (rode sem -SkipPrebuild)" }
    Write-Host "`n==> expo prebuild ($label) em $shortRoot" -ForegroundColor Cyan
    Push-Location $shortRoot
    try {
        npx expo prebuild --platform android --no-install
    } finally {
        Pop-Location
    }
    if (-not (Test-Path (Join-Path $androidDir "gradlew.bat"))) {
        throw "prebuild falhou: gradlew ausente em $androidDir"
    }
    return $androidDir
}

function Ensure-ExclusiveDeepLinkScheme($androidDir, $scheme, $packageName) {
    # Evita chooser "Open with" do scheme compartilhado expo-dev-launcher entre parent/child.
    $manifest = Join-Path $androidDir "app\src\main\AndroidManifest.xml"
    if (-not (Test-Path $manifest)) { return }
    $xml = Get-Content $manifest -Raw -ErrorAction SilentlyContinue
    if (-not $xml) { return }
    if ($xml -match [regex]::Escape("android:scheme=`"$scheme`"")) { return }

    $filter = @"
      <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="$scheme"/>
      </intent-filter>
"@
    if ($xml -match '(?s)(<activity[^>]*android:name="\.MainActivity"[^>]*>)(.*?)(</activity>)') {
        $before = $Matches[1]
        $body = $Matches[2]
        $after = $Matches[3]
        if ($body -notmatch [regex]::Escape("android:scheme=`"$scheme`"")) {
            $newBody = $body + "`n" + $filter
            $xml = $xml.Replace($before + $body + $after, $before + $newBody + $after)
            $utf8 = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($manifest, $xml, $utf8)
            Write-Host "  + scheme exclusivo '$scheme' em AndroidManifest ($packageName)" -ForegroundColor DarkCyan
        }
    }
}

function Set-GradleShortPaths($androidDir) {
    $props = Join-Path $androidDir "gradle.properties"
    $text = ""
    if (Test-Path $props) { $text = Get-Content $props -Raw -ErrorAction SilentlyContinue }
    $patch = @{
        "android.enableLongPaths"  = "true"
        "reactNativeArchitectures" = "x86_64"
        "org.gradle.caching"       = "true"
    }
    if ($env:GF_WIN_BUILD -ne "0") {
        $patch["newArchEnabled"] = "false"
        $patch["edgeToEdgeEnabled"] = "false"
        $patch["expo.edgeToEdgeEnabled"] = "false"
        $patch["android.compileSdkVersion"] = "35"
        $patch["android.targetSdkVersion"] = "35"
    }
    foreach ($k in $patch.Keys) {
        if ($text -match "(?m)^\s*$([regex]::Escape($k))\s*=") {
            $text = [regex]::Replace($text, "(?m)^\s*$([regex]::Escape($k))\s*=.*$", "$k=$($patch[$k])")
        } else {
            $text = $text.TrimEnd() + "`n$k=$($patch[$k])`n"
        }
    }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($props, $text, $utf8)
}

function Install-DevClient($envKey, $label, $metroPort, $serial, $scheme, $packageName) {
    $shortRoot = [Environment]::GetEnvironmentVariable($envKey, "Process")
    if (-not $shortRoot) { throw "$envKey nao definido; rode mobile_short_paths.ps1" }
    $shortRoot = Normalize-GfDriveRoot $shortRoot

    Write-Host "`n==> $label dev client ($shortRoot) -> $serial · Metro $metroPort · scheme $scheme" -ForegroundColor Cyan
    Ensure-EmulatorOnline $serial $(if ($ParentEmulator -ne $ChildEmulator) { "dual" } else { "single" })

    $androidDir = Ensure-AndroidProject $shortRoot $label
    Set-GradleShortPaths $androidDir
    foreach ($s in @($scheme -split ',')) {
        $trimmed = $s.Trim()
        if ($trimmed) { Ensure-ExclusiveDeepLinkScheme $androidDir $trimmed $packageName }
    }

    $env:ANDROID_SERIAL = $serial
    $env:LC_NUMERIC = "en_US.UTF-8"

    Push-Location $androidDir
    try {
        # Daemon ligado por padrão (build quente). CI: $env:GF_GRADLE_NO_DAEMON=1
        $daemonArgs = @()
        if ($env:GF_GRADLE_NO_DAEMON -eq "1") { $daemonArgs = @("--no-daemon") }
        if ($Clean) { & .\gradlew.bat @daemonArgs clean | Out-Null }
        $portArg = "-PreactNativeDevServerPort=$metroPort"
        & .\gradlew.bat @daemonArgs installDebug $portArg --parallel
        if ($LASTEXITCODE -ne 0) { throw "gradlew installDebug falhou (exit $LASTEXITCODE)" }
    } finally {
        Pop-Location
    }

    & $adb -s $serial reverse "tcp:$metroPort" "tcp:$metroPort" | Out-Null
}

if ($App -in @("child", "both")) {
    Install-DevClient "GUARDAO_CHILD_PATH" "child" $ChildMetroPort $ChildEmulator "guardiao-filho,exp+guardiao-familia-child,guardiaofamilia" "com.guardiofilho"
}
if ($App -in @("parent", "both")) {
    Install-DevClient "GUARDAO_PARENT_PATH" "parent" $ParentMetroPort $ParentEmulator "guardiao-pai,exp+guardiao-familia-parent" "com.guardiaofamilia.parent"
}

Write-Host "`nPacotes instalados (isolados por emulador):" -ForegroundColor Green
if ($App -in @("parent", "both")) {
    Write-Host "parent @$ParentEmulator :" -NoNewline
    & $adb -s $ParentEmulator shell pm list packages 2>$null | Select-String "guardiao"
}
if ($App -in @("child", "both")) {
    Write-Host "child @$ChildEmulator :" -NoNewline
    & $adb -s $ChildEmulator shell pm list packages 2>$null | Select-String "guardiao|filho"
}
