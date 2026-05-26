@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
  set "PYTHON_EXE=c:\python313\python.exe"
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":5000 .*LISTENING"') do (
  taskkill /PID %%p /F >nul 2>nul
)

start "" "http://127.0.0.1:5000/login"
"%PYTHON_EXE%" app_web.py

endlocal
