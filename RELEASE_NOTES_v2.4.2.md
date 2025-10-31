# Release Notes v2.4.2

**发布日期**: 2025-10-31  
**版本类型**: Bug修复版本

---

## 🐛 重要Bug修复

### 1. 配置文件路径问题（严重）
**问题描述**: 用户反馈在 `src/` 目录下直接运行 `python portfolio_manager.py` 时，提示"配置文件加载失败"

**影响范围**: 所有从 `src/` 目录运行程序的用户

**修复内容**:
- ✅ 自动检测运行目录，智能选择配置文件路径
- ✅ 支持从项目根目录运行：`python src/portfolio_manager.py`
- ✅ 支持从 `src/` 目录运行：`cd src && python portfolio_manager.py`

**技术细节**:
```python
# 修复前
market_scanner = MarketScanner(binance_client, 'config/coins_config.json')

# 修复后
config_path = 'config/coins_config.json' if os.path.exists('config/coins_config.json') else '../config/coins_config.json'
market_scanner = MarketScanner(binance_client, config_path)
```

---

### 2. 杠杆倍数配置被忽略（严重）
**问题描述**: 用户在 `config/coins_config.json` 中设置 `"leverage": 5`，但程序实际使用的是默认的 `3x` 杠杆

**影响范围**: 所有需要自定义杠杆倍数的用户

**修复内容**:
- ✅ 正确从配置文件读取 `portfolio_rules.leverage`
- ✅ 新增 `min_cash_reserve_percent` 配置支持（保留资金比例）
- ✅ 新增 `max_single_coin_percent` 配置支持（单币最大仓位）
- ✅ 启动时打印配置信息，方便用户确认

**配置示例**:
```json
{
  "coins": [...],
  "portfolio_rules": {
    "leverage": 5,                    // 杠杆倍数（1-10）
    "min_cash_reserve_percent": 10,   // 保留10%现金
    "max_single_coin_percent": 100    // 单币最大100%额度
  }
}
```

**启动输出**:
```
📋 配置加载成功 - 杠杆: 5x, 最低保留资金: 10%, 单币最大: 100%
```

---

## 💡 改进

1. **更智能的配置加载**
   - 支持从任意目录运行
   - 自动检测配置文件位置
   - 更好的错误处理和默认值回退

2. **更清晰的启动信息**
   - 显示加载的配置参数
   - 方便用户确认设置是否正确

---

## 📦 下载

### 一键开箱版（推荐新手）
```bash
# 下载压缩包
wget https://github.com/xuanoooooo/ai-trading-bot/releases/download/v2.4.2/ai-trading-bot-easy-setup-v2.4.2.tar.gz

# 解压
tar -xzf ai-trading-bot-easy-setup-v2.4.2.tar.gz
cd ai-trading-bot-easy-setup

# Windows用户
双击 start.bat 启动交易程序
双击 start_dashboard.bat 启动看板

# Linux/Mac用户
bash scripts/start_trading.sh
bash scripts/start_dashboard.sh
```

### 完整源码版（开发者）
```bash
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot
git checkout v2.4.2
```

---

## 🔄 升级指南

### 从 v2.4.1 升级

**方法1: 直接替换文件**
```bash
# 备份你的配置
cp config/coins_config.json config/coins_config.json.backup
cp .env .env.backup

# 下载新版本并替换 src/ 目录
# 恢复配置
cp config/coins_config.json.backup config/coins_config.json
cp .env.backup .env
```

**方法2: Git拉取**
```bash
git stash  # 暂存本地修改
git pull origin main
git checkout v2.4.2
git stash pop  # 恢复本地修改
```

---

## ✅ 验证修复

### 测试1: 从src目录运行
```bash
cd src
python portfolio_manager.py
```
✅ 应该正常启动，不报错

### 测试2: 杠杆配置生效
1. 编辑 `config/coins_config.json`，设置 `"leverage": 5`
2. 启动程序
3. 查看输出：应该显示 `📋 配置加载成功 - 杠杆: 5x, ...`
4. 查看日志：实际杠杆设置应该是 5x

---

## 🙏 致谢

感谢社区用户的Bug反馈！这些问题影响了很多用户的使用体验，现在已经彻底修复。

---

## 📝 完整更新日志

查看 [CHANGELOG.md](./CHANGELOG.md) 获取完整的版本历史。

---

## ⚠️ 重要提醒

- 本版本为Bug修复版本，强烈建议所有用户升级
- 升级前请备份你的 `.env` 和 `config/coins_config.json`
- 如遇到问题，请提交 [Issue](https://github.com/xuanoooooo/ai-trading-bot/issues)

---

## 📞 支持

- **GitHub Issues**: https://github.com/xuanoooooo/ai-trading-bot/issues
- **README**: [中文](./README.md) | [English](./README_EN.md)
- **钱包地址**: 0xYourWalletAddress（如果你觉得有帮助，欢迎打赏支持）

