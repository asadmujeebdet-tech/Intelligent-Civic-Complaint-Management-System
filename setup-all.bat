@echo off
REM CivicLens AI - Complete System Setup

echo.
echo ===============================================
echo  CivicLens AI - Complete System Setup
echo ===============================================
echo.

echo 📦 Setting up Backend...
cd backend
call setup.bat
cd ..

echo.
echo 📦 Frontend Setup (HTML/CSS/Bootstrap)...
cd frontend
call setup.bat
cd ..

echo.
echo ===============================================
echo ✅ All setup complete!
echo.
echo Next steps:
echo 1. Update .env file in backend folder with:
echo    - MONGO_URI (MongoDB Atlas connection)
echo    - DB_NAME (database name)
echo    - GEMINI_API_KEY (Google Gemini API key)
echo.
echo 2. Open ONE terminal and navigate to backend:
echo    - cd backend
echo    - run.bat
echo.
echo 3. Backend will serve both API and frontend:
echo    - API: http://localhost:8000/api/v1
echo    - Frontend: http://localhost:8000
echo    - API Docs: http://localhost:8000/api/docs
echo.
echo ===============================================
echo.
pause
