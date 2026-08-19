@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-github-mcp.ps1"
exit /b %ERRORLEVEL%
