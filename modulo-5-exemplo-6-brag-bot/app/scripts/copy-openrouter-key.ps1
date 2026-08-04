# Copia OPENROUTER_* de outro exemplo do curso para o BragBot (sem exibir segredos)
$ErrorActionPreference = "Stop"
$AppDir = Split-Path $PSScriptRoot -Parent
$RepoRoot = Resolve-Path (Join-Path $AppDir "..\..")

$sources = @(
    "modulo-3-exemplo-9-mcp-langchain\.env",
    "modulo-4-exemplo-1-agente-ia-contratos\runtime\.env",
    "modulo-4-exemplo-6-plan-execute-e-reflection\runtime\.env",
    "modulo-4-exemplo-3-observabilidade\runtime\.env"
)

$sourceFile = $null
foreach ($rel in $sources) {
    $candidate = Join-Path $RepoRoot $rel
    if ((Test-Path $candidate) -and (Select-String -Path $candidate -Pattern '^OPENROUTER_API_KEY=\S+' -Quiet)) {
        $sourceFile = $candidate
        break
    }
}

if (-not $sourceFile) {
    Write-Error "Nenhum .env com OPENROUTER_API_KEY encontrado nos exemplos do curso."
}

$vars = @(
    'OPENROUTER_API_KEY',
    'OPENROUTER_MODEL',
    'OPENROUTER_BASE_URL',
    'OPENROUTER_HTTP_REFERER',
    'OPENROUTER_X_TITLE'
)

$lines = @(
    '# Copiado automaticamente de outro exemplo do curso POS',
    'LLM_PROVIDER=openrouter',
    'PORT=4000',
    ''
)

foreach ($name in $vars) {
    $match = Select-String -Path $sourceFile -Pattern "^$name=(.*)$" | Select-Object -First 1
    if ($match) {
        $lines += $match.Line
    }
}

if (-not ($lines | Where-Object { $_ -match '^OPENROUTER_API_KEY=\S+' })) {
    Write-Error "OPENROUTER_API_KEY vazia no arquivo de origem."
}

$dest = Join-Path $AppDir ".env"
Set-Content -Path $dest -Value ($lines -join "`n") -Encoding UTF8
Write-Host "[ok] .env atualizado em $dest (origem: $(Split-Path $sourceFile -Leaf))"
Write-Host "[ok] LLM_PROVIDER=openrouter"
