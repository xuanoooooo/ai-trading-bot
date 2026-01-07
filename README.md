# 🚀 AI Multi-Coin Portfolio Management System

English | [简体中文](README_CN.md)

> ⚠️ **Important**: This project supports **multiple exchanges** (Gate.io/Binance/OKX/Bybit) via CCXT library. Ensure your exchange account is set to **one-way position mode**.

## 💬 Author's Note

"After experiencing major losses in life and achieving nothing in crypto, I've completely lost faith in my own abilities. Instead of pretending to analyze charts while actually gambling, I'd rather let AI make the decisions—at least it won't go all-in due to market volatility. This project stems from a simple expectation: AI, however imperfect, is still better than me."

## 💰 Support This Project

If this project helps you, donations are appreciated.

**Network**: BEP20 / BSC
**Wallet Address**: `0x59B7c28c236E6017df28e7F376B84579872A4E33`

---

## 📥 Installation & Deployment

### Recommended Directory Structure

To maintain consistency with the project's path configuration, we recommend the following deployment structure:

```bash
# Clone the project
git clone https://github.com/xuanoooooo/ai-trading-bot.git duobizhong

# Or manually create directory
mkdir -p duobizhong
cd duobizhong
# Then place project files in this directory
```

**Important Notes**:
- The project's internal path configuration uses `duobizhong` as the root directory name
- If using a different directory name, modify the `PROJECT_ROOT` variable in:
  - `src/core/portfolio_manager.py` (line 50)
  - `src/core/market_scanner.py` (line 12)
- Example commands in README (e.g., `/root/ziyong/duobizhong`) are for reference only; adjust to your actual path

### Requirements

- Python 3.7+
- tmux (required for background execution)
- Exchange account (Gate.io/Binance/OKX/Bybit)
- OpenAI-compatible API (DeepSeek/SiliconFlow/Groq/OpenAI, etc.)

### Quick Start

1. **Install Dependencies**
```bash
pip3 install ccxt openai python-dotenv schedule pandas flask flask-cors
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
vim .env  # Fill in your API keys

# Configure exchange in config/coins_config.json
vim config/coins_config.json  # Set "exchange": "gateio" or "binance"
```

3. **Start Trading Program**
```bash
./scripts/start_portfolio.sh
```

For detailed deployment instructions, refer to the "Server Migration Guide" section below.

## 🎯 Core Features

- **Multi-Exchange Support**: Supports Gate.io/Binance/OKX/Bybit via CCXT, switch by config file ⭐NEW
- **AI Portfolio Manager**: Autonomous decision-making, dynamic rebalancing, flexible long/short positions
- **Complete Prompt Separation**: Code only passes data, strategies are in external files—modify strategies without touching code
- **Automatic Stop-Loss Protection**: Stop-loss orders placed on exchange immediately upon opening, AI can adjust dynamically
- **Objective Information Feedback**: Records stop-loss trigger history, objectively informs AI of market events
- **Four-Timeframe Analysis**: 5m (execution) + 15m (tactical) + 1h (strategic) + 4h (strategic) + BTC market overview
- **Complete Statistics**: Per-coin + overall + position synchronization
- **Visual Dashboard**: Web real-time monitoring (Flask), reads exchange API directly
- **Technical Indicator Analysis**: RSI, MACD, ATR, EMA, Bollinger Bands, and more

## 📈 Core Architecture Design

### 🎯 Prompt Architecture Optimization - Complete Code-Strategy Separation ⭐Core Feature

**Core Philosophy**: System Message (immutable rules) vs User Message (dynamic data)

This is the project's most important architectural design, achieving **complete decoupling of code and strategy**:
- **Modify Trading Strategy**: Just edit external text file `prompts/default.txt`, no code changes needed
- **Adjust System Rules**: Hard constraints like fund protection and stop-loss mechanisms stay in code for safety
- **Flexible Switching**: Create multiple strategy files (aggressive/conservative/balanced), switch anytime

#### 📋 Three-Layer Prompt Structure

