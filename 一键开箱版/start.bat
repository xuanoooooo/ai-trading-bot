@echo off
chcp 65001 >nul
echo ========================================
echo  🚀 AI交易机器人 - 启动程序
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python，请先安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/4] 检查文件...
if not exist "src\portfolio_manager.py" (
    echo ❌ 文件缺失，请确保在一键开箱版目录下运行
    pause
    exit /b 1
)
echo ✅ 文件检查通过

echo.
echo [3/4] 安装依赖包（首次运行需要几分钟）...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ⚠️ 依赖安装可能有警告，但会尝试继续运行
)
echo ✅ 依赖安装完成

echo.
echo [4/4] 启动交易程序...
cd src
python portfolio_manager.py

pause
