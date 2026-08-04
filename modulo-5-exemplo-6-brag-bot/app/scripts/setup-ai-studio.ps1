# Setup Google AI Studio — BragBot
# Guia interativo (criacao do projeto exige login Google no navegador)

param(
    [string]$ApiKey = "",
    [string]$ProjectName = "brag-bot-unipds"
)

$ErrorActionPreference = "Stop"
$AppDir = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $AppDir ".env"
$EnvExample = Join-Path $AppDir ".env.example"

Write-Host ""
Write-Host "=== BragBot — Google AI Studio Setup ===" -ForegroundColor Cyan
Write-Host ""

# 1. Garantir .env
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "[ok] .env criado a partir de .env.example"
}

# 2. Abrir AI Studio (criacao de projeto = manual, requer login Google)
Write-Host ""
Write-Host "Passo 1 — Criar projeto no AI Studio" -ForegroundColor Yellow
Write-Host "  Nome sugerido: $ProjectName"
Write-Host "  Abrindo https://aistudio.google.com/projects ..."
Start-Process "https://aistudio.google.com/projects"

Read-Host "Pressione ENTER apos criar o projeto no AI Studio"

# 3. Abrir pagina de API keys
Write-Host ""
Write-Host "Passo 2 — Gerar API Key" -ForegroundColor Yellow
Write-Host "  Selecione o projeto '$ProjectName' e clique em Create API key"
Write-Host "  Abrindo https://aistudio.google.com/apikey ..."
Start-Process "https://aistudio.google.com/apikey"

# 4. Capturar chave
if (-not $ApiKey) {
    Write-Host ""
    $ApiKey = Read-Host "Cole a GEMINI_API_KEY (AIza...)" -AsSecureString
    $ApiKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($ApiKey)
    )
}

if (-not $ApiKey -or $ApiKey -notmatch '^AIza') {
    Write-Error "API key invalida ou vazia. Esperado formato AIza..."
}

# 5. Gravar .env
$content = Get-Content $EnvFile -Raw
if ($content -match '(?m)^GEMINI_API_KEY=.*$') {
    $content = $content -replace '(?m)^GEMINI_API_KEY=.*$', "GEMINI_API_KEY=$ApiKey"
} else {
    $content += "`nGEMINI_API_KEY=$ApiKey`n"
}
Set-Content -Path $EnvFile -Value $content.TrimEnd() -Encoding UTF8
Write-Host "[ok] GEMINI_API_KEY salva em .env (nao commitar)"

# 6. Build + teste
Write-Host ""
Write-Host "Passo 3 — Build e teste da API" -ForegroundColor Yellow
Set-Location $AppDir

if (-not (Test-Path "dist/brag-bot/server/server.mjs")) {
    npm run build
}

$job = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    node --env-file=.env dist/brag-bot/server/server.mjs
} -ArgumentList $AppDir

Start-Sleep -Seconds 3

try {
    $body = @{ definition = "Otimizei a API com Redis e reduzi latencia de 800ms para 120ms" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:4000/api/brag" -Method POST -Body $body -ContentType "application/json"
    Write-Host ""
    Write-Host "[ok] API respondeu com sucesso!" -ForegroundColor Green
    Write-Host "  title: $($response.title)"
    Write-Host ""
    Write-Host "App: http://localhost:4000" -ForegroundColor Cyan
    Write-Host "Para subir novamente: npm run serve:ssr:brag-bot"
} catch {
    Write-Host ""
    Write-Host "[erro] Falha no teste da API: $_" -ForegroundColor Red
    Write-Host "Verifique a chave e o projeto no AI Studio."
} finally {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
    Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*brag-bot*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
}
