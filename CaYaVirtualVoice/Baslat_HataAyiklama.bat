@echo off
setlocal
cd /d "%~dp0"
set "PS51=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
"%PS51%" -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0CaYaVirtualVoice.ps1"
echo.
echo Uygulama kapandi. Bir hata varsa yukarida gorunur.
pause
endlocal
