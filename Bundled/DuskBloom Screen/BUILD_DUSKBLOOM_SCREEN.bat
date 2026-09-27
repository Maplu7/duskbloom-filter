@echo off
setlocal
cd /d "%~dp0"
title DuskBloom Screen Builder
echo.
echo ==========================================
echo          DuskBloom Screen v3.4.4
echo ==========================================
echo.

taskkill /F /IM DuskBloomScreen.exe >nul 2>&1
taskkill /F /IM MellowScreen.exe >nul 2>&1
taskkill /F /IM MigraineFilter.exe >nul 2>&1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist DuskBloomScreen.spec del /q DuskBloomScreen.spec

if not exist venv_build\Scripts\python.exe (
    echo Creating clean build environment...
    py -m venv venv_build
    if errorlevel 1 goto fail
)

call venv_build\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto fail
python -m pip install pyinstaller wxPython pystray pillow
if errorlevel 1 goto fail

echo.
echo Checking DuskBloom Screen...
python -m py_compile DuskBloomScreen.py
if errorlevel 1 goto fail

echo.
echo Building fresh DuskBloomScreen.exe...
python -m PyInstaller --noconfirm --clean --windowed --name DuskBloomScreen DuskBloomScreen.py
if errorlevel 1 goto fail

if exist "dist\DuskBloomScreen\DuskBloomScreen.exe" (
    echo.
    echo ==========================================
    echo      DUSKBLOOM SCREEN IS READY
    echo ==========================================
    start "" "dist\DuskBloomScreen\DuskBloomScreen.exe"
    echo Approve the Windows administrator prompt.
    pause
    exit /b 0
)

:fail
echo.
echo BUILD FAILED.
echo Leave this window open if you need to copy the error.
pause
exit /b 1
