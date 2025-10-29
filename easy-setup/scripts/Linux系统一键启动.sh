#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 AI交易机器人 - Linux系统一键启动脚本
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 使用方法：
# 1. 打开终端
# 2. 进入项目目录：cd /path/to/ai-trading-bot
# 3. 给脚本执行权限：chmod +x scripts/Linux系统一键启动.sh
# 4. 运行脚本：bash scripts/Linux系统一键启动.sh
#    或者：./scripts/Linux系统一键启动.sh
#
# 停止程序：
# - 按 Ctrl+C
#
# 后台运行（可选）：
# - nohup bash scripts/Linux系统一键启动.sh > trading.log 2>&1 &
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

print_box() {
    echo ""
    echo "┌────────────────────────────────────────────────────────────┐"
    echo -e "│ ${MAGENTA}$1${NC}"
    echo "└────────────────────────────────────────────────────────────┘"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_tip() {
    echo -e "${BLUE}💡 $1${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

print_header "🤖 AI交易机器人 - Linux系统启动程序"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 检查Python环境
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_info "检查Python环境..."

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
else
    print_error "未检测到Python！"
    echo ""
    print_info "请先运行安装脚本："
    echo "  ${CYAN}bash scripts/Linux系统一键安装.sh${NC}"
    echo ""
    exit 1
fi

print_success "$PYTHON_VERSION"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 检查项目文件
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_info "检查项目文件..."

if [ ! -d "src" ]; then
    print_error "未找到src目录！"
    echo ""
    print_info "请确保在正确的项目目录下运行此脚本"
    echo "当前目录: $(pwd)"
    echo ""
    exit 1
fi

if [ ! -f "src/deepseekBNB.py" ]; then
    print_error "未找到主程序文件 src/deepseekBNB.py！"
    echo ""
    exit 1
fi

print_success "项目文件检查通过"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 检查.env配置文件
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_info "检查配置文件..."

if [ ! -f ".env" ]; then
    print_error "未找到.env配置文件！"
    echo ""
    print_info "请先配置.env文件："
    echo ""
    echo "1️⃣  复制示例文件（如果有）："
    echo "   ${CYAN}cp config/env.example .env${NC}"
    echo ""
    echo "2️⃣  编辑.env文件："
    echo "   ${CYAN}nano .env${NC}  或  ${CYAN}vim .env${NC}"
    echo ""
    echo "3️⃣  填入您的API密钥："
    echo "   DEEPSEEK_API_KEY=sk-你的密钥"
    echo "   BINANCE_API_KEY=你的密钥"
    echo "   BINANCE_SECRET=你的密钥"
    echo ""
    echo "4️⃣  保存文件："
    echo "   nano: Ctrl+X, 然后Y, 然后Enter"
    echo "   vim: 按ESC, 然后输入:wq, 然后Enter"
    echo ""
    exit 1
fi

print_success "找到.env配置文件"

# 检查.env是否已配置（简单检查）
if grep -q "^DEEPSEEK_API_KEY=$" .env || ! grep -q "^DEEPSEEK_API_KEY=" .env; then
    echo ""
    print_warning "DEEPSEEK_API_KEY 似乎未配置！"
    echo ""
    print_info "请编辑.env文件并填入正确的API密钥："
    echo "  ${CYAN}nano .env${NC}"
    echo ""
    
    read -p "是否继续运行？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "程序已取消"
        exit 1
    fi
fi

if grep -q "^BINANCE_API_KEY=$" .env || ! grep -q "^BINANCE_API_KEY=" .env; then
    echo ""
    print_warning "BINANCE_API_KEY 似乎未配置！"
    echo ""
    print_info "请编辑.env文件并填入正确的API密钥："
    echo "  ${CYAN}nano .env${NC}"
    echo ""
    
    read -p "是否继续运行？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "程序已取消"
        exit 1
    fi
fi

if grep -q "^BINANCE_SECRET=$" .env || ! grep -q "^BINANCE_SECRET=" .env; then
    echo ""
    print_warning "BINANCE_SECRET 似乎未配置！"
    echo ""
    print_info "请编辑.env文件并填入正确的API密钥："
    echo "  ${CYAN}nano .env${NC}"
    echo ""
    
    read -p "是否继续运行？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "程序已取消"
        exit 1
    fi
fi

echo ""
print_success "配置文件检查通过"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 启动提示
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_header "🚀 正在启动AI交易机器人..."

print_box "💡 使用提示"
echo "  📌 保持此终端窗口打开以持续运行"
echo "  📌 按 ${CYAN}Ctrl+C${NC} 可以停止程序"
echo "  📌 日志文件：${CYAN}bnb_trader.log${NC}"
echo "  📌 决策记录：${CYAN}ai_decisions.json${NC}"
echo ""

print_box "🔧 后台运行方法（可选）"
echo "  如果希望程序在后台运行："
echo "  ${CYAN}nohup bash scripts/Linux系统一键启动.sh > trading.log 2>&1 &${NC}"
echo ""
echo "  查看后台进程："
echo "  ${CYAN}ps aux | grep deepseekBNB${NC}"
echo ""
echo "  停止后台进程："
echo "  ${CYAN}pkill -f deepseekBNB${NC}"
echo ""

print_box "⚠️  重要提醒"
echo "  ✓ 确保币安账户设置为"单向持仓模式""
echo "  ✓ 确保币安API开启"合约交易"权限"
echo "  ✓ 建议使用币安子账户进行交易"
echo "  ✓ 建议先用小额资金测试"
echo ""

print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 启动程序
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 进入src目录
cd src

# 运行程序
$PYTHON_CMD deepseekBNB.py

# 捕获退出状态
EXIT_CODE=$?

# 程序退出后的处理
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    print_header "✅ 程序正常退出"
    echo ""
else
    echo ""
    print_header "❌ 程序异常退出（退出码: $EXIT_CODE）"
    
    echo "可能的原因："
    echo ""
    echo "1️⃣  API密钥配置错误"
    echo "   解决方法：检查.env文件中的密钥是否正确"
    echo "   ${CYAN}nano .env${NC}"
    echo ""
    
    echo "2️⃣  网络连接问题"
    echo "   解决方法：检查网络是否能访问币安API"
    echo "   ${CYAN}ping api.binance.com${NC}"
    echo ""
    
    echo "3️⃣  币安API权限不足"
    echo "   解决方法：登录币安，检查API权限设置"
    echo "   - 确保开启"读取"权限"
    echo "   - 确保开启"合约交易"权限"
    echo ""
    
    echo "4️⃣  Python依赖包缺失"
    echo "   解决方法：重新运行安装脚本"
    echo "   ${CYAN}bash scripts/Linux系统一键安装.sh${NC}"
    echo ""
    
    echo "5️⃣  持仓模式设置错误"
    echo "   解决方法：确保币安账户设置为"单向持仓模式""
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "查看详细错误信息请向上滚动查看终端输出"
    echo "或查看日志文件：${CYAN}cat ../bnb_trader.log${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi





