# 更新日志 | Changelog

## v2.4.2 - 2025-10-31

### 🐛 Bug修复
- **配置文件路径**: 修复从 `src/` 目录运行时无法加载配置文件的问题
  - 现在支持从项目根目录或 `src/` 目录运行
  - 自动检测并使用正确的配置文件路径
  
- **杠杆倍数配置**: 修复杠杆倍数硬编码问题
  - 现在正确从 `config/coins_config.json` 的 `portfolio_rules.leverage` 读取
  - 新增 `min_cash_reserve_percent` 配置支持
  - 新增 `max_single_coin_percent` 配置支持
  - 启动时显示配置信息，方便确认

### 💡 改进
- 配置加载更加智能，支持从不同目录运行
- 更好的错误处理和默认值回退机制

---

## v2.4.1 - 2025-10-30

### ✨ 新特性
- **一键开箱版自动安装依赖**: 首次运行时自动执行 `pip install -r requirements.txt`
- 简化零基础用户的安装流程

### 📝 文档更新
- 完善快速上手指南
- 更新下载链接

---

## v2.0.0 - Multi-Coin Version | 多币种版本 (2025-10-31)

### 🎉 重大更新 | Major Update

这是一个**完全重构**的版本，从单币种交易升级到多币种投资组合管理系统。

This is a **complete rewrite**, upgrading from single-coin trading to multi-coin portfolio management.

### ✨ 新特性 | New Features

#### 多币种管理 | Multi-Coin Management
- ✅ 同时管理多个币种（BTC、ETH、SOL等）
- ✅ Manage multiple coins simultaneously (BTC, ETH, SOL, etc.)
- ✅ 智能资金分配，自动平衡投资组合
- ✅ Smart fund allocation, automatic portfolio balancing

#### 实时可视化看板 | Real-Time Dashboard
- ✅ Flask驱动的Web界面
- ✅ Flask-powered web interface
- ✅ 实时查看所有持仓和收益
- ✅ Real-time view of positions and profits
- ✅ AI决策记录可视化
- ✅ AI decision history visualization

#### 增强的AI决策引擎 | Enhanced AI Decision Engine
- ✅ 投资组合级别的决策分析
- ✅ Portfolio-level decision analysis
- ✅ 多币种市场扫描
- ✅ Multi-coin market scanning
- ✅ 风险分散策略
- ✅ Risk diversification strategy

#### 完善的风险控制 | Improved Risk Control
- ✅ 单币种仓位限制（20%）
- ✅ Per-coin position limit (20%)
- ✅ 最大持仓数量控制（5个）
- ✅ Maximum position count control (5)
- ✅ 自动止损止盈
- ✅ Automatic stop-loss/take-profit

### 📝 文档 | Documentation
- ✅ 中英文双语README
- ✅ Bilingual README (CN/EN)
- ✅ 详细的安装和使用指南
- ✅ Detailed installation and usage guide
- ✅ 完整的代码注释
- ✅ Complete code comments

### 🔄 迁移说明 | Migration Guide

**从单币种版本升级？| Upgrading from single-coin version?**

旧的单币种版本已备份到 `single-coin-version` 分支。
The old single-coin version is backed up in the `single-coin-version` branch.

如果你想继续使用单币种版本：
If you want to continue using the single-coin version:

```bash
git checkout single-coin-version
```

### 🔧 技术栈 | Tech Stack

**后端 | Backend:**
- Python 3.11+
- python-binance (Binance API)
- OpenAI (DeepSeek API)
- python-dotenv

**前端看板 | Frontend Dashboard:**
- Flask
- HTML/CSS/JavaScript
- Chart.js

### 📦 安装 | Installation

```bash
# 克隆项目 | Clone repository
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot

# 安装依赖 | Install dependencies
bash scripts/install.sh

# 配置API密钥 | Configure API keys
cp .env.example .env
nano .env

# 启动交易 | Start trading
bash scripts/start_trading.sh

# 启动看板 | Start dashboard (optional)
bash scripts/start_dashboard.sh
```

### ⚠️ 重要变化 | Breaking Changes

1. **项目结构完全重构** | Complete project structure rewrite
2. **配置文件格式变更** | Configuration file format changed
3. **不再向后兼容单币种版本** | Not backward compatible with single-coin version

### 🐛 已知问题 | Known Issues

暂无 | None

### 📅 下一步计划 | Roadmap

- [ ] 支持更多交易所（OKX、Bybit）
- [ ] Support more exchanges (OKX, Bybit)
- [ ] 添加Telegram通知
- [ ] Add Telegram notifications
- [ ] 回测功能
- [ ] Backtesting feature
- [ ] 移动端看板
- [ ] Mobile dashboard

---

## v1.x - Single Coin Version | 单币种版本

**注意：单币种版本已迁移到 `single-coin-version` 分支**  
**Note: Single-coin version moved to `single-coin-version` branch**

查看历史版本 | View history:
```bash
git checkout single-coin-version
git log
```
