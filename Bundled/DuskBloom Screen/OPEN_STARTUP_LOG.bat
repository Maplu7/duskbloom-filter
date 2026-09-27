@echo off
set "P=%APPDATA%\DuskBloom\DuskBloomScreen\startup.txt"
if exist "%P%" (
  notepad "%P%"
) else (
  echo No startup log exists yet.
  echo Path: %P%
  pause
)
