@echo off
setlocal
cd /d "%~dp0"
title DuskBloom Center Builder
color 0D

echo.
echo ==========================================
echo        DuskBloom Center v1.0.4
echo        stable build + install + app detection
echo ==========================================
echo.

taskkill /F /IM DuskBloomCenter.exe >nul 2>&1
if exist build rmdir /s /q build
if exist DuskBloomCenter.spec del /q DuskBloomCenter.spec

if not exist venv_build\Scripts\python.exe (
 echo [1/4] Creating private build environment...
 py -m venv venv_build || goto fail
) else ( echo [1/4] Build environment ready. )
call venv_build\Scripts\activate.bat

echo [2/4] Preparing build tools...
python -m pip install --disable-pip-version-check -q --upgrade pip || goto fail
python -m pip install --disable-pip-version-check -q pyinstaller wxPython || goto fail

echo [3/4] Checking DuskBloom Center...
python -m py_compile DuskBloomCenter.py || goto fail

echo [4/4] Building DuskBloom Center + bundled apps...
if exist "release_v104" rmdir /s /q "release_v104"
python -m PyInstaller --noconfirm --clean --windowed --distpath "release_v104" --workpath "build_v103" --name DuskBloomCenter --add-data "Bundled;Bundled" --add-data "update_catalog.json;." DuskBloomCenter.py || goto fail

if not exist "release_v104\DuskBloomCenter\DuskBloomCenter.exe" goto fail
REM PyInstaller 6 normally places data in _internal; Center supports both layouts.
if exist "release_v104\DuskBloomCenter\_internal\Bundled\DuskBloom Screen" goto bundles_ok
if exist "release_v104\DuskBloomCenter\Bundled\DuskBloom Screen" goto bundles_ok
echo ERROR: Bundled component data was not copied into the built app.
goto fail

:bundles_ok
echo.
echo ==========================================
echo   DUSKBLOOM CENTER IS READY
echo ==========================================
echo Screen 3.4.4, Web 1.1, Sonar 15.2 included.
echo Existing apps in %%LOCALAPPDATA%%\DuskBloom\Apps are detected too.
echo Opening Center now...
start "" "release_v104\DuskBloomCenter\DuskBloomCenter.exe"
exit /b 0

:fail
echo.
echo ==========================================
echo   BUILD FAILED
echo ==========================================
echo Copy the error above and send it to me.
pause
exit /b 1
