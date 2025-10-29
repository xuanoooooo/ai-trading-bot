@echo off
chcp 65001 >nul
title AI交易机器人 - 运行中

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🤖 AI交易机器人 - 启动程序
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Python！
    echo 请先运行 "一键安装.bat" 安装环境
    echo.
    pause
    exit /b 1
)

:: 检查.env文件
if not exist ".env" (
    echo ❌ 错误：未找到.env配置文件！
    echo.
    echo 请先配置.env文件：
    echo 1. 找到项目目录下的 .env 文件
    echo 2. 用记事本打开
    echo 3. 填入您的API密钥
    echo 4. 保存文件
    echo.
    pause
    exit /b 1
)

:: 检查.env是否已配置
findstr /C:"DEEPSEEK_API_KEY=" .env | findstr /V /C:"DEEPSEEK_API_KEY=$" >nul
if errorlevel 1 (
    echo ⚠️  警告：.env文件中的DEEPSEEK_API_KEY似乎未配置！
    echo.
    echo 请检查.env文件并填入正确的API密钥
    echo.
    pause
)

findstr /C:"BINANCE_API_KEY=" .env | findstr /V /C:"BINANCE_API_KEY=$" >nul
if errorlevel 1 (
    echo ⚠️  警告：.env文件中的BINANCE_API_KEY似乎未配置！
    echo.
    echo 请检查.env文件并填入正确的API密钥
    echo.
    pause
)

echo ✅ 环境检查通过
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 正在启动AI交易机器人...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 提示：
echo - 保持此窗口打开以持续运行
echo - 按 Ctrl+C 可以停止程序
echo - 日志文件保存在：bnb_trader.log
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 切换到src目录并运行
cd /d "%~dp0..\src"
python deepseekBNB.py

if errorlevel 1 (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ❌ 程序异常退出！
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 可能的原因：
    echo 1. API密钥配置错误
    echo 2. 网络连接问题
    echo 3. 币安API权限不足
    echo 4. Python依赖包缺失
    echo.
    echo 解决方案：
    echo 1. 检查.env文件中的API密钥是否正确
    echo 2. 检查网络是否能访问币安API
    echo 3. 确认币安API已开启"合约交易"权限
    echo 4. 重新运行"一键安装.bat"
    echo.
    echo 详细错误信息请查看上方输出
    echo.
)

pause

