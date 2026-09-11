@echo off
echo ========================================
echo    STARTING ALL AAROGYA ABHAYA SERVERS
echo ========================================
echo.

echo [1/4] Starting Camera API Server...
start cmd /k "cd /d C:\Project\pregnant module && echo Camera API Server starting on port 5001... && python run_all.py"
timeout /t 3

echo [2/4] Starting Flask ML Server...
start cmd /k "cd /d C:\Users\Aadhi\Downloads\aarogya-abhaya (2)\flask-ml-server && echo Flask ML Server starting on port 5000... && python app.py"
timeout /t 3

echo [3/4] Starting Malnutrition App...
start cmd /k "cd /d C:\Users\Aadhi\Downloads\aarogya-abhaya (2)\flask-ml-server && echo Malnutrition App starting on port 8501... && streamlit run malnutrition_app.py"
timeout /t 3

echo [4/4] Starting Website Server...
cd /d C:\Users\Aadhi\Downloads\aarogya-abhaya (2)\aarogya-abhaya\aarogya-backend
start cmd /k "echo Website Server starting on port 3000... && node server.js"
timeout /t 3

echo.
echo ========================================
echo    ✅ ALL SERVERS STARTED!
echo ========================================
echo.
echo Server URLs:
echo   🔵 Camera API:    http://localhost:5001
echo   🟢 Flask ML:      http://localhost:5000
echo   🏥 Malnutrition:  http://localhost:8501
echo   🌐 Website:       http://localhost:3000
echo.
start http://localhost:3000
echo.
pause