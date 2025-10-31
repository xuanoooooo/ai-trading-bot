# Release Notes v2.4.3

**发布日期**: 2025-10-31  
**版本类型**: Bug修复版本（看板程序）

---

## 🐛 修复的问题

### 看板程序三大Bug修复

#### 1. 模块导入错误
**问题描述**: 启动看板时报错 `ModuleNotFoundError: No module named 'market_scanner'`

**原因**: 
```python
# 错误的导入
from market_scanner import MarketScanner
```
`market_scanner.py` 在 `src/` 目录下，应该使用 `src.market_scanner`

**修复**:
```python
# 正确的导入
from src.market_scanner import MarketScanner
```

---

#### 2. 环境变量加载错误
**问题描述**: 看板无法读取 Binance API 配置

**原因**:
```python
# 硬编码的路径
load_dotenv('/root/DS/duobizhong/.env')
```
这个路径只在特定环境有效，其他用户无法使用

**修复**:
```python
# 自动查找 .env 文件
load_dotenv()

# 如果找不到，尝试从项目根目录加载
if not os.getenv('BINANCE_API_KEY'):
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)
```

---

#### 3. 数据文件路径错误（最严重）
**问题描述**: 
- 显示"未运行"
- AI交易决策为空
- 持仓数据的开仓时间为空

**原因**:
```python
# 错误的相对路径
STATS_FILE = '../portfolio_stats.json'
AI_DECISIONS_FILE = '../ai_decisions.json'
RUNTIME_FILE = '../current_runtime.json'

def load_json_file(filepath):
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    # 这会查找 dashboard/../portfolio_stats.json
    # 但实际文件在项目根目录
```

**修复**:
```python
# 使用绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(PROJECT_ROOT, 'portfolio_stats.json')
AI_DECISIONS_FILE = os.path.join(PROJECT_ROOT, 'ai_decisions.json')
RUNTIME_FILE = os.path.join(PROJECT_ROOT, 'current_runtime.json')

def load_json_file(filepath):
    if os.path.isabs(filepath):
        full_path = filepath
    else:
        full_path = os.path.join(PROJECT_ROOT, filepath)
    
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"⚠️ 文件不存在: {full_path}")
    return None
```

---

## 💡 改进

1. **更智能的路径处理**
   - 使用 `os.path.join` 确保跨平台兼容
   - 自动检测项目根目录
   - 支持从任意目录启动看板

2. **更好的错误提示**
   - 文件不存在时显示完整路径
   - 模块导入失败时显示详细错误

3. **配置文件路径优化**
   - `config/coins_config.json` 使用绝对路径
   - 避免相对路径导致的各种问题

---

## 📦 下载

### 一键开箱版（推荐新手）
```bash
# 下载压缩包
wget https://github.com/xuanoooooo/ai-trading-bot/releases/download/v2.4.3/ai-trading-bot-easy-setup-v2.4.3.tar.gz

# 解压
tar -xzf ai-trading-bot-easy-setup-v2.4.3.tar.gz
cd ai-trading-bot-easy-setup

# 启动看板
bash scripts/start_dashboard.sh
# 或 Windows:
双击 start_dashboard.bat
```

---

## 🔄 升级指南

### 从 v2.4.2 升级

只需替换 `dashboard/web_app.py` 文件：

```bash
# 备份
cp dashboard/web_app.py dashboard/web_app.py.backup

# 下载新版本并替换
# 或直接下载 v2.4.3 完整包
```

---

## ✅ 验证修复

### 测试1: 启动看板
```bash
cd dashboard
python web_app.py
```
✅ 应该正常启动，不报导入错误

### 测试2: 查看数据
1. 打开浏览器访问 `http://localhost:5000`
2. 查看"运行状态"区域
   - ✅ 应该显示运行时长（而不是"未运行"）
3. 查看"AI交易决策"区域
   - ✅ 应该显示最近的交易决策（如果有）
4. 查看"持仓数据"
   - ✅ 开仓时间应该正常显示

---

## 📝 影响范围

### 受影响的文件
- ✅ `dashboard/web_app.py` - 主修复文件
- ✅ `一键开箱版/dashboard/web_app.py` - 同步修复

### 不受影响的文件
- ✅ `src/portfolio_manager.py` - 无变化
- ✅ `src/market_scanner.py` - 无变化
- ✅ 其他核心交易逻辑 - 无变化

**这是一个纯看板程序的Bug修复，不影响交易逻辑！**

---

## 🙏 致谢

感谢用户反馈看板程序的详细Bug报告！
- ✅ 模块导入错误
- ✅ env文件路径问题
- ✅ 数据显示问题

这3个问题现已全部修复！

---

## 📞 支持

- **GitHub Issues**: https://github.com/xuanoooooo/ai-trading-bot/issues
- **README**: [中文](./README.md) | [English](./README_EN.md)
- **完整更新日志**: [CHANGELOG.md](./CHANGELOG.md)

