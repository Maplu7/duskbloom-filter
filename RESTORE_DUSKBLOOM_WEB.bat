@echo off
setlocal
cd /d "%~dp0"
set "DEST=%APPDATA%\DuskBloom\Web\Firefox-Zen"
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%" >nul 2>&1
xcopy /E /I /Y "Bundled\DuskBloom Web\Firefox-Zen\*" "%DEST%\" >nul
echo.
echo DuskBloom Web restored to:
echo %DEST%
echo.
start "" firefox "about:debugging#/runtime/this-firefox"
echo Choose Load Temporary Add-on and select:
echo %DEST%\manifest.json
pause
