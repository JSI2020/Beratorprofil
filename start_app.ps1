# Double-click this file to start the app and open your browser automatically.
# Or run in PowerShell: .\start_app.ps1

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "  Beraterprofil Generator" -ForegroundColor Cyan
Write-Host "  -----------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Opening: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "  Keep this window open while using the app." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

Start-Process "http://localhost:8501"
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1
