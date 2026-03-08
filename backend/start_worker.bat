@echo off
REM Celery Worker Startup Script
REM This script starts the Celery worker with the correct queue configuration

echo Starting Celery worker...
echo Queue: cpu_tasks (for PDF, Audio ingestion)
echo.

.\.venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info -P solo -Q cpu_tasks,gpu_tasks

REM The -Q flag tells the worker which queues to consume from
REM cpu_tasks: For PDF and Audio processing
REM gpu_tasks: For Video and Image processing (can run on same worker for PoC)
