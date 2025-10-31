# 更新日志 | Changelog

## v2.4.4 - 2025-11-01 🔥 重要安全更新

### 🛡️ 孤儿订单清理机制（防止反向开仓）

**问题描述**：
- 止损/止盈订单是独立的条件单
- 如果止损单触发平仓，止盈单会成为"孤儿订单"
- 后续价格波动可能误触发孤儿止盈单，导致**反向开仓**
- 这是一个严重的风险控制漏洞！

**修复内容**：
- ✅ **周期第一步清理**: 每个交易周期开始时清理所有孤儿订单
- ✅ **平仓后清理**: AI主动平仓后立即清理该币种所有挂单
- ✅ **单向持仓优化**: 针对Binance单向持仓模式进行优化

**修改文件**：
- `src/portfolio_manager.py`:
  - 新增 `clean_orphan_orders()` 函数（第1146-1197行）
  - 在 `portfolio_bot()` 第一步调用清理（第1206-1208行）
  - 平仓后添加 `futures_cancel_all_open_orders()` 调用（第898-902行）

**示例场景（修复前）**：
```
00:00 开多 BTC @ 95000，设置止损93000、止盈97000
00:02 价格跌破93000 → 止损触发，仓位清空
      止盈单97000还在（孤儿订单）⚠️
00:04 价格反弹到97000 → 误触发止盈单
      结果：反向开空仓！❌ 严重错误
```

**修复后效果**：
```
00:00 开多 BTC @ 95000，设置止损93000、止盈97000
00:02 价格跌破93000 → 止损触发，仓位清空
      ✅ 立即清理所有挂单（包括止盈单）
00:04 价格反弹到97000 → 无订单触发 ✅ 安全
```

**影响评估**：
- 🔴 **严重性**: 高（误开仓可能导致重大亏损）
- ✅ **已修复**: 孤儿订单清理机制已完全实现
- ✅ **测试通过**: 单向持仓模式下正常工作

⚠️ **强烈建议所有用户更新到 v2.4.4！**

---

## v2.4.3 - 2025-10-31

### 🐛 Bug修复 - 看板程序
- **模块导入错误**: 修复 `market_scanner` 导入失败，正确使用 `src.market_scanner`
- **环境变量加载**: 修复硬编码路径，改用 `load_dotenv()` 自动查找 `.env`
- **数据文件路径**: 修复相对路径导致无法加载数据文件的问题
  - 使用绝对路径定位 `portfolio_stats.json`、`ai_decisions.json`、`current_runtime.json`
  - 修复"显示未运行"和"AI交易决策空白"问题
  - 修复持仓数据"开仓时间空白"问题

### 💡 改进
- 看板程序现在可以从任意目录启动
- 更好的错误提示和文件路径调试信息
- 配置文件路径使用 `os.path.join` 确保跨平台兼容

---

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
