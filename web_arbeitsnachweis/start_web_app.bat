@echo off
setlocal
cd /d "%~dp0"

set PORT=8080

where python >nul 2>nul
if %errorlevel%==0 (
  start "" "http://localhost:%PORT%/"
  echo Starte lokalen Server mit Python auf Port %PORT% ...
  python -m http.server %PORT%
  goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
  start "" "http://localhost:%PORT%/"
  echo Starte lokalen Server mit py -3 auf Port %PORT% ...
  py -3 -m http.server %PORT%
  goto :eof
)

echo Python wurde nicht gefunden.
echo Bitte Python installieren oder manuell einen lokalen Server starten.
pause
