# Bootstrap Android SDK + AVD para E2E Appium (Windows, sem Android Studio GUI)
param(
    [string]$SdkRoot = "$env:LOCALAPPDATA\Android\Sdk",
    [string]$AvdName = $(if ($env:GF_PARENT_AVD) { $env:GF_PARENT_AVD } else { "Pixel_6_API34_Stable" }),
    [string]$ChildAvdName = $(if ($env:GF_CHILD_AVD) { $env:GF_CHILD_AVD } else { "Pixel_6_API34_Child" }),
    [switch]$SkipAvd,
    [switch]$AcceptLicensesOnly
)

$ErrorActionPreference = "Stop"
$ModuleRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$CmdLineToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$Packages = @(
    "platform-tools",
    "emulator",
    "platforms;android-34",
    "system-images;android-34;google_apis;x86_64"
)

function Write-Step($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }

if (-not (Test-Path $SdkRoot)) {
    New-Item -ItemType Directory -Path $SdkRoot -Force | Out-Null
}

$env:ANDROID_HOME = $SdkRoot
$env:ANDROID_SDK_ROOT = $SdkRoot
$CertFile = Join-Path $ModuleRoot "certs\cacert.pem"
if (Test-Path $CertFile) {
    $env:SSL_CERT_FILE = $CertFile
    $env:JAVA_TOOL_OPTIONS = "-Djavax.net.ssl.trustStoreType=Windows-ROOT"
}
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $SdkRoot, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $SdkRoot, "User")

$pt = Join-Path $SdkRoot "platform-tools\adb.exe"
if (-not (Test-Path $pt)) {
    Write-Step "Baixando platform-tools (zip direto)..."
    $ptZip = Join-Path $env:TEMP "platform-tools.zip"
    Invoke-WebRequest -Uri "https://dl.google.com/android/repository/platform-tools-latest-windows.zip" -OutFile $ptZip -UseBasicParsing
    Expand-Archive -Path $ptZip -DestinationPath $SdkRoot -Force
    Remove-Item $ptZip -Force -ErrorAction SilentlyContinue
}
if (-not (Test-Path (Join-Path $SdkRoot "cmdline-tools\latest\bin\sdkmanager.bat"))) {
    $tmp = Join-Path $env:TEMP "android-cmdline-tools.zip"
    Invoke-WebRequest -Uri $CmdLineToolsUrl -OutFile $tmp -UseBasicParsing
    $extract = Join-Path $env:TEMP "android-cmdline-extract"
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive -Path $tmp -DestinationPath $extract -Force
    $cmdRoot = Join-Path $SdkRoot "cmdline-tools\latest"
    New-Item -ItemType Directory -Path (Split-Path $cmdRoot) -Force | Out-Null
    if (Test-Path $cmdRoot) { Remove-Item $cmdRoot -Recurse -Force }
    Move-Item (Join-Path $extract "cmdline-tools") $cmdRoot
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}

$sdkmanager = Join-Path $SdkRoot "cmdline-tools\latest\bin\sdkmanager.bat"
if (-not (Test-Path $sdkmanager)) {
    throw "sdkmanager não encontrado em $sdkmanager"
}

Write-Step "Aceitando licencas SDK..."
$yes = ("y`n" * 40)
$prevErr = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$yes | & $sdkmanager --sdk_root=$SdkRoot --licenses *> $null
$ErrorActionPreference = $prevErr

if ($AcceptLicensesOnly) { exit 0 }

Write-Step "Instalando pacotes SDK (pode demorar)..."
$ErrorActionPreference = "Continue"
& $sdkmanager --sdk_root=$SdkRoot @Packages
if ($LASTEXITCODE -ne 0) {
    Write-Warning "sdkmanager exit $LASTEXITCODE — verifique proxy/SSL (certs/cacert.pem)"
}
$ErrorActionPreference = $prevErr
if (-not $SkipAvd) {
    $avdmanager = Join-Path $SdkRoot "cmdline-tools\latest\bin\avdmanager.bat"
    $emulator = Join-Path $SdkRoot "emulator\emulator.exe"
    $avds = @(& $emulator -list-avds 2>$null)
    foreach ($name in @($AvdName, $ChildAvdName)) {
        if ($avds -notcontains $name) {
            Write-Step "Criando AVD $name..."
            $createArgs = @(
                "create", "avd",
                "-n", $name,
                "-k", "system-images;android-34;google_apis;x86_64",
                "-d", "pixel_6",
                "--force"
            )
            "no`n" | & $avdmanager @createArgs 2>&1
        } else {
            Write-Host "AVD $name já existe."
        }
    }
}

Write-Step "Verificação"
& $pt version
Write-Host "ANDROID_HOME=$SdkRoot"
Write-Host "Parent AVD=$AvdName · Child AVD=$ChildAvdName (emuladores isolados)"
Write-Host "OK - reinicie o terminal ou defina ANDROID_HOME=$SdkRoot"
