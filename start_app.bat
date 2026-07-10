@echo off
cd /d "%~dp0"
echo Stopping old Streamlit on port 8501 and clearing cache...
python scripts\restart_app.py 8501
echo.
echo Starting Beraterprofil Streamlit App...
echo.
echo Open in browser: http://localhost:8501
echo.
set PYTHONDONTWRITEBYTECODE=1
start "" "http://localhost:8501"
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
pause
