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

## 🎁 Quick Start for Beginners (Recommended)

**📢 No programming experience? No problem!**

We've prepared an easy-setup version that's ready to use out of the box!

### 🚀 Super Simple Start (3 Steps Only)

#### Step 1: Download Easy-Setup Version

📦 **Download the package (Recommended):**

👉 [Click to download ai-trading-bot-easy-setup-v2.3.0.tar.gz](https://github.com/xuanoooooo/ai-trading-bot/releases/latest)

Or find "Releases" on the project page → Download latest version

**After extraction:**
```
ai-trading-bot/
├── 一键开箱版/          ← 👈 Open this folder!
│   ├── start.bat                   ← Start trading (Windows)
│   ├── start_dashboard.bat         ← Start dashboard (Windows)
│   └── stop.bat                    ← Stop program (Windows)
├── src/                 ← Program code
├── config/              ← Configuration
└── .env                 ← 👈 Need to edit this file
```

#### Step 2: Get API Keys

**1. DeepSeek Key** (AI brain for analysis)
- Visit https://platform.deepseek.com/
- Register and get API Key

**2. Binance Key** (Execute trades)
- Visit https://www.binance.com/
- API Management → Create Key
- ⚠️ Must enable: Futures Trading + Enable Trading
- ⚠️ Must set: **One-way Mode**

#### Step 3: Configure and Start

**1. Edit `.env` file**

Find `.env` in project root, open with notepad, fill in 3 keys:

```bash
DEEPSEEK_API_KEY=sk-xxxxx        # 👈 Fill in DeepSeek key
BINANCE_API_KEY=xxxxx            # 👈 Fill in Binance API Key  
BINANCE_SECRET=xxxxx             # 👈 Fill in Binance Secret Key
```

Save and close.

**2. Start Program**

**Windows Users (Super Easy):**
- Go to `一键开箱版/` folder
- Double-click `start.bat` → Start trading
- Double-click `start_dashboard.bat` → Start dashboard (optional)
- Browser visit: http://localhost:5000

**Linux/Mac Users:**
```bash
bash scripts/start_trading.sh        # Start trading
bash scripts/start_dashboard.sh      # Start dashboard
```

### ✅ Default Configuration (No Need to Modify)

**Optimized configuration, strongly recommended to use as-is:**

| Config | Default | Description |
|--------|---------|-------------|
| Trading Pairs | BTC, ETH, SOL, BNB, XRP, ADA, DOGE | 7 major coins |
| Leverage | 3x | Conservative level |
| Scan Interval | 5 minutes | Matches 15-min K-line |
| AI Model | deepseek-chat | Fast & cheap |
| Cash Reserve | 10% | Keep 10% cash as buffer |
| Max Per Coin | 100% (No limit) | AI decides position allocation |

### 💡 Usage Tips

**Minimum Capital:** 100 USDT (Recommend 200-500 USDT)  
**First Use:** Observe for 1-3 days to understand AI logic  
**Environment:** Cloud server is best (24/7 running)

### 🆘 Common Issues

**❓ Can't find files?**  
→ Make sure you're in the `ai-trading-bot` folder

**❓ API error?**  
→ Check if keys in `.env` are correct (no spaces)

**❓ Permission denied?**  
→ Check if Binance API has "Futures Trading" permission

**❓ Want more details?**  
→ See `一键开箱版/README_开箱版.md` or continue reading full documentation below

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

### 🔬 Technical Advantages (What Makes Us Different)

| Feature | Regular Bots | This Project |
|---------|-------------|--------------|
| **Timeframe Analysis** | Single period (e.g., 15-min only) | **15-min + 1-hour + 4-hour** triple cross-validation ✨ |
| **Market Context** | Only individual coin data | **Always reference BTC market sentiment** 🎯 |
| **Decision Basis** | Single-dimension judgment | **Short/Medium/Long-term combined**, avoid false breakouts 🛡️ |
| **Reliability** | Easily fooled by short-term noise | **Multi-timeframe verification**, more robust 💪 |

**Why Multi-Timeframe Analysis Matters:**
- 📉 15-min shows uptrend → 1-hour reveals downtrend → AI stays cautious
- 📈 15-min + 1-hour + 4-hour all bullish → BTC also rising → AI opens long with high confidence
- 🎯 Dramatically reduces false signals, improves win rate

---

## 🎯 Core Features

### 🧠 **AI-Driven Decision Making**

- **DeepSeek AI Analysis** - Intelligent market analysis based on advanced LLM
- **Fully Autonomous** - AI independently analyzes technical indicators, no human intervention
- **Portfolio Management** - Considers overall positions, avoids over-concentration

### 📊 **Technical Analysis Engine (Core Advantage)**

- **🌟 Multi-Timeframe Cross-Validation** - 15-min + 1-hour + 4-hour triple-period analysis
- **🔥 Short/Medium/Long-Term Combined** - 15-min captures short-term opportunities, 1-hour grasps trends, 4-hour validates direction
- **📊 BTC Market Sentiment** - Every decision references BTC movement, avoiding counter-trend trades
- **🎯 Comprehensive Indicators** - RSI, MACD, EMA, Bollinger Bands, ATR volatility
- **📈 Candlestick Pattern Analysis** - 16 historical candles + current real-time candle
- AI makes data-driven decisions based on multi-dimensional analysis

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

**How to add new coins (e.g., MATIC):**

**Before adding (7 default coins):**
```json
{
  "coins": [
    {"symbol": "BTC", "binance_symbol": "BTCUSDT", "precision": 3, "price_precision": 2, "min_order_value": 50},
    {"symbol": "ETH", "binance_symbol": "ETHUSDT", "precision": 3, "price_precision": 2, "min_order_value": 24},
    {"symbol": "SOL", "binance_symbol": "SOLUSDT", "precision": 1, "price_precision": 2, "min_order_value": 6},
    {"symbol": "BNB", "binance_symbol": "BNBUSDT", "precision": 2, "price_precision": 2, "min_order_value": 12},
    {"symbol": "XRP", "binance_symbol": "XRPUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6},
    {"symbol": "ADA", "binance_symbol": "ADAUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6},
    {"symbol": "DOGE", "binance_symbol": "DOGEUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6}
  ]
}
```

**After adding MATIC (8 coins):**
```json
{
  "coins": [
    {"symbol": "BTC", "binance_symbol": "BTCUSDT", "precision": 3, "price_precision": 2, "min_order_value": 50},
    {"symbol": "ETH", "binance_symbol": "ETHUSDT", "precision": 3, "price_precision": 2, "min_order_value": 24},
    {"symbol": "SOL", "binance_symbol": "SOLUSDT", "precision": 1, "price_precision": 2, "min_order_value": 6},
    {"symbol": "BNB", "binance_symbol": "BNBUSDT", "precision": 2, "price_precision": 2, "min_order_value": 12},
    {"symbol": "XRP", "binance_symbol": "XRPUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6},
    {"symbol": "ADA", "binance_symbol": "ADAUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6},
    {"symbol": "DOGE", "binance_symbol": "DOGEUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6},
    {"symbol": "MATIC", "binance_symbol": "MATICUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6}  ⬅️ New
  ]
}
```

**Parameter Explanation:**
- `symbol`: Coin symbol (for display)
- `binance_symbol`: Binance trading pair (must end with **USDT**)
- `precision`: Quantity decimal places (check Binance futures page)
- `price_precision`: Price decimal places
- `min_order_value`: Minimum order value for this coin (USDT)

**Coin Selection Rules:**
- ✅ Must be USDT pairs
- ✅ Coin price ≥ $1 (avoid SHIB, PEPE, etc.)
- ✅ 24h trading volume > $100M
- 💡 Recommended: AVAX, LINK, DOT, ATOM, LTC, UNI

---

**4.3 Risk Management Parameters**

In `config/coins_config.json` under `portfolio_rules`:

```json
"portfolio_rules": {
  "leverage": 3,                    // Leverage (1-5x, recommend 3x)
  "min_cash_reserve_percent": 10,   // Min cash reserve % (10 = keep 10%)
  "max_single_coin_percent": 100    // Max % per coin (100 = no limit)
}
```

**Parameter Details:**

**`leverage`**: Leverage multiplier
- 3 = Use 3x leverage
- Recommend 2-3x (higher leverage = higher risk)

**`min_cash_reserve_percent`**: Minimum cash reserve percentage
- 10 = Keep 10% of available balance reserved
- Example: Total 100 USDT, set to 10, at least 10 USDT reserved, max 90 USDT for positions
- Recommend: 10-20 (keep 10-20% as buffer)

**`max_single_coin_percent`**: Max position size per coin
- 100 = Allow single coin to use 100% of available balance (no limit)
- 50 = Single coin max 50% of available balance
- 30 = Single coin max 30% of available balance
- AI will allocate within this limit

**Suggested Configs:**
- Conservative: `leverage: 2`, `min_cash_reserve_percent: 20`, `max_single_coin_percent: 30`
- Balanced: `leverage: 3`, `min_cash_reserve_percent: 10`, `max_single_coin_percent: 50`
- Aggressive: `leverage: 5`, `min_cash_reserve_percent: 10`, `max_single_coin_percent: 100`

---

**4.4 Other Important Parameters**

In `src/portfolio_manager.py`, `PORTFOLIO_CONFIG` section:

```python
PORTFOLIO_CONFIG = {
    'leverage': 3,                    # Leverage (keep consistent with coins_config.json)
    'check_interval_minutes': 5,      # Scan interval (5 minutes)
    'test_mode': False                # False=Live trading, True=Test mode
}
```

**Parameter Explanation:**
- `leverage`: Leverage multiplier (recommend keeping consistent with `coins_config.json`)
- `check_interval_minutes`: AI analysis interval (**NOT recommended to modify**)
  - Default: 5 minutes
  - ⚠️ **Changing this will cause K-line data mismatch**: The program uses **15-min + 1-hour + 4-hour** multi-timeframe cross-validation. 5-minute interval perfectly captures 15-min K-line changes
  - If changed to other values (e.g., 10 minutes), you'll miss critical K-line pattern changes
- `test_mode`: Test mode switch
  - `False`: Live mode, real orders
  - `True`: Test mode, analysis only without real orders (recommended for beginners)

---

### 5. Start Trading Program

**Using script (Recommended)**

```bash
# Start trading program
bash scripts/start_trading.sh
```

**Or start manually**

```bash
cd src
python3 portfolio_manager.py
```

**Stop trading program**

```bash
# Using script (Recommended)
bash scripts/stop_trading.sh

# Or stop manually
pkill -f portfolio_manager.py
```

---

### 6. Start Dashboard (Optional)

**Using script (Recommended)**

```bash
# Start dashboard
bash scripts/start_dashboard.sh

# Visit: http://localhost:5000
# Or: http://your-server-ip:5000
```

**Stop dashboard**

```bash
# Using script (Recommended)
bash scripts/stop_dashboard.sh

# Or stop manually
pkill -f web_app.py
```

---

### 📋 Quick Command Reference

| Action | Command |
|--------|---------|
| 🚀 Start Trading | `bash scripts/start_trading.sh` |
| 🛑 Stop Trading | `bash scripts/stop_trading.sh` |
| 🎨 Start Dashboard | `bash scripts/start_dashboard.sh` |
| 🛑 Stop Dashboard | `bash scripts/stop_dashboard.sh` |
| 📊 View Logs | `tail -f logs/portfolio_manager.log` |

---

## 💡 Advanced: Running with tmux (Recommended)

**Why use tmux?**

If you're running the trading program on a remote server via SSH, **tmux is highly recommended**:

### ✅ tmux Advantages

| Scenario | Without tmux | With tmux |
|----------|-------------|-----------|
| **SSH Disconnect** | ❌ Program stops | ✅ Program keeps running |
| **View Logs** | ❌ Need tail -f | ✅ Direct terminal output |
| **Reconnect** | ❌ Cannot recover | ✅ Resume exactly where you left off |
| **Multi-window** | ❌ Need multiple SSH | ✅ Multiple windows in one SSH |

### 📝 tmux Basic Usage

**Start Trading Program (tmux version)**

```bash
# Create a tmux session named "portfolio"
tmux new -s portfolio

# Start trading program in tmux (Note: cd to project's src directory first)
cd ai-trading-bot/src
python3 portfolio_manager.py
```

**Detach tmux (program continues running)**

```bash
# Press keyboard shortcut:
Ctrl + B, then press D
# Now you can safely close SSH, program still runs
```

**Reattach to view**

```bash
# After SSH reconnect, resume tmux session
tmux attach -t portfolio
# Instantly see real-time output, as if never disconnected
```

**Other useful commands**

```bash
# List all tmux sessions
tmux ls

# Stop program and exit tmux
Ctrl + C (stop program)
exit (exit tmux)

# Or directly kill session
tmux kill-session -t portfolio
```

### 🎯 Recommended Use Cases

- ✅ **Server Deployment**: Program needs long-term running
- ✅ **Remote Monitoring**: Check real-time logs anytime via SSH
- ✅ **Debugging**: Convenient to observe AI decision process
- ⚠️ **Production**: Can also use systemd service (more advanced)

### ⚠️ Notes

- tmux is not mandatory, you can also use Docker or systemd
- For local running, direct terminal execution is fine
- Dashboard usually doesn't need tmux, background running is sufficient

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
