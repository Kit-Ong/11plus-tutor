@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo.
echo Starting 11+ Tutor...
echo Opening http://localhost:3783 in your browser...
echo.
echo Press Ctrl+C to stop
echo.
start "" http://localhost:3783
python scripts/start_app.py
