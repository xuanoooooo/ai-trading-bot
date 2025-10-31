# 🤖 AI Multi-Coin Automated Trading System

<div align="center">

**Let AI Monitor Markets for You | 24/7 Automated Trading | Multi-Coin Portfolio Management**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-purple.svg)](https://www.deepseek.com/)

[🇨🇳 中文](README_CN.md) | [🇺🇸 English](README_EN.md)

</div>

---

## 💭 Author's Note

> *"After experiencing significant life losses and achieving little in crypto trading, I've completely lost confidence in my own abilities.*  
> *Rather than pretending to analyze charts while essentially gambling, it's better to let AI make the decisions—at least it won't panic-sell during market swings.*  
> *This project stems from a simple expectation: Even an imperfect AI is better than me."*

### ⚠️ Important Reminder

**AI trading cannot guarantee profits. Markets are risky, invest cautiously.**  
This project is for educational purposes only. Users assume all trading risks.  
View AI's decision-making abilities rationally, control positions reasonably, and don't blindly trust.

**No fees, no referral codes, just asking for stars** ⭐

---

## 📸 System Interface

### 🎨 Web Dashboard Mode (Recommended)

**Real-time visualization interface showing positions and AI decisions**

![AI Trading Dashboard](docs/images/看板截图.png)

**Dashboard Features:**
- ✅ **Left Panel**: Real-time position list (entry price, current price, PnL, stop-loss/take-profit)
- ✅ **Right Panel**: AI decision log (reasoning, technical indicators, risk assessment)
- ✅ Dark theme, easy on the eyes
- ✅ Auto-refresh every 30 seconds
- ✅ Green for profit, red for loss - crystal clear

### 💻 Terminal Log Mode

**Suitable for server background running, view via SSH**

![AI Trading Logs](docs/images/日志截图.png)

**Terminal Features:**
- ✅ Detailed trading execution logs
- ✅ Real-time display of each AI analysis process
- ✅ Perfect for remote SSH monitoring
- ✅ Lightweight, minimal resource usage

---

## 📖 Project Overview

An automated cryptocurrency trading system based on **DeepSeek AI**, supporting **multi-coin portfolio management** and **real-time visualization dashboard**.

**Differences from Single-Coin Version**:
- ✅ **Multi-Coin Management** - Simultaneously manage multiple coins (BTC, ETH, SOL, etc.)
- ✅ **Smart Allocation** - AI automatically allocates funds and balances portfolio
- ✅ **Market Scanning** - Scans market every 5 minutes to find best trading opportunities
- ✅ **Web Dashboard** - Real-time view of all positions and returns

---

## 🎯 Core Features

### 🧠 **AI-Driven Decision Making**

- **DeepSeek AI Analysis** - Intelligent market analysis based on advanced LLM
- **Fully Autonomous** - AI independently analyzes technical indicators, no human intervention
- **Portfolio Management** - Considers overall positions, avoids over-concentration

### 📊 **Technical Analysis Engine**

- **Multi-Dimensional Indicators** - RSI, MACD, EMA20/50, Bollinger Bands, ATR volatility
- **Multi-Timeframe Analysis** - 1-hour (medium-term) + 4-hour (long-term) cross-validation
- **Candlestick Pattern Analysis** - 16 historical candles + current real-time candle
- **Time Series Data** - Trend of last 10 indicator values (old → new)

### 🛡️ **Risk Management System**

- **Smart Position Allocation** - 20% per coin by default, max 5 positions
- **Auto Stop-Loss/Take-Profit** - 3% stop-loss, 8% take-profit (configurable)
- **Leverage Control** - 3x default, adjustable 1-5x
- **Max Drawdown Protection** - Automatic total risk control

### 📈 **Real-Time Visualization Dashboard**

- **Web Interface** - Flask-powered real-time dashboard
- **Position Monitoring** - View P&L of all positions
- **AI Decision Log** - View reasoning and confidence of each decision
- **Profit Curve** - Visualize profit trend
- **Trading Statistics** - Win rate, total P&L, trade count, etc.

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot
```

### 2. Install Dependencies

```bash
# Run installation script
bash scripts/install.sh

# Or install manually
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

**Required API Keys:**
- **DeepSeek API Key**: Get from [DeepSeek Platform](https://platform.deepseek.com/)
- **Binance API Key**: Create in [Binance](https://www.binance.com/) account settings
  - ⚠️ Futures trading permission required
  - ⚠️ API trading permission required

### 4. Configure AI Model & Trading Coins

**4.1 Configure AI Model (Important!)**

Edit `src/portfolio_manager.py` line 648:

```python
response = deepseek_client.chat.completions.create(
    model="deepseek-chat",  # Default: chat mode (Recommended)
    # model="deepseek-reasoner",  # Reasoning mode (Slow & Expensive, NOT recommended)
```

**AI Model Comparison:**

| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| **deepseek-chat** ✅ | Fast (1-2s) | Cheap ($0.0001/call) | **Default, 5-min scan** |
| deepseek-reasoner | Slow (10-30s) | 50x more ($0.005/call) | Not for high-frequency |

**⚠️ Important:**
- ✅ **Use `deepseek-chat` by default** (already configured)
- ❌ **Don't use `deepseek-reasoner`**: Too expensive for 5-min scanning (Daily cost: $1.44 vs $0.03)

---

**4.2 Configure Trading Coins**

Edit `config/coins_config.json`:

```json
{
  "coins": [
    {
      "symbol": "BTC",
      "binance_symbol": "BTCUSDT",
      "precision": 3,
      "price_precision": 2,
      "min_order_value": 50
    }
    // ... more coins
  ]
}
```

**Default Coins (Recommended):**

| Coin | Pair | Risk | Notes |
|------|------|------|-------|
| **BTC** | BTCUSDT | Low | Market leader |
| **ETH** | ETHUSDT | Low | Second largest |
| **SOL** | SOLUSDT | Medium | High-performance |
| **BNB** | BNBUSDT | Medium | Exchange token |
| **XRP** | XRPUSDT | Medium | Cross-border |
| **ADA** | ADAUSDT | Medium | Academic project |
| **DOGE** | DOGEUSDT | High | High volatility |

**⚠️ Coin Selection Tips:**

1. ✅ **Strongly recommend using default config**
2. ✅ **Must use USDT pairs** (not USDC - less liquidity)
3. ❌ **Avoid coins < $1** (e.g., SHIB $0.00001):
   - Precision issues
   - Order size control problems
4. ❌ **Avoid low-volume coins**:
   - 24h volume should be > $100M
5. ✅ **Recommended mix**: Large caps (BTC/ETH) + Mid caps (SOL/BNB)

**How to add new coins:**

```json
{
  "symbol": "MATIC",
  "binance_symbol": "MATICUSDT",  // Must be USDT pair
  "precision": 0,                 // Quantity decimals
  "price_precision": 4,           // Price decimals
  "min_order_value": 6            // Min order value (USDT)
}
```

### 5. Start Trading Program

```bash
cd src
python portfolio_manager.py
```

**Or use script:**

```bash
bash scripts/start_trading.sh
```

### 6. Start Dashboard (Optional)

```bash
cd dashboard
python web_app.py
```

**Or use script:**

```bash
bash scripts/start_dashboard.sh
```

Then visit: **http://localhost:5000**

---

## 📊 System Architecture

```
ai-trading-bot/
├── src/                          # Core code
│   ├── portfolio_manager.py      # Portfolio manager (main program)
│   ├── market_scanner.py         # Market data scanner
│   └── portfolio_statistics.py   # Trading statistics module
├── dashboard/                    # Web visualization dashboard
│   ├── web_app.py               # Flask application
│   ├── static/                  # Static resources (CSS/JS)
│   └── templates/               # HTML templates
├── config/                       # Configuration files
│   └── coins_config.json        # Coin configuration
├── scripts/                      # Startup scripts
│   ├── install.sh               # Installation script
│   ├── start_trading.sh         # Start trading
│   └── start_dashboard.sh       # Start dashboard
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── LICENSE                      # Apache 2.0 license
└── README.md                    # Project documentation
```

---

## 🧠 AI Decision Flow

### Workflow:

1. **Market Scan** (Every 5 minutes) → Scan configured coins, fetch K-lines and indicators
2. **AI Analysis** → DeepSeek analyzes market data and current portfolio
3. **Decision Generation** → AI provides trading suggestions:
   - `OPEN_LONG` - Open long position
   - `OPEN_SHORT` - Open short position
   - `CLOSE` - Close position
   - `HOLD` - Continue holding
   - `WAIT` - Wait and observe
4. **Risk Check** → Verify decision meets risk control rules
5. **Execute Trade** → Execute via Binance API
6. **Record Keeping** → Save decision process and trading results

---

## ⚠️ Risk Warning

### 🚨 Important Warnings

**Cryptocurrency trading carries extremely high risks:**

| ⚠️ Risk Type | Description |
|---------|------|
| **Principal Risk** | May result in complete loss of principal |
| **Leverage Risk** | Leverage amplifies both gains and losses |
| **Market Risk** | Extreme volatility can cause rapid losses |
| **Technical Risk** | Network issues or API problems may affect trading |
| **AI Decision Risk** | AI doesn't guarantee profits, may make wrong decisions |

### ✅ Safety Recommendations

1. **Start Small** - Begin with 100-500 USDT
2. **Set Stop-Loss** - Strictly follow stop-loss strategy
3. **Diversify** - Don't put all funds in one coin
4. **Regular Checks** - Check account at least once daily
5. **Risk Tolerance** - Only invest what you can afford to lose

---

## 💰 Support Project

If this project helps you, consider supporting:

**Wallet Address (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

Your support motivates continued updates ❤️

---

## 📄 License

This project is licensed under [Apache 2.0](LICENSE)

---

## ⚖️ Disclaimer

This software is for educational and research purposes only. Users assume all responsibility for profits and losses from live trading. The author is not responsible for any losses incurred from using this software.

**Cryptocurrency trading carries high risks. Invest cautiously!**

---

<div align="center">

**⭐ If this project helps you, please give it a Star! ⭐**

**No fees, no referral codes, just asking for stars** 🌟

Made with ❤️ by AI Trading Community

</div>
