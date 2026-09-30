@echo off
setlocal
cd /d "%~dp0"
title DuskBloom Center Debug
if exist "dist\DuskBloomCenter\DuskBloomCenter.exe" (
  echo Starting built Center...
  "dist\DuskBloomCenter\DuskBloomCenter.exe"
  echo.
  echo Exit code: %ERRORLEVEL%
) else (
  echo Built Center was not found.
)
echo.
if exist "%APPDATA%\DuskBloom\Center\launch_error.txt" (
 echo ===== launch_error.txt =====
 type "%APPDATA%\DuskBloom\Center\launch_error.txt"
)
if exist "launch_error.txt" (
 echo ===== local launch_error.txt =====
 type "launch_error.txt"
)
if exist "web_guardian_error.txt" (
 echo ===== web_guardian_error.txt =====
 type "web_guardian_error.txt"
)
pause
