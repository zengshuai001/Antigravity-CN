@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Antigravity 还原英文版
echo ========================================================
echo          Antigravity 还原回滚为官方英文版
echo ========================================================
echo.
echo 请先彻底关闭 Antigravity 客户端。
echo 关闭后按任意键继续...
pause >nul
echo.
echo [*] 正在从备份恢复英文原版...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\apply.ps1" -Restore
echo.
echo 操作完成。请重新打开 Antigravity 查看原版效果。
pause
