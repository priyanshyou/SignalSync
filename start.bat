@echo off
echo.
echo =======================================================
echo    Coherent B2B Pipeline Setup - One Command Script
echo =======================================================
echo.

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo =======================================================
echo    Starting Pipeline, Scheduler, and API Backend
echo =======================================================
echo.
echo Starting FastAPI Server on http://localhost:8000
echo The scraper will automatically start in the background.
echo.

python -m src.api.main
pause
