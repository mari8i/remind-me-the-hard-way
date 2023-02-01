@echo off
if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)

schtasks /create /sc ONLOGON /it /tn "Remind me the hard way" /tr "%~dp0start.bat"

echo "Process scheduled"
pause