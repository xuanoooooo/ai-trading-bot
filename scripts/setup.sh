#!/bin/bash
# 🚀 AI Trading Bot Installation Script
# 🚀 AI交易机器人安装脚本
# Automatically install dependencies, configure environment, verify settings
# 自动安装依赖、配置环境、验证设置

set -e  # Exit immediately on error / 遇到错误立即退出

# Color definitions / 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions / 打印函数
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

# 检查系统要求
check_system_requirements() {
    print_info "检查系统要求..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 1 ]]; then
            print_success "Python版本: $PYTHON_VERSION ✓"
        else
            print_error "Python版本过低: $PYTHON_VERSION，需要3.11+"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.11+"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        print_success "pip已安装 ✓"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    # 检查git
    if command -v git &> /dev/null; then
        print_success "git已安装 ✓"
    else
        print_warning "未找到git，建议安装git"
    fi
}

# 安装系统依赖
install_system_dependencies() {
    print_info "安装系统依赖..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux系统
        if command -v apt &> /dev/null; then
            # Ubuntu/Debian
            print_info "检测到Ubuntu/Debian系统"
            sudo apt update
            sudo apt install -y python3.11-venv python3-pip curl wget
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            print_info "检测到CentOS/RHEL系统"
            sudo yum install -y python3.11-venv python3-pip curl wget
        elif command -v dnf &> /dev/null; then
            # Fedora
            print_info "检测到Fedora系统"
            sudo dnf install -y python3.11-venv python3-pip curl wget
        else
            print_warning "未识别的Linux发行版，请手动安装依赖"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS系统
        print_info "检测到macOS系统"
        if command -v brew &> /dev/null; then
            brew install python@3.11
        else
            print_warning "建议安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    else
        print_warning "未识别的操作系统: $OSTYPE"
    fi
}

# 创建虚拟环境
create_virtual_environment() {
    print_info "创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        print_warning "虚拟环境已存在，是否重新创建？(y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf venv
            print_info "删除旧虚拟环境"
        else
            print_info "使用现有虚拟环境"
            return
        fi
    fi
    
    python3 -m venv venv
    print_success "虚拟环境创建成功"
}

# 激活虚拟环境
activate_virtual_environment() {
    print_info "激活虚拟环境..."
    source venv/bin/activate
    print_success "虚拟环境已激活"
}

# 安装Python依赖
install_python_dependencies() {
    print_info "安装Python依赖包..."
    
    # 升级pip
    pip install --upgrade pip setuptools wheel
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    # 检查关键模块
    python3 -c "
import sys
print(f'Python版本: {sys.version}')

try:
    import binance
    print('✅ python-binance模块导入成功')
except ImportError as e:
    print(f'❌ python-binance模块导入失败: {e}')
    sys.exit(1)

try:
    import openai
    print('✅ openai模块导入成功')
except ImportError as e:
    print(f'❌ openai模块导入失败: {e}')
    sys.exit(1)

try:
    import pandas
    print('✅ pandas模块导入成功')
except ImportError as e:
    print(f'❌ pandas模块导入失败: {e}')
    sys.exit(1)

try:
    import schedule
    print('✅ schedule模块导入成功')
except ImportError as e:
    print(f'❌ schedule模块导入失败: {e}')
    sys.exit(1)

print('✅ 所有依赖模块验证通过')
"
    
    if [ $? -eq 0 ]; then
        print_success "安装验证通过"
    else
        print_error "安装验证失败"
        exit 1
    fi
}

# 配置环境变量
setup_environment() {
    print_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f "config/env.example" ]; then
            cp config/env.example .env
            print_success "已创建.env文件，请编辑并填入您的API密钥"
        else
            print_warning "未找到环境变量模板文件"
        fi
    else
        print_info ".env文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p backup
    mkdir -p data
    
    print_success "目录创建完成"
}

# 设置权限
set_permissions() {
    print_info "设置文件权限..."
    
    # 设置脚本执行权限
    chmod +x scripts/*.sh 2>/dev/null || true
    
    # 设置.env文件权限
    if [ -f ".env" ]; then
        chmod 600 .env
        print_success "已设置.env文件权限"
    fi
    
    print_success "权限设置完成"
}

# 显示安装总结
show_summary() {
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "📋 下一步操作："
    echo "1. 编辑 .env 文件，填入您的API密钥："
    echo "   nano .env"
    echo ""
    echo "2. 启动交易机器人："
    echo "   source venv/bin/activate"
    echo "   python src/deepseekBNB.py"
    echo ""
    echo "3. 或使用启动脚本："
    echo "   ./scripts/start_trading.sh"
    echo ""
    echo "📚 更多信息请查看："
    echo "- 安装指南: docs/installation.md"
    echo "- 配置指南: docs/configuration.md"
    echo "- 交易指南: docs/trading_guide.md"
    echo ""
    echo "⚠️  重要提醒："
    echo "- 请先在测试模式下运行"
    echo "- 建议使用子账户进行交易"
    echo "- 定期监控机器人运行状态"
    echo ""
}

# 主函数
main() {
    echo "🚀 AI交易机器人安装脚本"
    echo "================================"
    
    # 检查是否在项目根目录
    if [ ! -f "requirements.txt" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    check_system_requirements
    install_system_dependencies
    create_virtual_environment
    activate_virtual_environment
    install_python_dependencies
    verify_installation
    setup_environment
    create_directories
    set_permissions
    show_summary
}

# 运行主函数
main "$@"
