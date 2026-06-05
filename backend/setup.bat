@echo off
REM CivicLens AI - Backend Setup Script for Windows

echo.
echo ============================================
echo  CivicLens AI - Backend Setup
echo ============================================
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================
echo ✅ Backend setup complete!
echo.
echo Next steps:
echo 1. Update .env file with your credentials
echo 2. Run: python -m uvicorn app.main:app --reload
echo.
echo API Documentation: http://localhost:8000/api/docs
echo ============================================
echo.
pause
