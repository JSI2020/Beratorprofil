# Double-click this file to start the app.
# Or run in PowerShell: .\start_app.ps1

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "  Beraterprofil Generator" -ForegroundColor Cyan
Write-Host "  -----------------------" -ForegroundColor DarkGray
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  ERROR: Python not found." -ForegroundColor Red
    exit 1
}

Write-Host "  [1/3] Stopping old server and clearing cache..." -ForegroundColor DarkGray
python scripts\restart_app.py 8501

Write-Host "  [2/3] Checking app imports..." -ForegroundColor DarkGray
python -c "import app; print('Import OK')"
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "  [3/3] Starting Streamlit on http://localhost:8501" -ForegroundColor Green
Write-Host "        Keep this window open. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

$env:PYTHONDONTWRITEBYTECODE = "1"
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
