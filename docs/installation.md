# 📦 安装指南

## 🖥️ 系统要求

### 最低要求
- **操作系统**: Linux/macOS/Windows
- **Python版本**: 3.11 或更高版本
- **内存**: 至少 2GB RAM
- **存储空间**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **Python版本**: 3.11+
- **内存**: 4GB+ RAM
- **存储空间**: 5GB+ 可用空间
- **网络**: 高速稳定的互联网连接

## 🚀 快速安装

### 方法1: 使用安装脚本（推荐）
```bash
# 克隆项目
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot

# 运行安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 方法2: 手动安装
```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp config/env.example .env
# 编辑 .env 文件，填入您的API密钥
```

## 🔧 详细安装步骤

### 1. 环境准备

#### Ubuntu/Debian
```bash
# 更新包管理器
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装系统依赖
sudo apt install git curl wget -y
```

#### CentOS/RHEL
```bash
# 安装Python 3.11
sudo dnf install python3.11 python3.11-pip python3.11-venv -y

# 安装系统依赖
sudo dnf install git curl wget -y
```

#### macOS
```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python@3.11

# 安装系统依赖
brew install git curl wget
```

#### Windows
```powershell
# 使用Chocolatey安装Python
choco install python311

# 或下载Python安装包
# https://www.python.org/downloads/
```

### 2. 项目设置

```bash
# 克隆项目
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 依赖安装

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import binance, openai, pandas; print('✅ 所有依赖安装成功')"
```

### 4. 配置文件设置

```bash
# 复制环境变量模板
cp config/env.example .env

# 编辑配置文件
nano .env  # 或使用您喜欢的编辑器
```

在 `.env` 文件中填入您的API密钥：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
```

### 5. 验证安装

```bash
# 运行测试脚本
python -c "
import sys
print(f'Python版本: {sys.version}')
print('✅ 环境检查通过')
"

# 测试API连接
python -c "
from src.utils import load_env_vars, validate_api_keys
env_vars = load_env_vars()
if validate_api_keys(env_vars):
    print('✅ API密钥配置正确')
else:
    print('❌ API密钥配置有误')
"
```

## 🐳 Docker安装（可选）

### 使用Docker Compose
```bash
# 创建docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  trading-bot:
    build: .
    container_name: ai-trading-bot
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
EOF

# 构建并启动
docker-compose up -d
```

### 使用Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/deepseekBNB.py"]
```

## 🔍 故障排除

### 常见问题

#### 1. Python版本问题
```bash
# 检查Python版本
python3 --version

# 如果版本过低，安装Python 3.11
# Ubuntu:
sudo apt install python3.11 -y
# macOS:
brew install python@3.11
```

#### 2. 虚拟环境问题
```bash
# 删除旧虚拟环境
rm -rf venv

# 重新创建
python3.11 -m venv venv
source venv/bin/activate
```

#### 3. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip setuptools wheel

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt --no-cache-dir
```

#### 4. 权限问题
```bash
# 给脚本执行权限
chmod +x scripts/*.sh

# 检查文件权限
ls -la scripts/
```

#### 5. 网络连接问题
```bash
# 测试网络连接
ping api.binance.com
ping api.deepseek.com

# 检查防火墙设置
sudo ufw status
```

### 日志文件位置
- **主日志**: `trading_bot.log`
- **备份日志**: `trading_bot.log.1`, `trading_bot.log.2`
- **错误日志**: 检查控制台输出

### 获取帮助
如果遇到问题，请：
1. 检查日志文件
2. 查看GitHub Issues
3. 提交新的Issue
4. 联系技术支持

## ✅ 安装验证清单

- [ ] Python 3.11+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] API密钥已配置
- [ ] 配置文件已设置
- [ ] 网络连接正常
- [ ] 权限设置正确
- [ ] 测试运行成功

安装完成后，请参考 [配置指南](configuration.md) 进行下一步设置。
