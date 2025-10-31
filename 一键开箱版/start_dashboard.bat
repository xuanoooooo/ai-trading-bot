@echo off
chcp 65001 >nul
echo ========================================
echo  🎨 AI交易机器人 - 启动看板
echo ========================================
echo.

echo [1/2] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/3] 安装依赖包（首次运行需要几分钟）...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ⚠️ 依赖安装可能有警告，但会尝试继续运行
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 启动看板程序...
cd dashboard
start "AI交易看板" python web_app.py

echo.
echo ✅ 看板已启动！
echo 📊 请在浏览器访问: http://localhost:5000
echo.
pause
