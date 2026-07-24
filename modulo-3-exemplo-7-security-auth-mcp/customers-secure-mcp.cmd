@echo off
cd /d "%~dp0"
for /f "usebackq tokens=1,2,3 delims=|" %%a in (`powershell -NoProfile -Command "$body = '{\"username\":\"erickwendel\",\"password\":\"123123\",\"adminSuperSecret\":\"AM I THE BOSS?\"}'; $r = Invoke-RestMethod -Uri 'http://127.0.0.1:9999/v1/auth/service-token' -Method POST -ContentType 'application/json' -Body $body; Write-Output ($r.serviceToken + '|' + $r.role + '|' + $r.department)"`) do (
  set SERVICE_TOKEN=%%a
  set SERVICE_TOKEN_ROLE=%%b
  set SERVICE_TOKEN_DEPARTMENT=%%c
)
if "%SERVICE_TOKEN%"=="" (
  echo Failed to obtain SERVICE_TOKEN. Is legacy-api running on port 9999?
  exit /b 1
)
"C:\Program Files\nodejs\node.exe" --experimental-strip-types "%~dp0src\index.ts"
