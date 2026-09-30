@echo off
setlocal
cd /d "%~dp0"
if not exist venv_build\Scripts\python.exe py -m venv venv_build || goto fail
call venv_build\Scripts\activate.bat
python -m pip install --disable-pip-version-check -q --upgrade pip pyinstaller || goto fail
python -m py_compile duskbloom_sonar_v15_2.py || goto fail
python -m PyInstaller --noconfirm --clean --windowed --onefile --name DuskBloomSonar duskbloom_sonar_v15_2.py || goto fail
copy /Y "dist\DuskBloomSonar.exe" ".\DuskBloomSonar.exe" >nul || goto fail
exit /b 0
:fail
echo DuskBloom Sonar build failed.
exit /b 1
