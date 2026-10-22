@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Google Antigravity Chinese Localization Launcher
cd /d "%~dp0"

echo ================================================================
echo           Google Antigravity 界面中文本地化工具
echo ================================================================
echo.

set "PY_CMD="

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto FOUND_PY
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py"
    goto FOUND_PY
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto FOUND_PY
    )
)
for /d %%D in ("C:\Python3*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto FOUND_PY
    )
)

echo [错误] 未在系统 PATH 中找到 Python 3！
echo 请确保 Python 已正确安装并勾选添加到系统环境变量。
echo.
pause
exit /b 1

:FOUND_PY
"%PY_CMD%" "%~dp0auto_localize.py" %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo Script exited with code %ERRORLEVEL%.
    pause
)
