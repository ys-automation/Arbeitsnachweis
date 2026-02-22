@echo off
setlocal
cd /d "%~dp0"

set HOST=127.0.0.1
set PORT=8080
set URL=http://%HOST%:%PORT%/
set PYTHON_FOUND=0

where python >nul 2>nul
if %errorlevel%==0 (
  set PYTHON_FOUND=1
  echo Starte lokalen Server mit Python auf %URL% ...
  call :start_and_open "python -m http.server %PORT%"
  if %errorlevel%==0 goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
  set PYTHON_FOUND=1
  echo Starte lokalen Server mit py -3 auf %URL% ...
  call :start_and_open "py -3 -m http.server %PORT%"
  if %errorlevel%==0 goto :eof
)

if "%PYTHON_FOUND%"=="1" (
  echo Lokaler Server konnte nicht gestartet werden. Starte Direktmodus...
) else (
  echo Starte Direktmodus...
)
echo Hinweis: Ohne Server sind App-Installation und Offline-Cache deaktiviert.
start "" "%~dp0index.html"
goto :eof

:start_and_open
start "Arbeitsnachweis-Server" cmd /k %~1
call :wait_for_server
if %errorlevel%==0 (
  start "" "%URL%"
  exit /b 0
)
exit /b 1

:wait_for_server
for /L %%i in (1,1,8) do (
  powershell -NoProfile -Command "$c = New-Object Net.Sockets.TcpClient; try { $c.Connect('%HOST%', %PORT%); exit 0 } catch { exit 1 } finally { $c.Close() }" >nul 2>nul
  if not errorlevel 1 exit /b 0
  timeout /t 1 >nul
)
exit /b 1
