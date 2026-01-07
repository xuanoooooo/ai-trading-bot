#!/bin/bash

# AI Trading 看板启动脚本

SESSION_NAME="web-dashboard"
# 获取脚本所在的目录 (即 web/ 目录)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")" # 项目根目录

echo "============================================"
echo "📊 AI Trading 看板启动器"
echo "============================================"

# 检查是否已有运行中的会话
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "⚠️  检测到已存在的 '$SESSION_NAME' 看板会话"
    echo ""
    echo "请选择操作:"
    echo "1) 连接到现有会话 (查看看板日志)"
    echo "2) 终止并重启看板"
    echo "3) 取消操作"
    echo ""
    read -p "请输入选项 (1/2/3): " choice
    
    case $choice in
        1)
            echo "📺 连接到现有看板会话..."
            tmux attach -t $SESSION_NAME
            exit 0
            ;;
        2)
            echo "🛑 终止现有看板会话..."
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
echo "📂 切换到前端工作目录并构建..."
# 先进入前端目录构建
tmux send-keys -t $SESSION_NAME "cd $SCRIPT_DIR/ui" C-m
tmux send-keys -t $SESSION_NAME "echo '⏳ 正在构建前端...'" C-m
tmux send-keys -t $SESSION_NAME "npm run build" C-m

# 构建完成后，回到根目录启动后端
# 注意：这里我们简单地顺序发送命令。如果前端构建失败，后端启动可能会有问题，
# 但在tmux中，这通常意味着你会看到错误信息。
tmux send-keys -t $SESSION_NAME "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME "echo '🚀 启动 Flask 后端...'" C-m
tmux send-keys -t $SESSION_NAME "python3 web/web_app.py" C-m

echo ""
echo "✅ 看板启动指令已发送！"
echo "前端构建可能需要几秒钟，请稍候..."
echo ""
echo "============================================"
echo "📋 常用 tmux 命令 (看板会话: $SESSION_NAME)"
echo "============================================"
echo "连接会话: tmux attach -t $SESSION_NAME"
echo "断开会话: Ctrl+B 然后按 D"
echo "停止程序: Ctrl+C (在会话内)"
echo "查看所有会话: tmux ls"
echo "终止会话: tmux kill-session -t $SESSION_NAME"
echo "============================================"
echo ""

# 自动连接到新创建的会话
echo "🔗 正在连接到看板会话..."
sleep 1
tmux attach -t $SESSION_NAME