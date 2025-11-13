#!/bin/bash

# AI交易机器人可视化Web服务启动脚本

echo "========================================"
echo "🚀 启动AI交易机器人可视化服务"
echo "========================================"

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查是否已有运行中的进程
if pgrep -f "web_app.py" > /dev/null; then
    echo "⚠️  Web服务已在运行"
    read -p "是否停止现有服务并重新启动? (y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "🔄 停止现有服务..."
        pkill -f web_app.py
        sleep 1
    else
        echo "❌ 取消启动"
        exit 0
    fi
fi

echo "🌐 启动Web服务 (端口 5000)..."
echo ""

# 后台启动Web服务
nohup python3 web_app.py > web_app.log 2>&1 &

# 等待1秒让服务启动
sleep 1

# 检查服务是否正常运行
if pgrep -f "web_app.py" > /dev/null; then
    echo "✅ Web服务已成功启动！"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 安全模式: 仅本地访问 (127.0.0.1:5000)"
    echo ""
    echo "📱 访问方式 (通过SSH隧道):"
    echo "   1. 在本地电脑执行:"
    echo "      ssh -L 5000:localhost:5000 root@your-server-ip"
    echo ""
    echo "   2. 保持SSH连接，然后浏览器访问:"
    echo "      http://localhost:5000"
    echo ""
    echo "🔧 管理命令:"
    echo "   停止服务: pkill -f web_app.py"
    echo "   查看日志: tail -f web_app.log"
    echo "   查看进程: ps aux | grep web_app"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  注意: Web服务仅用于监控，不执行交易"
    echo "⚠️  交易程序需要独立启动 (cd ../  && ./start_portfolio.sh)"
    echo ""
    echo "========================================"
else
    echo "❌ Web服务启动失败，请检查日志: tail -f web_app.log"
    exit 1
fi
