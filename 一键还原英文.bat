@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Google Antigravity 一键还原原版英文
cd /d "%~dp0"

echo ================================================================
echo           Google Antigravity 一键还原回滚至官方原版英文
echo ================================================================
echo.
echo [*] 正在检测系统 Python 环境...

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

echo.
echo [错误] 未在系统中检测到 Python 3 环境！
echo ----------------------------------------------------------------
echo 提示：请确保系统已安装 Python 并已添加至环境变量。
echo ----------------------------------------------------------------
echo.
pause
exit /b 1

:FOUND_PY
echo [+] 已找到 Python 运行环境: %PY_CMD%
echo [*] 正在执行原版回滚程序...
echo.
"%PY_CMD%" "%~dp0auto_localize.py" --restore

echo.
pause
