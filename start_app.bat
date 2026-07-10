@echo off
cd /d "%~dp0"
echo Starting Beraterprofil Streamlit App...
echo.
echo Open in browser: http://localhost:8501
echo.
start "" "http://localhost:8501"
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
