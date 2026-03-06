@echo OFF
echo Starting QSM Monitoring Server...

set "VENV_PATH=%~dp0..\..\.qsm_venv"
echo Checking for virtual environment at %VENV_PATH%

if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Virtual environment not found. Please run the training script first to create it.
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

echo Launching web monitor...
cd /D "%~dp0web_monitor"
python web_monitor.py

pause