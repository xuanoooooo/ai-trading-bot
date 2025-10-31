#!/bin/bash

# AI多币种投资组合管理系统启动脚本

SESSION_NAME="portfolio"
SCRIPT_DIR="/root/ai-trading-bot"

echo "=========================================="
echo "🚀 AI多币种投资组合管理系统"
echo "=========================================="

# 检查是否已有运行中的会话
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "⚠️  检测到已存在的 '$SESSION_NAME' 会话"
    echo ""
    echo "请选择操作:"
    echo "1) 连接到现有会话 (查看运行状态)"
    echo "2) 终止并重启"
    echo "3) 取消"
    echo ""
    read -p "请输入选项 (1/2/3): " choice
    
    case $choice in
        1)
            echo "📺 连接到现有会话..."
            tmux attach -t $SESSION_NAME
            exit 0
            ;;
        2)
            echo "🛑 终止现有会话..."
            tmux kill-session -t $SESSION_NAME
            sleep 1
            ;;
        3)
            echo "❌ 取消操作"
            exit 0
            ;;
        *)
            echo "❌ 无效选项"
            exit 1
            ;;
    esac
fi

# 创建新的tmux会话
echo "🎬 创建新的tmux会话: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME

# 发送命令到tmux会话
echo "📂 切换到工作目录..."
tmux send-keys -t $SESSION_NAME "cd $SCRIPT_DIR" C-m

echo "🚀 启动投资组合管理器..."
tmux send-keys -t $SESSION_NAME "python3 portfolio_manager.py" C-m

sleep 2

echo ""
echo "✅ 启动成功！"
echo ""
echo "=========================================="
echo "📋 常用命令"
echo "=========================================="
echo "连接会话: tmux attach -t $SESSION_NAME"
echo "断开会话: Ctrl+B 然后按 D"
echo "停止程序: Ctrl+C (在会话内)"
echo "查看会话: tmux ls"
echo "终止会话: tmux kill-session -t $SESSION_NAME"
echo "=========================================="
echo ""

# 自动连接到会话
echo "🔗 正在连接到会话..."
sleep 1
tmux attach -t $SESSION_NAME

