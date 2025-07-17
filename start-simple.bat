@echo off
REM CreAItion Simplified Startup Script
REM Starts FastAPI backend and React frontend

echo 🚀 Starting CreAItion Platform (FastAPI + React)...

REM Create necessary directories
if not exist "backend\assets" mkdir backend\assets
if not exist "backend\output" mkdir backend\output

REM Start Backend
echo 🤖 Starting FastAPI Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo 📦 Installing/updating Python dependencies...
pip install -r requirements.txt

echo 🚀 Starting FastAPI Backend on port 8002...
start "FastAPI Backend" python fast_api.py

cd ..

REM Start Frontend
echo 🎨 Starting Frontend...
if not exist "frontend\node_modules" (
    echo 📦 Installing Node.js dependencies...
    cd frontend
    npm install
    cd ..
)

cd frontend
echo 🎨 Starting Frontend on port 5173...
start "Frontend" npm run dev
cd ..

timeout /t 3 /nobreak >nul

echo.
echo ✅ CreAItion Platform Started Successfully!
echo.
echo 🌐 Access Points:
echo    Frontend:     http://localhost:5173
echo    FastAPI:      http://localhost:8002
echo.
echo 📊 Health Check:
echo    Backend:      http://localhost:8002/health
echo.
echo Press any key to open the frontend...
pause >nul

start http://localhost:5173
