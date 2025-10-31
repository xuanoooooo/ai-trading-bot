#!/bin/bash

echo "🛑 停止交易程序..."

# 查找并停止portfolio_manager进程
pkill -f portfolio_manager.py

if [ $? -eq 0 ]; then
    echo "✅ 交易程序已停止"
else
    echo "⚠️  交易程序未运行或已停止"
fi

# 等待进程完全停止
sleep 1

# 验证是否已停止
if ps aux | grep -v grep | grep portfolio_manager.py > /dev/null; then
    echo "⚠️  进程仍在运行，尝试强制停止..."
    pkill -9 -f portfolio_manager.py
    sleep 1
    echo "✅ 已强制停止"
else
    echo "✅ 进程已完全停止"
fi

