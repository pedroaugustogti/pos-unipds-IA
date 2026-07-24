@echo off
set "PATH=C:\Program Files\Docker\Docker\resources\bin;%PATH%"
cd /d "%~dp0nodejs-fastify-mongodb-crud-z"
docker compose down --remove-orphans
