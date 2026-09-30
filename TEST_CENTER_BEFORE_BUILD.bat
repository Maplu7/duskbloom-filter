@echo off
setlocal
cd /d "%~dp0"
title DuskBloom Center Pre-Build Test
if not exist venv_build\Scripts\python.exe (
  py -m venv venv_build
  call venv_build\Scripts\activate.bat
  python -m pip install --disable-pip-version-check -q wxPython
) else (
  call venv_build\Scripts\activate.bat
)
echo.
echo Starting Center directly from Python...
python DuskBloomCenter.py
echo.
echo Center exited with code %ERRORLEVEL%.
pause
