@echo off
setlocal
cd /d "%~dp0"
title DuskBloom Update Helper
echo.
echo ==========================================
echo       DuskBloom Component Update
echo ==========================================
echo.
echo Put the NEW component ZIP in this folder first.
echo Then update update_catalog.json with its new version and URL/path.
echo.
echo Current catalog:
type update_catalog.json
echo.
echo Center's updater reads update_catalog.json and compares versions.
echo For friends/family, the ZIP must live at a reachable HTTPS download URL.
echo.
pause