**1️⃣ System Message - System Hard Rules** (in code, immutable)

Location: `portfolio_manager.py:510-577`

**Contains**:
- **JSON Format Specification**: Ensures AI returns parseable standard JSON structure
- **Moving Stop-Loss Mechanism**: Fill in new price on HOLD, system auto-updates stop-loss order
- **Hard Safety Rules**:
  - Fund Protection: Must reserve 10% of total assets as buffer
  - Fixed Leverage: 5x leverage (managed via config file `coins_config.json`)
  - Minimum Opening: Global 13 USDT + coin-specific limits (dynamically read from config)
  - Stop-Loss Required: All openings must provide stop-loss price

**Why Hard-Coded**: ✅ Ensure system safety | ✅ Guarantee correct format | ✅ Prevent exchange rule violations

---

**2️⃣ User Message - External Trading Strategy** (freely modifiable, no code changes)

Location: `prompts/default.txt`

**Contains**:
- 📋 Trading identity & style positioning (intraday/swing/long-term)
- 🎯 Decision authority & philosophy (autonomous decision-making, observing is also a decision)
- 📊 Multi-timeframe analysis framework (how to use 5m/15m/1h/4h data)
- 🎲 Entry signal standards (specific technical conditions for long/short)
- 💰 Position management strategy (position allocation for strong/medium/weak signals)
- ⏱️ Holding time & frequency control
- 🛡️ Stop-loss & take-profit strategy (ATR reference, trailing take-profit)
- 📈 Performance targets (Sharpe ratio, maximum drawdown)

**How to Modify Strategy**:
```bash
# 1. Edit strategy file directly
vim prompts/default.txt

# 2. Create multiple strategy versions for testing
cp prompts/default.txt prompts/aggressive.txt   # Aggressive strategy
cp prompts/default.txt prompts/conservative.txt # Conservative strategy

# 3. Restart program to take effect
pkill -f portfolio_manager.py && ./scripts/start_portfolio.sh
```

**Advantages**: ✅ Zero code modification | ✅ Quick strategy testing | ✅ Easy version control

---

**3️⃣ Dynamic Market Data** (real-time updates with each call)

Location: `portfolio_manager.py:478-507`

**Contains**:
- ⏰ System status: start time, runtime, call count
- 💰 Fund status: total assets, used margin, available balance, margin usage rate
- 📊 **Multi-timeframe market data** (detailed below)
- 🏦 Current positions: floating P&L, stop-loss & take-profit prices
- 📈 Historical statistics: win rate, P&L records
- 📝 Recent decisions: AI's historical decisions and results

**Fund Calculation Logic** (Important):
```
Maximum Available Margin = Total Assets × 90% - Used Margin

Example:
- Initial: total=100, used=0  → available = 90-0  = 90
- Open 50: total=100, used=50 → available = 90-50 = 40
- Open 30: total=100, used=80 → available = 90-80 = 10
```

---

#### 📊 Multi-Timeframe Candlestick & Technical Indicator System

Provides AI with complete multi-timeframe market perspective, supporting analysis from short-term execution to long-term strategy:

**Candlestick Data Coverage**:
- **5-minute** (13 candles, ~1 hour): Execution layer, capture short-term entry timing
- **15-minute** (16 candles, 4 hours): Tactical layer, judge short-term trends
- **1-hour** (10 candles, ~10 hours): Strategic layer, medium-term trend analysis
- **4-hour** (6 candles, 24 hours): Strategic layer, daily trend direction

**Technical Indicators Configuration**:
- **15-minute/1-hour**: EMA20/50, RSI(14), MACD, ATR(14), Bollinger Bands
- **4-hour**: EMA20/50, ATR(14) (lightweight, avoid information redundancy)
- **Market Sentiment**: Funding rate, open interest, 24h/15m price change

