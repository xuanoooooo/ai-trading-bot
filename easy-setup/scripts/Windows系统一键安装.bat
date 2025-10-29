@echo off
chcp 65001 >nul
title AI交易机器人 - 一键安装

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🤖 AI交易机器人 - 一键安装程序
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 检查Python是否已安装
echo [1/4] 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Python！
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo 下载地址：https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH" 选项！
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python环境检查通过
echo.

:: 检查pip是否可用
echo [2/4] 正在检查pip工具...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：pip未安装或不可用！
    echo 请重新安装Python并确保勾选pip组件
    echo.
    pause
    exit /b 1
)
echo ✅ pip工具检查通过
echo.

:: 检查网络连接
echo [3/4] 正在检查网络连接...
ping -n 1 pypi.org >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：无法连接到PyPI服务器
    echo 如果安装失败，请检查网络连接或使用国内镜像源
    echo.
) else (
    echo ✅ 网络连接正常
    echo.
)

:: 安装依赖包
echo [4/4] 正在安装Python依赖包...
echo 这可能需要1-3分钟，请耐心等待...
echo.

cd /d "%~dp0.."
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败！
    echo.
    echo 可能的解决方案：
    echo 1. 检查网络连接是否正常
    echo 2. 尝试使用国内镜像源：
    echo    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo 3. 以管理员身份运行此脚本
    echo.
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ 安装完成！
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📋 下一步操作：
echo.
echo 1. 编辑 .env 文件，填入您的API密钥
echo    - DeepSeek API Key
echo    - 币安 API Key
echo    - 币安 Secret Key
echo.
echo 2. 确保币安账户设置为"单向持仓模式"
echo.
echo 3. 双击运行 "一键启动.bat" 启动程序
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause

