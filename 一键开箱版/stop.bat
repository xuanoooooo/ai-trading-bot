@echo off
chcp 65001 >nul
echo ========================================
echo  🛑 AI交易机器人 - 停止程序
echo ========================================
echo.

echo 正在停止交易程序...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq portfolio_manager*" 2>nul

echo 正在停止看板程序...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq web_app*" 2>nul

echo.
echo ✅ 程序已停止
echo.
pause
