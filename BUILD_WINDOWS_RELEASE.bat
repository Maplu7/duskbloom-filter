@echo off
setlocal
cd /d "%~dp0"
title DuskBloom 2.0 Windows Release Builder
if not exist venv_release\Scripts\python.exe py -m venv venv_release || goto fail
call venv_release\Scripts\activate.bat
python -m pip install --disable-pip-version-check -q --upgrade pip pyinstaller wxPython pystray pillow pymupdf python-docx pyttsx3 || goto fail
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomScreen --distpath "Bundled\DuskBloom Screen\dist_release" --workpath "build_release\screen" "Bundled\DuskBloom Screen\DuskBloomScreen.py" || goto fail
copy /Y "Bundled\DuskBloom Screen\dist_release\DuskBloomScreen.exe" "Bundled\DuskBloom Screen\DuskBloomScreen.exe" >nul || goto fail
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomReader --distpath "Bundled\DuskBloom Reader\dist_release" --workpath "build_release\reader" "Bundled\DuskBloom Reader\DuskBloomReader.py" || goto fail
copy /Y "Bundled\DuskBloom Reader\dist_release\DuskBloomReader.exe" "Bundled\DuskBloom Reader\DuskBloomReader.exe" >nul || goto fail
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomSonar --distpath "Bundled\DuskBloom Sonar\dist_release" --workpath "build_release\sonar" "Bundled\DuskBloom Sonar\duskbloom_sonar_v15_2.py" || goto fail
copy /Y "Bundled\DuskBloom Sonar\dist_release\DuskBloomSonar.exe" "Bundled\DuskBloom Sonar\DuskBloomSonar.exe" >nul || goto fail
python -m PyInstaller --noconfirm --clean --windowed --onedir --name DuskBloomCenter --distpath "release_v210" --workpath "build_release\center" --add-data "Bundled;Bundled" --add-data "update_catalog.json;." DuskBloomCenter.py || goto fail
powershell -NoProfile -Command "Compress-Archive -Path 'release_v210\DuskBloomCenter\*' -DestinationPath 'DuskBloom_Windows_v2.1.0.zip' -Force" || goto fail
echo DONE: DuskBloom_Windows_v2.1.0.zip
exit /b 0
:fail
echo BUILD FAILED. Keep this window open and copy the error.
pause
exit /b 1
