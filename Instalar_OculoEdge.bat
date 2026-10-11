@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Instale Python 3.13 de python.org o use el paquete portable.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto fail
if exist "wheelhouse" (
  ".venv\Scripts\python.exe" -m pip install --no-index --find-links wheelhouse -r requirements-lock.txt
) else (
  ".venv\Scripts\python.exe" -m pip install -r requirements-lock.txt
)
if errorlevel 1 goto fail
".venv\Scripts\python.exe" run.py --check
if errorlevel 1 goto fail
echo Listo. Abra Iniciar_OculoEdge.bat.
pause
exit /b 0
:fail
echo Instalacion incompleta. Revise el mensaje anterior.
pause
exit /b 1
