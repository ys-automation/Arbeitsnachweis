@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Erstelle Release-ZIP ...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\create_release_zip.ps1"
if errorlevel 1 goto :error

echo [2/2] Pruefe ZIP gegen Quellordner ...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\verify_release_zip.ps1"
if errorlevel 1 goto :error

echo Fertig: Release-ZIP erfolgreich erstellt und verifiziert.
exit /b 0

:error
echo FEHLER: Release-ZIP konnte nicht erfolgreich erstellt/verifiziert werden.
exit /b 1
