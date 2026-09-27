@echo off
cd /d "%~dp0"
py -3 duskbloom_sonar_v15_2.py
echo.
echo Send sonar_widget_log.txt if the mixer values stop updating.
pause
