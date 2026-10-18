@echo off
chcp 65001 >nul
title Google Antigravity 发布至 GitHub
cd /d "%~dp0"

echo ================================================================
echo           Google Antigravity 一键创建并发布至 GitHub
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

echo [错误] 未在系统 PATH 中找到 Python 3！
echo 请确保 Python 已正确安装并添加到系统环境变量。
echo.
pause
exit /b 1

:FOUND_PY
"%PY_CMD%" "%~dp0publish_github.py"

echo.
pause
