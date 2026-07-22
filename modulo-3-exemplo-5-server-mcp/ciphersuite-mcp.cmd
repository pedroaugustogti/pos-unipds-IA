@echo off
cd /d "%~dp0"
"C:\Program Files\nodejs\node.exe" --experimental-strip-types "%~dp0src\index.ts"
