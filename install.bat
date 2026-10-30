@echo off
setlocal

echo.
echo ========================================
echo   AquaPulse Pro v1.0.0 - Installer
echo ========================================
echo.
echo Installing dependencies...
echo.

rem Create virtual environment if it doesn't exist
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python 3.10+ is installed and on your PATH.
        echo Download Python from: https://python.org
        pause
        exit /b 1
    )
    echo     Virtual environment created successfully.
) else (
    echo [1/3] Virtual environment already exists.
)

rem Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

rem Install/upgrade pip
echo [2/3] Upgrading pip...
python -m pip install --upgrade pip --quiet

rem Install the package
echo [3/3] Installing AquaPulse and dependencies...
pip install -e ".[dev]" --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start AquaPulse, run:  start.bat
echo Or:  .venv\Scripts\activate && python run.py
echo.
pause
endlocal