# P6 — validate .env keys present (no values printed)
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir

$required = @(
  'DATABASE_URL',
  'GOOGLE_CLOUD_PROJECT_ID',
  'GOOGLE_CLOUD_LOCATION',
  'MODEL_GRADE',
  'MODEL_ANSWER',
  'MODEL_EMBEDDING',
  'SERPER_API_KEY',
  'LANGFUSE_PUBLIC_KEY',
  'LANGFUSE_SECRET_KEY',
  'LANGFUSE_BASE_URL'
)
$optional = @('OTEL_EXPORTER_OTLP_ENDPOINT', 'OTEL_EXPORTER_OTLP_HEADERS')

$map = [ordered]@{}
foreach ($k in $required) { $map[$k] = Test-EnvKeySet $k }
foreach ($k in $optional) { $map[$k] = Test-EnvKeySet $k }

$missing = @($required | Where-Object { -not $map[$_] })
$status = if ($missing.Count -eq 0) { 'ok' } else { 'partial' }
Update-State 'P6' $status
Write-PhaseEvidence 'P6-env' @{ status = $status; present = $map; missing = $missing } | Out-Null
$map.GetEnumerator() | ForEach-Object { Write-Host ("{0}: {1}" -f $_.Key, $(if($_.Value){'set'}else{'MISSING'})) }
if ($missing.Count) { Write-Host "MISSING: $($missing -join ', ')" }
Write-Host "P6=$status"
exit $(if ($missing.Count -eq 0) { 0 } else { 1 })
