#!/bin/bash
# 🚀 AI Trading Bot Startup Script
# 🚀 AI交易机器人启动脚本
# Automatically start trading bot with tmux session management support
# 自动启动交易机器人，支持tmux会话管理

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置参数
SESSION_NAME="ai-trading-bot"
SCRIPT_NAME="deepseekBNB.py"
VENV_PATH="venv"
LOG_FILE="trading_bot.log"
USE_VENV=false  # 设置为false则直接使用系统python3

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    print_info "检查运行环境..."
    
    # 检查是否在项目根目录
    if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 检查虚拟环境（如果启用）
    if [ "$USE_VENV" = true ] && [ ! -d "$VENV_PATH" ]; then
        print_error "虚拟环境不存在，请先运行 ./scripts/setup.sh"
        print_info "或者设置 USE_VENV=false 直接使用系统Python3"
        exit 1
    fi
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        print_error "未找到python3命令"
        exit 1
    fi
    
    # 检查主脚本
    if [ ! -f "src/$SCRIPT_NAME" ]; then
        print_error "未找到主脚本文件: src/$SCRIPT_NAME"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        print_warning "未找到.env文件，请先配置API密钥"
        print_info "可以复制 config/env.example 为 .env 并编辑"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 检查API密钥
check_api_keys() {
    print_info "检查API密钥配置..."
    
    # 检查.env文件中的API密钥
    if grep -q "your_.*_api_key_here" .env; then
        print_error "请先编辑.env文件，填入您的真实API密钥"
        print_info "编辑命令: nano .env"
        exit 1
    fi
    
    # 检查必需的API密钥
    if ! grep -q "DEEPSEEK_API_KEY=" .env || ! grep -q "BINANCE_API_KEY=" .env || ! grep -q "BINANCE_SECRET=" .env; then
        print_error ".env文件中缺少必需的API密钥"
        exit 1
    fi
    
    print_success "API密钥配置检查通过"
}

# 检查tmux
check_tmux() {
    if command -v tmux &> /dev/null; then
        print_success "tmux已安装"
        return 0
    else
        print_warning "未安装tmux，建议安装以支持远程会话管理"
        print_info "安装命令:"
        print_info "  Ubuntu/Debian: sudo apt install tmux"
        print_info "  CentOS/RHEL: sudo yum install tmux"
        print_info "  macOS: brew install tmux"
        return 1
    fi
}

# 启动机器人（直接模式）
start_direct() {
    print_info "直接启动交易机器人..."
    
    # 激活虚拟环境（如果启用）
    if [ "$USE_VENV" = true ]; then
        source $VENV_PATH/bin/activate
        PYTHON_CMD="python"
    else
        PYTHON_CMD="python3"
    fi
    
    # 启动机器人
    print_success "启动交易机器人..."
    $PYTHON_CMD src/$SCRIPT_NAME
}

# 启动机器人（tmux模式）
start_tmux() {
    print_info "使用tmux启动交易机器人..."
    
    # 检查是否已有同名会话
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        print_warning "会话 $SESSION_NAME 已存在"
        print_info "选择操作:"
        print_info "1. 连接到现有会话"
        print_info "2. 终止现有会话并创建新会话"
        print_info "3. 退出"
        read -p "请选择 (1-3): " choice
        
        case $choice in
            1)
                print_info "连接到现有会话..."
                tmux attach -t $SESSION_NAME
                return
                ;;
            2)
                print_info "终止现有会话..."
                tmux kill-session -t $SESSION_NAME
                ;;
            3)
                print_info "退出"
                exit 0
                ;;
            *)
                print_error "无效选择"
                exit 1
                ;;
        esac
    fi
    
    # 创建新会话
    print_info "创建新tmux会话: $SESSION_NAME"
    tmux new-session -d -s $SESSION_NAME
    
    # 在tmux中运行命令
    tmux send-keys -t $SESSION_NAME "cd $(pwd)" Enter
    
    # 激活虚拟环境（如果启用）
    if [ "$USE_VENV" = true ]; then
        tmux send-keys -t $SESSION_NAME "source $VENV_PATH/bin/activate" Enter
        tmux send-keys -t $SESSION_NAME "python src/$SCRIPT_NAME" Enter
    else
        tmux send-keys -t $SESSION_NAME "python3 src/$SCRIPT_NAME" Enter
    fi
    
    print_success "交易机器人已在tmux会话中启动"
    print_info "会话名称: $SESSION_NAME"
    print_info "连接命令: tmux attach -t $SESSION_NAME"
    print_info "断开会话: Ctrl+b 然后按 d"
    print_info "终止会话: tmux kill-session -t $SESSION_NAME"
    
    # 询问是否立即连接
    read -p "是否立即连接到会话？(y/N): " connect
    if [[ "$connect" =~ ^[Yy]$ ]]; then
        tmux attach -t $SESSION_NAME
    fi
}

# 显示状态
show_status() {
    print_info "检查机器人状态..."
    
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        print_success "机器人正在运行 (tmux会话: $SESSION_NAME)"
        
        # 显示会话信息
        tmux list-sessions | grep $SESSION_NAME
        
        # 显示日志文件大小
        if [ -f "$LOG_FILE" ]; then
            LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
            print_info "日志文件大小: $LOG_SIZE"
        fi
        
        # 显示最近的日志
        if [ -f "$LOG_FILE" ]; then
            print_info "最近日志 (最后5行):"
            tail -5 "$LOG_FILE"
        fi
    else
        print_warning "机器人未运行"
    fi
}

# 停止机器人
stop_bot() {
    print_info "停止交易机器人..."
    
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        # 发送Ctrl+C信号
        tmux send-keys -t $SESSION_NAME C-c
        sleep 2
        
        # 终止会话
        tmux kill-session -t $SESSION_NAME
        print_success "机器人已停止"
    else
        print_warning "机器人未运行"
    fi
}

# 显示帮助
show_help() {
    echo "🚀 AI交易机器人启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start       启动机器人 (默认)"
    echo "  start-tmux  使用tmux启动机器人"
    echo "  start-direct 直接启动机器人"
    echo "  status      显示机器人状态"
    echo "  stop        停止机器人"
    echo "  restart     重启机器人"
    echo "  logs        查看日志"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start-tmux    # 使用tmux启动"
    echo "  $0 status        # 查看状态"
    echo "  $0 logs          # 查看日志"
    echo ""
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_info "显示日志文件 (按Ctrl+C退出):"
        tail -f "$LOG_FILE"
    else
        print_warning "日志文件不存在: $LOG_FILE"
    fi
}

# 重启机器人
restart_bot() {
    print_info "重启交易机器人..."
    stop_bot
    sleep 2
    start_tmux
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            check_environment
            check_api_keys
            if check_tmux; then
                start_tmux
            else
                print_warning "tmux不可用，使用直接模式启动"
                start_direct
            fi
            ;;
        "start-tmux")
            check_environment
            check_api_keys
            if check_tmux; then
                start_tmux
            else
                print_error "tmux不可用，请先安装tmux"
                exit 1
            fi
            ;;
        "start-direct")
            check_environment
            check_api_keys
            start_direct
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_bot
            ;;
        "restart")
            restart_bot
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