**Data Format Example**:
```
【15-Minute Candlesticks】Latest 16:
  K1: 🟢 O:3245.50 H:3250.00 L:3240.00 C:3248.00 (+0.08%) V:1234.5
  K2: 🔴 O:3248.00 H:3252.00 L:3242.00 C:3244.00 (-0.12%) V:1456.7
  ...
```

**Advantages**: ✅ AI can observe candlestick patterns | ✅ Multi-timeframe trend resonance | ✅ Balance information & cost

**Code Location**:
- `market_scanner.py:157-296` - Multi-timeframe data retrieval
- `portfolio_manager.py:234-254, 394-435` - Data formatting & delivery

---

#### 🔧 Dynamic Config Reading & OpenAI API Compatibility

**Minimum Opening Amount**: Dynamically read from `coins_config.json`, auto-synced to AI prompts
```python
# Auto-generated and inserted into System Message
Coin limits: BTC 50 | ETH 24 | SOL 13 | BNB 13 | ...
```

**Flexible AI Service Provider Switching**:
```bash
# .env file configuration (supports all OpenAI-compatible APIs)
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat

# Supported provider examples:
# DeepSeek:     https://api.deepseek.com          | deepseek-chat
# SiliconFlow:  https://api.siliconflow.cn/v1     | deepseek-ai/DeepSeek-V2.5
# Groq:         https://api.groq.com/openai/v1    | llama-3.1-70b-versatile
# OpenAI:       https://api.openai.com/v1         | gpt-4o
```

**Advantages**: ✅ Config changes take effect immediately | ✅ Single source of truth | ✅ No manual sync

---

### 🎯 Binance Trading Precision Settings ✅

**Precision Configuration**:
- **Quantity Precision**: BTC/ETH 0.001 | SOL 0.1 | BNB 0.01 | XRP/ADA/DOGE integer
- **Price Precision**: BTC/ETH/SOL/BNB 2 decimals | XRP/ADA/DOGE 4 decimals
- **Minimum Amount**: Global 13 USDT | BTC 50 | ETH 24

**Smart Rounding Algorithm**:
- ✅ Auto-select floor/ceil, minimize error (tested ≤15%)
- ✅ Global 13 USDT hard-coded protection (no coin below this value)
- ✅ Config file: `config/coins_config.json`

**Test Verification**: All coin precisions meet Binance requirements, no order rejection issues

## 📁 Project Structure

```
duobizhong/
├── src/core/                      # Core trading logic
│   ├── portfolio_manager.py       # Portfolio management main program
│   ├── market_scanner.py          # Market data scanner
│   └── portfolio_statistics.py    # Portfolio statistics module
├── web/                           # Web visualization interface
│   ├── web_app.py                 # Flask backend app
│   ├── templates/index.html       # Frontend page template
│   ├── static/                    # CSS/JS resources
│   └── start_web.sh               # Web service startup script
├── scripts/                       # Scripts directory
│   ├── start_portfolio.sh         # Trading program startup script
│   └── 清理历史记录.sh            # History cleanup script
├── data/                          # Data files directory
│   ├── ai_decisions.json          # AI decision history
│   ├── portfolio_stats.json      # Portfolio statistics data
│   └── current_runtime.json       # Current runtime status
├── config/                        # Config files directory
│   └── coins_config.json          # Coin config (precision, min amount)
├── prompts/                       # Prompts directory
│   └── default.txt                # Default trading strategy (fully external)
└── docs/                          # Documentation directory
    └── ...
```

## 🚀 Quick Start

### Trading Program

```bash
cd /root/ziyong/duobizhong
./scripts/start_portfolio.sh       # Start
tmux attach -t portfolio           # View
pkill -f portfolio_manager.py      # Stop
```

### Visual Dashboard

```bash
cd /root/ziyong/duobizhong/web
./start_web.sh                    # Start (background)
pkill -f web_app.py              # Stop

# SSH tunnel access (local secure)
ssh -L 5000:localhost:5000 user@server
# Browser: http://localhost:5000
```

## 🖥️ Visual Dashboard

