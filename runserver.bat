@echo off
cd /d "%~dp0"

set "PROJECT_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PROJECT_PYTHON%" (
    echo Cannot find .venv\Scripts\python.exe
    echo Please create the virtual environment and install requirements first.
    pause
    exit /b 1
)

"%PROJECT_PYTHON%" manage.py runserver
if errorlevel 1 pause
