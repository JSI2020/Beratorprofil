# Double-click this file to start the app and open your browser automatically.
# Or run in PowerShell: .\start_app.ps1

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "  Stopping old Streamlit on port 8501 and clearing cache..." -ForegroundColor DarkGray
python scripts\restart_app.py 8501
Write-Host ""
Write-Host "  Beraterprofil Generator" -ForegroundColor Cyan
Write-Host "  -----------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Opening: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "  Keep this window open while using the app." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

$env:PYTHONDONTWRITEBYTECODE = "1"
Start-Process "http://localhost:8501"
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1
