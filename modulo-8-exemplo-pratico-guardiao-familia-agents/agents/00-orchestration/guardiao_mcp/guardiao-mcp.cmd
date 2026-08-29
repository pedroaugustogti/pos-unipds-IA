@echo off
REM Cursor MCP launcher — Guardião Família agents (Fase B)
setlocal
cd /d "%~dp0..\..\.."
set "PYTHONPATH=%CD%\agents\00-orchestration;%CD%"
python -m guardiao_mcp
endlocal
