@echo off
cd /d "%~dp0"

REM Check if environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found. Please run the install script first.
    pause
    exit /b
)

call venv\Scripts\activate.bat

REM Check if Python script exists
if not exist "scripts\start_app.py" (
    echo Error: scripts\start_app.py not found in %CD%
    pause
    exit /b
)

echo.
echo Starting 11+ Tutor...
echo Please wait while services start...
echo.
echo Press Ctrl+C to stop
echo.

REM Run the app (browser will open automatically when ready)
python scripts/start_app.py

REM Pause only if the app crashed
if %errorlevel% neq 0 pause