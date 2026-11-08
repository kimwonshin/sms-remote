@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv
  if errorlevel 1 py -3.12 -m venv .venv
  if errorlevel 1 py -3.10 -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
if not exist "client-config.json" copy "client-config.example.json" "client-config.json" >nul
echo Setup complete. Run remote_test.cmd.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.10, 3.11 or 3.12 and retry.
pause
exit /b 1
