@echo off
echo ========================================
echo    STARTING ALL AAROGYA ABHAYA SERVERS
echo ========================================
echo.

REM Get the directory where this script is located
set "PROJECT_DIR=%~dp0"

echo [1/3] Starting Flask ML Server...
start cmd /k "cd /d "%PROJECT_DIR%flask-ml-server" && echo Flask ML Server starting on port 5000... && python app.py"
timeout /t 3

echo [2/3] Starting Malnutrition App...
start cmd /k "cd /d "%PROJECT_DIR%flask-ml-server" && echo Malnutrition App starting on port 8501... && streamlit run malnutrition_app.py"
timeout /t 3

echo [3/3] Starting Website Server...
start cmd /k "cd /d "%PROJECT_DIR%aarogya-backend" && echo Website Server starting on port 3000... && node server.js"
timeout /t 3

echo.
echo ========================================
echo    ✅ ALL SERVERS STARTED!
echo ========================================
echo.
echo Server URLs:
echo   🟢 Flask ML:      http://localhost:5000
echo   🏥 Malnutrition:  http://localhost:8501
echo   🌐 Website:       http://localhost:3000
echo.
echo NOTE: Posture detection is triggered from the pregnant dashboard.
echo.
start http://localhost:3000
echo.
pause
