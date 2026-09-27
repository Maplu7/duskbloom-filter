@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo        DuskBloom Screen Builder
echo ==========================================
py -m pip install --upgrade pip
if errorlevel 1 goto :error
py -m pip install -r requirements.txt
if errorlevel 1 goto :error
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DuskBloomScreen src\DuskBloomScreen.py
if errorlevel 1 goto :error
echo.
echo Build complete: dist\DuskBloomScreen.exe
pause
exit /b 0
:error
echo.
echo Build failed.
pause
exit /b 1
