@echo off
chcp 65001 >nul
REM run_dashboard.bat - Auto-Venv Mode
echo ==================================================
echo [QSOT] Flamehaven Dashboard Launcher
echo ==================================================

REM 1. Set paths
cd /d "%~dp0"
set "VENV_DIR=.venv"

REM 2. Check/Create Virtual Environment
if not exist "%VENV_DIR%" (
    echo [SETUP] Virtual Environment not found. Creating...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 ( 
        echo [ERROR] Failed to create venv. Check Python installation.
        pause
        exit /b 1
    )
    
    echo [SETUP] Activating and Installing Dependencies...
    call "%VENV_DIR%\Scripts\activate.bat"
    python -m pip install --upgrade pip
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
    ) else (
        echo [WARN] requirements.txt not found. Installing streamlit manually...
        python -m pip install streamlit numpy
    )
) else (
    echo [INFO] Virtual Environment found. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
)

REM 2.1 Ensure Dependencies are Up-to-Date
echo [SETUP] Checking Dependencies (This may take a while for PyTorch)...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
)

REM 3. Set Environment Variables
set "PYTHONPATH=%~dp0src"
echo [INFO] PYTHONPATH: %PYTHONPATH%

REM 4. Run Dashboard
echo.
echo [INFO] Launching Dashboard...
python -m streamlit run src\qsot\server\dashboard.py --server.port 8501 --server.address 127.0.0.1

if %errorlevel% neq 0 (
    echo [ERROR] Dashboard crashed with code %errorlevel%
)

echo.
echo [INFO] Session Closed.
pause
