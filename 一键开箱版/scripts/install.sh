#!/bin/bash

echo "🚀 AI多币种交易系统 - 快速安装"
echo "================================"
echo ""

# 检查Python版本
echo "📋 检查Python版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python版本: $PYTHON_VERSION"

# 安装依赖
echo ""
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 创建.env文件
if [ ! -f .env ]; then
    echo ""
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入你的API密钥"
fi

# 创建必要的目录
mkdir -p logs

echo ""
echo "✅ 安装完成！"
echo ""
echo "📖 下一步："
echo "1. 编辑 .env 文件，填入API密钥"
echo "2. 编辑 config/coins_config.json 配置交易币种"
echo "3. 运行: bash scripts/start_trading.sh"
echo ""
