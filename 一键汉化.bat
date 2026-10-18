@echo off
chcp 65001 >nul
title Google Antigravity 中文本地化一键启动器
cd /d "%~dp0"

echo ================================================================
echo           Google Antigravity 界面中文本地化工具
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

:: 尝试在常见默认安装路径中查找 python.exe
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
echo 提示：
echo 1. 请前往 Python 官方网站下载安装：https://www.python.org/downloads/
echo 2. 安装时请务必勾选：[Add python.exe to PATH] (将 Python 添加到环境变量)
echo ----------------------------------------------------------------
echo.
pause
exit /b 1

:FOUND_PY
echo [+] 已找到 Python 运行环境: %PY_CMD%
echo.
"%PY_CMD%" "%~dp0auto_localize.py" %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [提示] 程序执行退出，退出码: %ERRORLEVEL%
    pause
)