### Features
- 📊 Account Overview: Funds, P&L (realized + floating), win rate, trade count
- 🪙 Current Positions: Real-time display of coin positions + floating P&L + stop-loss/take-profit prices
- 📜 Trade History: Latest 15 trade records
- 🤖 AI Decision Log: Latest 10 AI decisions and rationale
- 📈 P&L Curve: Cumulative P&L trend chart
- 💹 Real-time Prices: BTC/ETH/SOL/BNB/XRP/ADA/DOGE

### Tech Stack
- **Backend**: Flask (listens on localhost only, SSH tunnel access)
- **Data Source**: Binance API (account, positions) + local files (trade history)
- **Frontend**: Chart.js + vanilla JS + dark theme
- **Update Frequency**: 10s (positions/stats/prices) | on new trades (curve)

## 📝 Common Commands

```bash
# Trading program
tail -f portfolio_manager.log     # View logs
tmux attach -t portfolio           # Connect to session
pkill -f portfolio_manager.py      # Stop program

# Dashboard
tail -f web/web_app.log       # View logs
pkill -f web_app.py                # Stop dashboard
```

---

### 🔄 Clear History

**Use Cases**: Let AI start from scratch | Test new strategies | System reset

**How to Run**:
```bash
cd /root/ziyong/duobizhong
./scripts/清理历史记录.sh
```

**Features**:
- ✅ Auto-stop all running programs
- ✅ Backup to `backups/backup_YYYYMMDD_HHMMSS/`
- ✅ Clear AI decision history, stats data, runtime logs
- ⚠️ Reminder to check Binance account has no positions

**Restore Backup**:
```bash
ls -lh backups/  # View all backups
cp backups/backup_20251111_134530/* data/  # Restore specific backup
```

---

## 🐛 Common Issues

**Position Not Syncing**: Auto-syncs on startup, Binance is source of truth

**Dashboard Load Failed**: Check if Web service is running, restart: `pkill -f web_app.py && cd web && ./start_web.sh`

**Precision/Order Error**: Fully fixed, config file: `config/coins_config.json`

**Quantity 0 Error**: Target amount below minimum limit (Global 13 USDT | BTC 50 | ETH 24)

## 📝 Important Files

- `config/coins_config.json` - Coin configuration (precision, min amount, leverage)
- `prompts/default.txt` - **External trading strategy** ⭐Start here to modify strategies
- `data/portfolio_stats.json` - Statistics data (includes stop-loss trigger history)
- `data/ai_decisions.json` - AI decision log
- `scripts/清理历史记录.sh` - Cleanup script

## 📦 Server Migration Guide

### System Environment Setup

```bash
# Install necessary tools (Ubuntu/Debian)
apt update && apt install -y python3 python3-pip tmux git

# Install Python dependencies
pip3 install ccxt openai python-dotenv schedule pandas flask flask-cors
```

### Configure Environment Variables

```bash
cp .env.example .env
vim .env
```

**Required Config**:
- Exchange API Keys (choose one):
  - `GATEIO_API_KEY` / `GATEIO_SECRET` - Gate.io
  - `BINANCE_API_KEY` / `BINANCE_SECRET` - Binance
  - `OKX_API_KEY` / `OKX_SECRET` / `OKX_PASSWORD` - OKX
  - `BYBIT_API_KEY` / `BYBIT_SECRET` - Bybit
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL_NAME` - AI service provider
- Set exchange in `config/coins_config.json`: `"exchange": "gateio"` (or binance/okx/bybit)

**Supported AI Providers**: DeepSeek | SiliconFlow | Groq | OpenAI (any OpenAI-compatible API)

### Start Program

```bash
chmod +x scripts/start_portfolio.sh web/start_web.sh
./scripts/start_portfolio.sh  # Start trading program
```

For detailed migration steps, refer to the project docs directory.

## 🚨 Risk Warning

Cryptocurrency trading carries high risk, 5x leverage amplifies both gains and losses. Recommend testing mode first and continuous monitoring. This project is for educational purposes only, use at your own risk.

---
