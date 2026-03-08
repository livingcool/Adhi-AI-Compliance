@echo off
REM Complete fresh start for audio pipeline testing

echo.
echo ========================================
echo  AUDIO PIPELINE - FRESH START
echo ========================================
echo.

echo Step 1: Killing ALL Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 3 /nobreak >nul

echo Step 2: Clearing Redis...
docker exec redis_server redis-cli FLUSHALL

echo Step 3: Cleaning data directories...
if exist data\uploads rmdir /s /q data\uploads 2>nul
if exist data\metadata.db del /f data\metadata.db 2>nul
if exist data\vectors\*.faiss del /f data\vectors\*.faiss 2>nul
mkdir data\uploads 2>nul

echo Step 4: Waiting 5 seconds for cleanup...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Starting services...
echo ========================================
echo.

echo Starting Backend (uvicorn)...
start "Backend" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend (streamlit)...
start "Frontend" cmd /k ".venv\Scripts\activate && streamlit run frontend_app.py"

timeout /t 3 /nobreak >nul

echo Starting Celery Worker...
start "Celery" cmd /k ".venv\Scripts\activate && celery -A app.workers.celery_app worker --loglevel=info -P solo -Q cpu_tasks,gpu_tasks"

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo Wait 10 seconds, then test with:
echo   python test_audio_pipeline.py your_audio.mp3
echo.
pause
