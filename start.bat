@echo off
setlocal

echo.
echo ========================================
echo   AquaPulse Pro v1.0.0 - Starting Server
echo ========================================
echo.

rem Check for virtual environment
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
    echo Using virtual environment: .venv
) else (
    echo Virtual environment not found.
    echo Run install.bat first to set up dependencies.
    echo.
    pause
    exit /b 1
)

rem Activate virtual environment
call .venv\Scripts\activate.bat

rem Start server and open browser
echo.
echo Server starting at http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
echo.

rem Open browser in background (best effort)
start http://127.0.0.1:8000

rem Start uvicorn server (blocking)
python -c "import uvicorn, sys; sys.path.insert(0, 'src'); uvicorn.run('aquapulse.api:app', host='127.0.0.1', port=8000)"
if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start.
    pause
)

endlocal