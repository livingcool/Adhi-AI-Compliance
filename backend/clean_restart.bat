@echo off
REM Complete clean restart - kills all Celery processes and clears everything

echo Killing all Celery workers...
taskkill /F /IM celery.exe 2>nul

echo.
echo Clearing Redis completely...
docker exec redis_server redis-cli FLUSHALL

echo.
echo Redis cleared!
echo.
echo Waiting 2 seconds for cleanup...
timeout /t 2 /nobreak >nul

echo.
echo Starting Celery worker with completely fresh state...
.\.venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info -P solo -Q cpu_tasks,gpu_tasks
