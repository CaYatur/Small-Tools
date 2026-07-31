@echo off
setlocal
cd /d "%~dp0"
set "PS51=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS51%" (
  echo Windows PowerShell 5.1 bulunamadi.
  pause
  exit /b 1
)
start "CaYa Virtual Voice" "%PS51%" -NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File "%~dp0CaYaVirtualVoice.ps1"
endlocal
