@echo off
setlocal
cd /d "%~dp0"
title DuskBloom 2.1 Windows EXE Builder

if not exist venv_release\Scripts\python.exe py -m venv venv_release || goto fail
call venv_release\Scripts\activate.bat
python -m pip install --disable-pip-version-check -q --upgrade pip pyinstaller wxPython pystray pillow pymupdf python-docx pyttsx3 || goto fail

if exist release_exes rmdir /S /Q release_exes
mkdir release_exes

echo [1/4] Building DuskBloom Screen...
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomScreen --distpath "release_exes" --workpath "build_release\screen" "Bundled\DuskBloom Screen\DuskBloomScreen.py" || goto fail

echo [2/4] Building DuskBloom Reader...
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomReader --distpath "release_exes" --workpath "build_release\reader" "Bundled\DuskBloom Reader\DuskBloomReader.py" || goto fail

echo [3/4] Building DuskBloom Sonar...
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomSonar --distpath "release_exes" --workpath "build_release\sonar" "Bundled\DuskBloom Sonar\duskbloom_sonar_v15_2.py" || goto fail

rem Put standalone EXEs into Center's bundle before Center is frozen.
copy /Y "release_exes\DuskBloomScreen.exe" "Bundled\DuskBloom Screen\DuskBloomScreen.exe" >nul || goto fail
copy /Y "release_exes\DuskBloomReader.exe" "Bundled\DuskBloom Reader\DuskBloomReader.exe" >nul || goto fail
copy /Y "release_exes\DuskBloomSonar.exe" "Bundled\DuskBloom Sonar\DuskBloomSonar.exe" >nul || goto fail

echo [4/4] Building DuskBloom Center as one standalone EXE...
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomCenter --distpath "release_exes" --workpath "build_release\center" --add-data "Bundled;Bundled" --add-data "update_catalog.json;." DuskBloomCenter.py || goto fail

powershell -NoProfile -Command "Compress-Archive -Path 'release_exes\*' -DestinationPath 'DuskBloom_Windows_v2.1.0_EXEs.zip' -Force" || goto fail

echo.
echo DONE. Standalone EXEs:
dir /B release_exes\*.exe
echo ZIP: DuskBloom_Windows_v2.1.0_EXEs.zip
exit /b 0

:fail
echo BUILD FAILED. Keep this window open and copy the error.
exit /b 1
