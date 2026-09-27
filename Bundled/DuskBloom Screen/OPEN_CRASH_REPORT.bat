@echo off
set "P=%APPDATA%\DuskBloom\DuskBloomScreen\crash.txt"
if exist "%P%" (
  notepad "%P%"
) else (
  echo No crash report exists.
  pause
)
