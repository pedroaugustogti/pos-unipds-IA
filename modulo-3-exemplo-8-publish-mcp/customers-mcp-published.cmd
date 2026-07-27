@echo off
cd /d "%~dp0"
for /f "usebackq delims=" %%t in (`powershell -NoProfile -Command "$body = '{\"username\":\"erickwendel\",\"password\":\"123123\",\"adminSuperSecret\":\"AM I THE BOSS?\"}'; $r = Invoke-RestMethod -Uri 'http://127.0.0.1:9999/v1/auth/service-token' -Method POST -ContentType 'application/json' -Body $body; Write-Output $r.serviceToken"`) do set SERVICE_TOKEN=%%t
if "%SERVICE_TOKEN%"=="" (
  echo Failed to obtain SERVICE_TOKEN. Is legacy-api running on port 9999?
  exit /b 1
)
set SERVICE_TOKEN=%SERVICE_TOKEN%
npx --yes --registry http://localhost:4873 @pedroaugusto/customers-mcp@latest
