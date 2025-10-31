# 🤖 AI Multi-Coin Automated Trading System | AI多币种自动交易系统

<div align="center">

**Let AI Monitor Markets for You | 让AI替你盯盘交易**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-purple.svg)](https://www.deepseek.com/)

### 📖 Choose Your Language | 选择语言

<table>
<tr>
<td width="50%" align="center">

### 🇨🇳 简体中文

[👉 查看中文完整文档](README_CN.md)

**多币种投资组合管理**  
**24/7全自动运行**  
**实时可视化看板**

</td>
<td width="50%" align="center">

### 🇺🇸 English

[👉 View Full English Docs](README_EN.md)

**Multi-Coin Portfolio Management**  
**24/7 Automated Trading**  
**Real-Time Dashboard**

</td>
</tr>
</table>

</div>

---

## 💭 Author's Note | 作者的话

> 🇨🇳 *"经历了生活的大亏损、在币圈也没获得什么结果，我对自己的水平彻底失望。*  
> *与其每天假装看盘实则在赌，不如把决策交给AI——至少它不会因为行情波动而梭哈。*  
> *这个项目源于一个简单的期望：AI再不完美也比我强。"*

> 🇺🇸 *"After experiencing significant life losses and achieving little in crypto trading, I've completely lost confidence in my own abilities.*  
> *Rather than pretending to analyze charts while essentially gambling, it's better to let AI make the decisions—at least it won't panic-sell during market swings.*  
> *This project stems from a simple expectation: Even an imperfect AI is better than me."*

---

## ⚠️ Important | 重要提醒

<table>
<tr>
<td width="50%">

### 🇨🇳 中文

**市场有风险，投资需谨慎。**

本项目仅供学习交流使用。

**没有收费也没有挂邀请码，只求各位给星星** ⭐

</td>
<td width="50%">

### 🇺🇸 English

**Markets are risky, invest cautiously.**

This project is for educational purposes only.

**No fees, no referral codes, just asking for stars** ⭐

</td>
</tr>
</table>

---

## 🎯 What Makes This Special | 项目亮点

### 🆚 Single Coin vs Multi-Coin | 单币种 VS 多币种

<table>
<tr>
<th width="33%">Feature | 特性</th>
<th width="33%">Single Coin | 单币种</th>
<th width="33%">Multi-Coin (This) | 多币种（本项目）</th>
</tr>
<tr>
<td><b>Management | 管理方式</b></td>
<td>Only 1 coin | 只交易1个币</td>
<td><b>5-8 coins simultaneously | 同时管理5-8个币种</b> ✨</td>
</tr>
<tr>
<td><b>Risk | 风险</b></td>
<td>Concentrated | 集中风险</td>
<td><b>Diversified | 分散风险</b> 🛡️</td>
</tr>
<tr>
<td><b>Opportunity | 机会</b></td>
<td>Limited | 单一机会</td>
<td><b>Multiple markets | 多市场捕捉</b> 📈</td>
</tr>
<tr>
<td><b>Returns | 收益</b></td>
<td>Depends on 1 coin | 依赖单币</td>
<td><b>More stable | 更稳定</b> 💪</td>
</tr>
</table>

---

## ✨ Key Features | 核心功能

<table>
<tr>
<td width="50%">

### 🇨🇳 中文版

#### 🧠 AI全自动决策
- DeepSeek AI智能分析
- 完全解放双手，24/7运行
- 自动开仓、平仓、止损止盈

#### 📊 多币种管理
- 同时管理BTC、ETH、SOL等
- 智能资金分配
- 风险分散，不怕单币暴跌

#### 🎨 实时看板
- Web界面直观展示
- 持仓、盈亏一目了然
- AI决策记录可查询

#### 🛡️ 风险控制
- 单币种不超过20%
- 自动止损3%、止盈8%
- 最多持有5个币种

#### 📈 技术分析
- RSI、MACD、EMA、布林带
- 1小时+4小时双周期验证
- AI有理有据做决策

</td>
<td width="50%">

### 🇺🇸 English

#### 🧠 AI Auto-Decision
- DeepSeek AI analysis
- Fully automated, 24/7 operation
- Auto open/close positions & stop-loss

#### 📊 Multi-Coin Management
- Manage BTC, ETH, SOL simultaneously
- Smart fund allocation
- Risk diversification

#### 🎨 Real-Time Dashboard
- Web interface visualization
- Clear position & P&L display
- AI decision history

#### 🛡️ Risk Control
- Max 20% per coin
- Auto stop-loss 3%, take-profit 8%
- Max 5 positions

#### 📈 Technical Analysis
- RSI, MACD, EMA, Bollinger Bands
- 1h + 4h dual timeframe validation
- Data-driven AI decisions

</td>
</tr>
</table>

---

## 🚀 Quick Start | 快速开始

### Step 1 | 步骤1: Clone | 克隆

```bash
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot
```

### Step 2 | 步骤2: Install | 安装

```bash
bash scripts/install.sh
# or | 或者
pip install -r requirements.txt
```

### Step 3 | 步骤3: Configure | 配置

```bash
cp .env.example .env
nano .env  # Fill in your API keys | 填入API密钥
```

**Get API Keys | 获取密钥:**
- DeepSeek: https://platform.deepseek.com/
- Binance: https://www.binance.com/ (需要开通合约交易)

**⚠️ Important | 重要提示:**
- ✅ Default uses `deepseek-chat` (Fast & Cheap) | 默认使用 `deepseek-chat`（快速且便宜）
- ✅ Default coins: BTC, ETH, SOL, BNB, XRP, ADA, DOGE (USDT pairs) | 默认币种（USDT交易对）
- ✅ Recommend using default config | 建议使用默认配置
- ❌ Don't use coins < $1 (e.g., SHIB) | 不要使用单价低于$1的币种

📖 **Detailed config guide** | 详细配置指南:
- [🇨🇳 中文完整说明](README_CN.md#步骤4配置交易币种和ai模型)
- [🇺🇸 English Guide](README_EN.md#4-configure-ai-model--trading-coins)

### Step 4 | 步骤4: Start Trading | 启动交易

```bash
bash scripts/start_trading.sh
# or | 或者
cd src && python portfolio_manager.py
```

### Step 5 | 步骤5: Start Dashboard (Optional) | 启动看板（可选）

```bash
bash scripts/start_dashboard.sh
# Visit | 访问: http://localhost:5000
```

---

## 📸 System Interface Preview | 系统界面预览

### 🎨 Web Dashboard | Web可视化看板

**Real-time monitoring of positions and AI decisions | 实时监控持仓和AI决策**

![Web Dashboard](docs/images/看板截图.png)

**Features | 看板功能:**
- 💰 **Left Panel | 左侧**: Current positions with real-time P&L | 当前持仓，实时盈亏
- 🤖 **Right Panel | 右侧**: AI decision log with reasoning | AI决策日志，分析理由
- 🎨 **Dark Theme | 深色主题**: Easy on the eyes | 护眼舒适
- 🔄 **Auto Refresh | 自动刷新**: Updates every 30 seconds | 每30秒更新
- 💚💔 **Color Coded | 颜色标识**: Green for profit, red for loss | 绿色盈利，红色亏损

---

### 💻 Terminal Mode | 终端日志模式

**Detailed execution logs for server monitoring | 详细执行日志，适合服务器监控**

![Terminal Logs](docs/images/日志截图.png)

**Features | 日志功能:**
- 📝 **Detailed Logs | 详细日志**: Every AI analysis and trade execution | 每次AI分析和交易执行
- 🔍 **Real-time Display | 实时显示**: Live monitoring via SSH | SSH远程实时监控
- 💡 **Lightweight | 轻量级**: Minimal resource usage | 资源占用极低
- 📊 **Complete Info | 完整信息**: Market data, decisions, and results | 市场数据、决策、结果

---

## 📊 How It Works | 工作原理

<table>
<tr>
<td width="50%">

### 🇨🇳 工作流程

```
1️⃣ 市场扫描（每5分钟）
   ↓ 获取K线和技术指标
   
2️⃣ AI分析
   ↓ DeepSeek分析市场数据
   
3️⃣ 决策生成
   ↓ 开多/开空/平仓/持有
   
4️⃣ 风险检查
   ↓ 验证是否符合规则
   
5️⃣ 执行交易
   ↓ 通过币安API执行
   
6️⃣ 记录保存
   ↓ 保存决策和交易记录
```

</td>
<td width="50%">

### 🇺🇸 Workflow

```
1️⃣ Market Scan (Every 5 min)
   ↓ Fetch K-lines & indicators
   
2️⃣ AI Analysis
   ↓ DeepSeek analyzes data
   
3️⃣ Decision Making
   ↓ Long/Short/Close/Hold
   
4️⃣ Risk Check
   ↓ Validate compliance
   
5️⃣ Execute Trade
   ↓ Via Binance API
   
6️⃣ Record Keeping
   ↓ Save decisions & trades
```

</td>
</tr>
</table>

---

## 🗂️ Project Structure | 项目结构

```
ai-trading-bot/
├── src/                    # Core code | 核心代码
│   ├── portfolio_manager.py      # Main program | 主程序
│   ├── market_scanner.py         # Market scanner | 市场扫描
│   └── portfolio_statistics.py   # Statistics | 统计
├── dashboard/              # Web dashboard | Web看板
│   ├── web_app.py         # Flask app | Flask应用
│   ├── static/            # CSS/JS | 静态文件
│   └── templates/         # HTML | 模板
├── config/                 # Configuration | 配置
│   └── coins_config.json  # Coin settings | 币种配置
├── scripts/                # Scripts | 脚本
│   ├── install.sh         # Installation | 安装
│   ├── start_trading.sh   # Start trading | 启动交易
│   └── start_dashboard.sh # Start dashboard | 启动看板
├── .env.example            # Environment template | 环境模板
└── requirements.txt        # Dependencies | 依赖
```

---

## 📚 Documentation | 完整文档

<table>
<tr>
<td width="50%" align="center">

### 🇨🇳 中文文档

**[📖 查看完整中文文档](README_CN.md)**

包含：
- 详细安装步骤
- 配置说明
- AI决策逻辑详解
- 监控命令大全
- 常见问题Q&A

</td>
<td width="50%" align="center">

### 🇺🇸 English Docs

**[📖 View Full English Docs](README_EN.md)**

Including:
- Detailed installation
- Configuration guide
- AI decision logic
- Monitoring commands
- FAQ

</td>
</tr>
</table>

---

## 🤝 Contributing | 贡献

Contributions welcome! | 欢迎贡献！

**Roadmap | 开发计划:**
- [ ] Support more exchanges (OKX, Bybit) | 支持更多交易所
- [ ] Telegram notifications | Telegram通知
- [ ] Backtesting feature | 回测功能
- [ ] Mobile dashboard | 移动端看板

---

## 💰 Support | 支持

<div align="center">

**If this helps you, consider supporting | 如果有帮助，欢迎支持**

**Wallet (BEP20/BSC) | 钱包地址**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

Your support motivates updates ❤️  
您的支持是持续更新的动力 ❤️

</div>

---

## 📄 License | 许可

Apache 2.0 License | Apache 2.0 许可证

---

## 📞 Links | 相关链接

- [🇨🇳 完整中文文档](README_CN.md)
- [🇺🇸 Full English Docs](README_EN.md)
- [📝 Changelog | 更新日志](CHANGELOG.md)
- [🐛 Issues](https://github.com/xuanoooooo/ai-trading-bot/issues)
- [🔀 Pull Requests](https://github.com/xuanoooooo/ai-trading-bot/pulls)

---

<div align="center">

**⭐ Star this project if it helps you! | 如果有帮助请给星！⭐**

**No fees, no referral codes | 没有收费，没有邀请码** 🌟

Made with ❤️ by AI Trading Community

</div>
