@echo off
REM CivicLens AI - Backend Run Script

echo.
echo ============================================
echo  CivicLens AI - Backend Server
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run FastAPI server
echo Starting FastAPI server...
echo.
echo 🚀 Server starting on http://localhost:8000
echo 📚 API Docs: http://localhost:8000/api/docs
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
