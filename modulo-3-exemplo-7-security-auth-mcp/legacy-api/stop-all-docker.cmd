@echo off
set "PATH=C:\Program Files\Docker\Docker\resources\bin;%PATH%"
echo Stopping exemplo 6 legacy-api (if running)...
if exist "%~dp0..\..\modulo-3-exemplo-6-mcp-integration-api\legacy-api\docker-compose.yml" (
  pushd "%~dp0..\..\modulo-3-exemplo-6-mcp-integration-api\legacy-api"
  docker compose down --remove-orphans 2>nul
  popd
)
echo Stopping exemplo 7 legacy-api...
pushd "%~dp0nodejs-fastify-mongodb-crud-z"
docker compose down --remove-orphans 2>nul
popd
echo Stopping any remaining containers...
for /f %%i in ('docker ps -q 2^>nul') do docker stop %%i
echo Done.
