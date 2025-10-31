#!/bin/bash

echo "🛑 停止看板程序..."

# 查找并停止web_app进程
pkill -f web_app.py

if [ $? -eq 0 ]; then
    echo "✅ 看板程序已停止"
else
    echo "⚠️  看板程序未运行或已停止"
fi

# 等待进程完全停止
sleep 1

# 验证是否已停止
if ps aux | grep -v grep | grep web_app.py > /dev/null; then
    echo "⚠️  进程仍在运行，尝试强制停止..."
    pkill -9 -f web_app.py
    sleep 1
    echo "✅ 已强制停止"
else
    echo "✅ 进程已完全停止"
fi

