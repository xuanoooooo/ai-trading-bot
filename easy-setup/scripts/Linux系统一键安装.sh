#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 AI交易机器人 - Linux系统一键安装脚本
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 使用方法：
# 1. 打开终端
# 2. 进入项目目录：cd /path/to/ai-trading-bot
# 3. 给脚本执行权限：chmod +x scripts/Linux系统一键安装.sh
# 4. 运行脚本：bash scripts/Linux系统一键安装.sh
#    或者：./scripts/Linux系统一键安装.sh
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

print_step() {
    echo -e "${BLUE}[$1]${NC} $2"
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

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

print_header "🤖 AI交易机器人 - Linux系统一键安装"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤1: 检测操作系统
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "1/6" "检测操作系统..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
    # 检测Linux发行版
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION
    else
        OS_NAME="Unknown Linux"
        OS_VERSION="Unknown"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
    OS_NAME="macOS"
    OS_VERSION=$(sw_vers -productVersion)
else
    OS_TYPE="Unknown"
    OS_NAME="Unknown"
    OS_VERSION="Unknown"
fi

print_success "操作系统: $OS_NAME $OS_VERSION"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤2: 检查Python环境
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "2/6" "检查Python环境..."

# 检查python3命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_success "$PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
    print_success "$PYTHON_VERSION"
else
    print_error "未检测到Python！"
    echo ""
    print_info "请先安装Python 3.8或更高版本："
    echo ""
    
    if [[ "$OS_TYPE" == "Linux" ]]; then
        if [[ "$OS_NAME" == *"Ubuntu"* ]] || [[ "$OS_NAME" == *"Debian"* ]]; then
            echo "  Ubuntu/Debian系统安装命令："
            echo "  ${CYAN}sudo apt-get update${NC}"
            echo "  ${CYAN}sudo apt-get install python3 python3-pip${NC}"
        elif [[ "$OS_NAME" == *"CentOS"* ]] || [[ "$OS_NAME" == *"Red Hat"* ]]; then
            echo "  CentOS/RHEL系统安装命令："
            echo "  ${CYAN}sudo yum install python3 python3-pip${NC}"
        else
            echo "  请使用系统包管理器安装Python3"
        fi
    elif [[ "$OS_TYPE" == "macOS" ]]; then
        echo "  macOS系统安装命令（需要先安装Homebrew）："
        echo "  ${CYAN}brew install python3${NC}"
        echo ""
        echo "  如果没有Homebrew，请先安装："
        echo "  ${CYAN}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
    fi
    
    echo ""
    exit 1
fi

# 检查Python版本
PYTHON_VERSION_NUM=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION_NUM" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    print_error "Python版本过低！当前版本: $PYTHON_VERSION_NUM，需要: >= $REQUIRED_VERSION"
    echo ""
    exit 1
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤3: 检查pip工具
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "3/6" "检查pip工具..."

# 检查pip3命令
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    PIP_VERSION=$(pip3 --version 2>&1)
    print_success "$PIP_VERSION"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    PIP_VERSION=$(pip --version 2>&1)
    print_success "$PIP_VERSION"
else
    print_error "pip工具未安装或不可用！"
    echo ""
    print_info "请安装pip："
    
    if [[ "$OS_TYPE" == "Linux" ]]; then
        if [[ "$OS_NAME" == *"Ubuntu"* ]] || [[ "$OS_NAME" == *"Debian"* ]]; then
            echo "  ${CYAN}sudo apt-get install python3-pip${NC}"
        elif [[ "$OS_NAME" == *"CentOS"* ]] || [[ "$OS_NAME" == *"Red Hat"* ]]; then
            echo "  ${CYAN}sudo yum install python3-pip${NC}"
        fi
    elif [[ "$OS_TYPE" == "macOS" ]]; then
        echo "  ${CYAN}python3 -m ensurepip --upgrade${NC}"
    fi
    
    echo ""
    exit 1
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤4: 检查网络连接
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "4/6" "检查网络连接..."

if ping -c 1 -W 2 pypi.org &> /dev/null; then
    print_success "网络连接正常"
else
    print_warning "无法连接到PyPI服务器"
    print_info "如果安装失败，可尝试使用国内镜像源"
    echo ""
    echo "  清华大学镜像："
    echo "  ${CYAN}$PIP_CMD install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple${NC}"
    echo ""
    echo "  阿里云镜像："
    echo "  ${CYAN}$PIP_CMD install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/${NC}"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤5: 检查requirements.txt
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "5/6" "检查依赖文件..."

if [ ! -f "requirements.txt" ]; then
    print_error "未找到requirements.txt文件！"
    echo ""
    print_info "请确保在正确的项目目录下运行此脚本"
    echo ""
    exit 1
fi

print_success "找到requirements.txt"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤6: 安装Python依赖包
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print_step "6/6" "安装Python依赖包..."
print_info "这可能需要1-3分钟，请耐心等待..."
echo ""

# 显示将要安装的包
echo "将要安装的依赖包："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat requirements.txt
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 尝试安装
if $PIP_CMD install -r requirements.txt --upgrade; then
    echo ""
    print_header "✅ 安装完成！"
    
    echo "📋 下一步操作："
    echo ""
    echo "1️⃣  配置API密钥"
    echo "   ${CYAN}nano .env${NC}  或  ${CYAN}vim .env${NC}"
    echo "   填入您的DeepSeek和币安API密钥"
    echo ""
    echo "2️⃣  确保币安账户设置"
    echo "   - 设置为"单向持仓模式""
    echo "   - API开启"合约交易"权限"
    echo ""
    echo "3️⃣  启动程序"
    echo "   ${CYAN}bash scripts/Linux系统一键启动.sh${NC}"
    echo "   或"
    echo "   ${CYAN}./scripts/Linux系统一键启动.sh${NC}"
    echo ""
    
    print_header "📚 更多帮助"
    echo "查看详细配置说明：${CYAN}cat config/配置说明.txt${NC}"
    echo "查看快速指南：${CYAN}cat README_快速开始.txt${NC}"
    echo ""
    
else
    echo ""
    print_header "❌ 安装失败！"
    
    echo "可能的解决方案："
    echo ""
    echo "1️⃣  检查网络连接"
    echo "   ${CYAN}ping pypi.org${NC}"
    echo ""
    echo "2️⃣  使用国内镜像源（推荐中国用户）"
    echo "   ${CYAN}$PIP_CMD install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple${NC}"
    echo ""
    echo "3️⃣  使用sudo权限（如果提示权限错误）"
    echo "   ${CYAN}sudo $PIP_CMD install -r requirements.txt${NC}"
    echo ""
    echo "4️⃣  更新pip工具"
    echo "   ${CYAN}$PIP_CMD install --upgrade pip${NC}"
    echo ""
    
    exit 1
fi



