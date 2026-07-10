@echo off
cd /d "%~dp0"

echo ========================================
echo  Beraterprofil Generator
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ and add it to PATH.
    pause
    exit /b 1
)

echo [1/3] Stopping old server and clearing cache...
python scripts\restart_app.py 8501
echo.

echo [2/3] Checking app imports...
python -c "import app; print('Import OK')" 
if errorlevel 1 (
    echo ERROR: App failed to load. See error above.
    pause
    exit /b 1
)
echo.

echo [3/3] Starting Streamlit on http://localhost:8501
echo      Keep this window open. Press Ctrl+C to stop.
echo.

set PYTHONDONTWRITEBYTECODE=1
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false

pause
