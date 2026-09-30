@echo off
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (start "" pyw -3 duskbloom_sonar_v15_2.py & exit /b)
where pythonw >nul 2>nul
if %errorlevel%==0 (start "" pythonw duskbloom_sonar_v15_2.py & exit /b)
echo Python 3 was not found.
pause
