@echo off
setlocal
cd /d "%~dp0"

echo [1/4] Stopping all Docker containers...
call legacy-api\stop-all-docker.cmd
if errorlevel 1 exit /b 1

echo [2/4] Installing MCP dependencies...
call npm install
if errorlevel 1 exit /b 1

echo [3/4] Starting secure legacy API (Docker)...
call legacy-api\start-docker.cmd
if errorlevel 1 exit /b 1

echo [4/4] Running tests...
call npm test
if errorlevel 1 exit /b 1

echo.
echo Exemplo 7 ready. API: http://127.0.0.1:9999/v1
echo MCP launcher: customers-secure-mcp.cmd
endlocal
