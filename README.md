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

[👉 查看中文文档](README_CN.md)

**多币种投资组合管理**  
**24/7全自动运行**  
**实时可视化看板**

</td>
<td width="50%" align="center">

### 🇺🇸 English

[👉 View English Docs](README_EN.md)

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

## ⚠️ Important Reminder | 重要提醒

<table>
<tr>
<td width="50%">

### 🇨🇳 中文

**AI交易无法保证盈利，市场有风险，投资需谨慎。**

本项目仅供学习交流，使用者需自行承担交易风险。

**没有收费也没有挂邀请码，只求各位给星星** ⭐

</td>
<td width="50%">

### 🇺🇸 English

**AI trading cannot guarantee profits. Markets are risky, invest cautiously.**

This project is for educational purposes only. Users assume all trading risks.

**No fees, no referral codes, just asking for stars** ⭐

</td>
</tr>
</table>

---

## 🚀 Quick Start | 快速开始

```bash
# Clone repository | 克隆项目
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot

# Install dependencies | 安装依赖
bash scripts/install.sh

# Configure API keys | 配置API密钥
cp .env.example .env
nano .env

# Start trading | 启动交易
bash scripts/start_trading.sh

# Start dashboard (optional) | 启动看板（可选）
bash scripts/start_dashboard.sh
```

---

## 🎯 Core Features | 核心特性

<table>
<tr>
<th width="50%">🇨🇳 中文</th>
<th width="50%">🇺🇸 English</th>
</tr>
<tr>
<td>

### ✨ 主要功能

- ✅ **AI自主决策** - DeepSeek智能分析
- ✅ **多币种管理** - 同时管理多个币种
- ✅ **技术指标** - RSI、MACD、EMA、布林带
- ✅ **风险控制** - 自动止损、仓位管理
- ✅ **Web看板** - 实时监控持仓和收益

</td>
<td>

### ✨ Main Features

- ✅ **AI Decision Making** - DeepSeek analysis
- ✅ **Multi-Coin Management** - Manage multiple coins
- ✅ **Technical Indicators** - RSI, MACD, EMA, BB
- ✅ **Risk Control** - Auto stop-loss, position management
- ✅ **Web Dashboard** - Real-time monitoring

</td>
</tr>
</table>

---

## 📊 System Architecture | 系统架构

```
ai-trading-bot/
├── src/                          # Core code | 核心代码
│   ├── portfolio_manager.py      # Portfolio manager | 投资组合管理器
│   ├── market_scanner.py         # Market scanner | 市场扫描器
│   └── portfolio_statistics.py   # Statistics | 统计模块
├── dashboard/                    # Web dashboard | Web看板
│   ├── web_app.py               # Flask app | Flask应用
│   ├── static/                  # Static files | 静态文件
│   └── templates/               # HTML templates | HTML模板
├── config/                       # Configuration | 配置文件
├── scripts/                      # Scripts | 启动脚本
├── .env.example                 # Environment template | 环境变量模板
└── requirements.txt             # Dependencies | Python依赖
```

---

## ⚠️ Risk Warning | 风险警告

<table>
<tr>
<td width="50%">

### 🇨🇳 风险提示

**加密货币交易存在极高风险：**

- ⚠️ 可能导致本金全部亏损
- ⚠️ 杠杆会放大盈亏
- ⚠️ 市场剧烈波动可能导致快速亏损
- ⚠️ AI不保证盈利

**安全建议：**

1. 从小金额开始（100-500 USDT）
2. 严格执行止损策略
3. 不要投入无法承受损失的资金

</td>
<td width="50%">

### 🇺🇸 Risk Warning

**Cryptocurrency trading carries extremely high risks:**

- ⚠️ May result in complete loss of principal
- ⚠️ Leverage amplifies gains and losses
- ⚠️ Extreme volatility can cause rapid losses
- ⚠️ AI doesn't guarantee profits

**Safety Recommendations:**

1. Start small (100-500 USDT)
2. Strictly follow stop-loss strategy
3. Only invest what you can afford to lose

</td>
</tr>
</table>

---

## 💰 Support Project | 支持项目

<div align="center">

**If this project helps you, consider supporting:**  
**如果这个项目对你有帮助，欢迎支持：**

**Wallet Address (BEP20/BSC) | 钱包地址**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

Your support motivates continued updates ❤️  
您的支持是我持续更新的动力 ❤️

</div>

---

## 📖 Documentation | 文档

- 🇨🇳 [完整中文文档](README_CN.md)
- 🇺🇸 [Full English Documentation](README_EN.md)

---

## 📄 License | 许可证

This project is licensed under [Apache 2.0](LICENSE)  
本项目采用 [Apache 2.0](LICENSE) 许可证

---

## ⚖️ Disclaimer | 免责声明

<table>
<tr>
<td width="50%">

本软件仅供学习和研究使用。使用本软件进行实盘交易的任何盈亏由用户自行承担。作者不对使用本软件造成的任何损失负责。

**加密货币交易具有高风险，请谨慎投资！**

</td>
<td width="50%">

This software is for educational and research purposes only. Users assume all responsibility for profits and losses from live trading. The author is not responsible for any losses.

**Cryptocurrency trading carries high risks. Invest cautiously!**

</td>
</tr>
</table>

---

<div align="center">

**⭐ If this project helps you, please give it a Star! | 如果这个项目对你有帮助，欢迎Star支持！⭐**

**No fees, no referral codes, just asking for stars**  
**没有收费，没有邀请码，只求各位给个星星** 🌟

Made with ❤️ by AI Trading Community

</div>
