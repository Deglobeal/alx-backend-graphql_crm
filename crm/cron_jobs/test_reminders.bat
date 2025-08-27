@echo off
echo Testing order reminder script...
echo Log file will be created at: %TEMP%\order_reminders_log.txt

:: Start mock server if not running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "mock_graphql_server.py">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting mock server...
    start python mock_graphql_server.py
    timeout /T 3 > nul
)

:: Run the reminder script
python send_order_reminders.py

:: Show log file contents
echo.
echo Log file contents:
type %TEMP%\order_reminders_log.txt
pause