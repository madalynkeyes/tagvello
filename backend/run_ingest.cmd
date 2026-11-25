@echo off
REM Daily Tagvello price check. Task Scheduler runs this file.
REM Output is appended to backend\logs\ingest.log.

cd /d "%~dp0"
if not exist logs mkdir logs

echo ===== %date% %time% =====>> logs\ingest.log

REM Make sure the database container is running (Docker Desktop must be open).
docker compose -f ..\docker-compose.yml up -d >> logs\ingest.log 2>&1

.venv\Scripts\python.exe -m worker.ingest >> logs\ingest.log 2>&1
echo.>> logs\ingest.log
