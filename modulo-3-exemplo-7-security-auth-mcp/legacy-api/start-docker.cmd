@echo off
set "PATH=C:\Program Files\Docker\Docker\resources\bin;%PATH%"
cd /d "%~dp0nodejs-fastify-mongodb-crud-z"
echo Building and starting UNIPDS secure API (port 9999)...
docker compose up -d --build --wait
if errorlevel 1 (
  echo Docker failed. Is Docker Desktop running?
  exit /b 1
)
echo API ready at http://127.0.0.1:9999/v1/health
