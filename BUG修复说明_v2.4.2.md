# BUG修复说明 v2.4.2

**修复日期**: 2025-10-31  
**修复版本**: v2.4.2

---

## 🐛 修复的问题

### 问题1: 配置文件路径错误
**症状**: 用户在 `src/` 目录下直接运行 `python portfolio_manager.py` 时，提示配置文件加载失败

**原因**: 
```python
# 原代码（第98行）
market_scanner = MarketScanner(binance_client, 'config/coins_config.json')
```
- 这个路径是相对路径
- 从项目根目录运行时正确：`./config/coins_config.json`
- 从 `src/` 目录运行时错误：`./src/config/coins_config.json` （不存在）

**修复**:
```python
# 新代码（第99-101行）
# 配置文件路径（兼容从项目根目录或src目录运行）
config_path = 'config/coins_config.json' if os.path.exists('config/coins_config.json') else '../config/coins_config.json'
market_scanner = MarketScanner(binance_client, config_path)
```
- 自动检测并使用正确的路径
- 从项目根目录运行：使用 `config/coins_config.json`
- 从 `src/` 目录运行：使用 `../config/coins_config.json`

---

### 问题2: 杠杆倍数配置被忽略
**症状**: 用户在 `config/coins_config.json` 中设置 `leverage: 5`，但程序仍然使用 `3x` 杠杆

**原因**:
```python
# 原代码（第156-160行）- 硬编码配置
PORTFOLIO_CONFIG = {
    'leverage': 3,  # ❌ 硬编码！配置文件的值被忽略
    'check_interval_minutes': 5,
    'test_mode': False
}
```

虽然 `config/coins_config.json` 中有配置：
```json
"portfolio_rules": {
    "leverage": 3,
    "min_cash_reserve_percent": 10,
    "max_single_coin_percent": 100
}
```
但这些配置**从未被读取**！

**修复**:
```python
# 新代码（第159-181行）
def load_portfolio_config():
    """从coins_config.json加载投资组合配置"""
    try:
        portfolio_rules = market_scanner.coins_config.get('portfolio_rules', {})
        return {
            'leverage': portfolio_rules.get('leverage', 3),
            'min_cash_reserve_percent': portfolio_rules.get('min_cash_reserve_percent', 10),
            'max_single_coin_percent': portfolio_rules.get('max_single_coin_percent', 100),
            'check_interval_minutes': 5,
            'test_mode': False
        }
    except Exception as e:
        print(f"⚠️ 加载配置失败，使用默认值: {e}")
        return {
            'leverage': 3,
            'min_cash_reserve_percent': 10,
            'max_single_coin_percent': 100,
            'check_interval_minutes': 5,
            'test_mode': False
        }

PORTFOLIO_CONFIG = load_portfolio_config()
print(f"📋 配置加载成功 - 杠杆: {PORTFOLIO_CONFIG['leverage']}x, 最低保留资金: {PORTFOLIO_CONFIG['min_cash_reserve_percent']}%, 单币最大: {PORTFOLIO_CONFIG['max_single_coin_percent']}%")
```

**新增功能**:
- ✅ 自动从 `config/coins_config.json` 读取 `portfolio_rules`
- ✅ 读取 `leverage`（杠杆倍数）
- ✅ 读取 `min_cash_reserve_percent`（最低保留资金百分比）
- ✅ 读取 `max_single_coin_percent`（单币最大仓位百分比）
- ✅ 如果配置文件缺失或读取失败，使用默认值
- ✅ 启动时打印配置信息，方便用户确认

---

## 📋 修改的文件

1. ✅ `/src/portfolio_manager.py` - 主程序
2. ✅ `/一键开箱版/src/portfolio_manager.py` - 开箱版主程序

---

## 🎯 用户如何使用

### 修改杠杆倍数
编辑 `config/coins_config.json`:
```json
{
  "coins": [...],
  "portfolio_rules": {
    "leverage": 5,  // 修改为你想要的杠杆倍数（1-10）
    "min_cash_reserve_percent": 10,  // 最低保留10%现金
    "max_single_coin_percent": 100   // 单币最大使用100%可用额度
  }
}
```

### 从src目录运行
现在可以直接在 `src/` 目录下运行：
```bash
cd src
python portfolio_manager.py
```
程序会自动找到 `../config/coins_config.json`

---

## ✅ 测试验证

### 测试1: 从项目根目录运行
```bash
cd /root/DS/Github发布版
python src/portfolio_manager.py
```
**预期结果**: 
- ✅ 正常加载配置文件
- ✅ 打印 `📋 配置加载成功 - 杠杆: Xx, ...`

### 测试2: 从src目录运行
```bash
cd /root/DS/Github发布版/src
python portfolio_manager.py
```
**预期结果**:
- ✅ 正常加载配置文件（使用 `../config/coins_config.json`）
- ✅ 打印配置信息

### 测试3: 修改杠杆倍数
1. 编辑 `config/coins_config.json`，设置 `"leverage": 5`
2. 运行程序
3. 查看输出：`📋 配置加载成功 - 杠杆: 5x, ...`
4. 查看日志中的实际杠杆设置

---

## 🔄 后续步骤

1. ✅ 已修复主版本 (`/src/`)
2. ✅ 已同步到一键开箱版 (`/一键开箱版/src/`)
3. ⏳ 需要重新打包 `ai-trading-bot-easy-setup-v2.4.2.tar.gz`
4. ⏳ 需要推送到GitHub
5. ⏳ 需要创建 Release v2.4.2

---

## 📝 CHANGELOG条目

```markdown
### v2.4.2 - 2025-10-31

#### 🐛 Bug修复
- **配置文件路径**: 修复从 `src/` 目录运行时无法加载配置文件的问题
  - 现在支持从项目根目录或 `src/` 目录运行
  - 自动检测并使用正确的配置文件路径
  
- **杠杆倍数配置**: 修复杠杆倍数硬编码问题
  - 现在正确从 `config/coins_config.json` 的 `portfolio_rules.leverage` 读取
  - 新增 `min_cash_reserve_percent` 配置支持
  - 新增 `max_single_coin_percent` 配置支持
  - 启动时显示配置信息，方便确认

#### 💡 改进
- 配置加载更加智能，支持从不同目录运行
- 更好的错误处理和默认值回退机制
```

---

## 🙏 感谢

感谢用户反馈这两个重要的BUG！

