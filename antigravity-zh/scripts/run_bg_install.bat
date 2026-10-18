@echo off
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

if "%ANTIGRAVITY_PATH%"=="" (
    set "AG_PATH=%LOCALAPPDATA%\Programs\Antigravity"
) else (
    set "AG_PATH=%ANTIGRAVITY_PATH%"
)

start "" python "%SCRIPT_DIR%bg_install.py" %1 "%AG_PATH%" "%PROJECT_ROOT%" %2 %3 %4 %5 %6 %7 %8 %9
