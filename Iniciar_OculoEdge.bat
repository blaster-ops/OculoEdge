@echo off
setlocal
cd /d "%~dp0"
if exist "runtime\python.exe" (
  "runtime\python.exe" run.py %*
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run.py %*
) else (
  echo Instale primero con Instalar_OculoEdge.bat o use el paquete portable.
  pause
  exit /b 1
)
if errorlevel 1 pause
