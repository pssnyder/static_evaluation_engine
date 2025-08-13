@echo off
echo 🚀 Chess Engine Analysis Dashboard - Data Refresh
echo ================================================

cd /d "s:\Maker Stuff\Programming\Static Evaluation Chess Engine\static_evaluation_engine\docs"

echo.
echo 📊 Extracting engine data...
python extract_engine_data.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Data extraction completed successfully!
    echo.
    echo 🌐 Opening dashboard in browser...
    start "" "Enhanced_Engine_Analysis_Dashboard.html"
    echo.
    echo 💡 Tip: Use F5 to refresh the dashboard after data updates
) else (
    echo.
    echo ❌ Error occurred during data extraction
    echo Please check the console output above for details
)

echo.
pause
