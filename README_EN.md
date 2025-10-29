# 🤖 AI Trading Bot - Single Coin Per Instance (Run Multiple Instances for Multi-Coin Trading)

## 📖 Language Selection / 语言选择

<div align="center">

| [🇺🇸 English](README_EN.md) | [🇨🇳 中文文档](README_CN.md) |
|:---:|:---:|
| **English** | **简体中文** |

</div>

---

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Trading](https://img.shields.io/badge/Trading-Cryptocurrency-orange.svg)](https://binance.com)

> 🚀 **Intelligent cryptocurrency trading bot powered by DeepSeek AI with dynamic position management and fully automated trading decisions**

---

## 📦 Easy Setup Version (For Non-Programmers)

> **🎁 Foolproof deployment package for users without programming experience!**

If you are a user **without programming experience**, we have prepared a ready-to-use version that can be started in just 3 steps:

### ✨ Easy Setup Features

- 🚀 **One-Click Installation** - Auto-detect environment, auto-install dependencies
- 🚀 **One-Click Startup** - Auto-check configuration, auto-start program
- 📝 **Detailed Documentation** - 5-minute quick start guide (Chinese & English)
- 🛡️ **Foolproof Configuration** - .env file with detailed Chinese annotations
- 💡 **Smart Detection** - Auto-diagnose issues and provide solutions
- 🎨 **Colorful Interface** - Linux version supports colorful terminal output
- 🔧 **Background Running** - Linux supports background running and process management

### 📥 Download Easy Setup Version

Download from [Releases](https://github.com/xuanoooooo/ai-trading-bot/releases) page:
- **`AI交易机器人-开箱即用版.tar.gz`** (Recommended, supports Windows/Linux/Mac)

Or get it directly from the project:
```bash
# After downloading the project, the easy setup version is located at:
./GitHub发布版/AI交易机器人-无编程基础用户版.tar.gz
```

### 🚀 3-Step Quick Start

#### Windows Users:
```
1. Extract the archive
2. Double-click scripts/Windows系统一键安装.bat (first time only)
3. Double-click scripts/Windows系统一键启动.bat
```

#### Linux/Mac Users:
```bash
# 1. Extract
tar -xzf AI交易机器人-开箱即用版.tar.gz
cd easy-setup

# 2. Configure API Keys
nano .env  # Fill in your DeepSeek and Binance API keys

# 3. Install and Start
chmod +x scripts/*.sh
bash scripts/Linux系统一键安装.sh
bash scripts/Linux系统一键启动.sh
```

### 📖 Easy Setup Package Contents

```
AI Trading Bot - Easy Setup/
├── 使用说明-请先看我.txt          # Homepage instructions
├── README_快速开始.txt             # Chinese quick guide
├── README_QUICK_START.txt          # English quick guide
├── .env                             # API key configuration (with detailed comments)
├── requirements.txt                 # Python dependencies
├── LICENSE                          # Open source license
│
├── src/
│   └── deepseekBNB.py              # Main program
│
├── scripts/
│   ├── Windows系统一键安装.bat     # Windows installation script
│   ├── Windows系统一键启动.bat     # Windows startup script
│   ├── Linux系统一键安装.sh        # Linux installation script
│   └── Linux系统一键启动.sh        # Linux startup script
│
└── config/
    └── 配置说明.txt                 # Detailed configuration tutorial (9 chapters)
```

---

## 📦 Project Positioning

This is a **Single Coin AI Trading System** (for multiple coins, run multiple program instances simultaneously). Features:
- ✅ **Single Coin Per Instance** - Default BNB/USDT contract (code example), can be modified for other coins
- ✅ **Multi-Coin Solution** - Need multiple coins? Simply run multiple program instances, each trading one coin
- ✅ **Binance Native Library** - Uses python-binance library (not CCXT), better performance
- ✅ **BTC Market Reference** - Keeps Bitcoin as market sentiment reference
- 🛡️ **Risk Isolation Recommendation** - Strongly recommend creating separate Binance sub-accounts for each coin, allowing AI to trade independently and effectively isolate risks. Multi-coin simultaneous operation is still under testing and will be released after confirming no risks

## 📖 Language Selection / 语言选择

<div align="center">

| [🇺🇸 English](README_EN.md) | [🇨🇳 中文文档](README_CN.md) |
|:---:|:---:|
| **English** | **简体中文** |

</div>

---

## ⚠️ **IMPORTANT NOTICES**

### 1. Must Use One-Way Position Mode
**Please ensure your Binance account is set to One-Way Position Mode. Hedge Mode will cause trading failures!**

### 2. For US Users
**⚠️ US users should use Binance.US instead of Binance.com**

- This bot is designed for **Binance.com** (international version)
- If you are in the US, please use **Binance.US** and obtain API keys from there
- You will need to modify the API endpoint in the code to point to Binance.US
- API endpoint for Binance.US: `https://api.binance.us`

### 3. Network Access
If you cannot access Binance API, please resolve network issues on your own.

---

## 🚀 Quick Start

### 📝 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot
```

### 🔑 2. Configure API Keys
Copy the example configuration file and fill in your API keys:
```bash
cp config/env.example .env
nano .env  # or use another editor
```

Fill in the `.env` file:
```env
# DeepSeek API Key (Required)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Binance API Configuration (Required)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret
```

### ⚙️ 3. Modify Trading Configuration (Optional)
Edit `src/deepseekBNB.py` to change trading pair and parameters:
```python
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',        # Trading pair
    'leverage': 3,                # Leverage multiplier
    'timeframe': '15m',           # K-line period
    'position_management': {
        'max_position_percent': 80,  # Maximum position percentage
        'min_position_percent': 5,   # Minimum position percentage
        'force_reserve_percent': 20, # Mandatory buffer funds
    }
}
```

### ▶️ 4. Install Dependencies and Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start with launch script (Recommended)
chmod +x scripts/start_trading.sh
./scripts/start_trading.sh start-tmux

# Or run directly
python src/deepseekBNB.py
```

**More launch options:**
```bash
./scripts/start_trading.sh status    # Check status
./scripts/start_trading.sh stop      # Stop bot
./scripts/start_trading.sh logs      # View logs
```

---

## 📸 Demo Screenshot

<div align="center">

![Terminal Demo](images/terminal-demo.png)

*✨ AI automatically analyzes market data and makes trading decisions - Real-time K-line analysis + Multi-timeframe technical indicators*

</div>

---

## 🔥 Latest Updates

### 🔮 **Coming Soon - 3-Minute Ultra-High Frequency Version (In Testing)**

> **⚡️ Extreme speed version for users who don't mind AI calling costs**

#### 🚨 Important Notes
- ⏱️ **3-Minute Decision Cycle** - AI analyzes market and makes decisions every 3 minutes
- 💰 **Higher AI Calling Costs** - Call frequency increased by 3x+ (from 10 minutes to 3 minutes)
- ⚠️ **Market Noise Risk** - Ultra-short cycles may lead to frequent trading, beware of market noise interference
- 🧪 **Testing Phase** - Currently being validated on test accounts, will be released after confirming no risks
- 🎯 **Use Case** - Suitable for users pursuing ultimate response speed and insensitive to trading costs

**Stay tuned!** We are conducting rigorous testing to ensure stability and safety before release.

---

### 🚀 **v2.1.0 (2025-10-29) - Major Multi-Timeframe Analysis Upgrade**

> **⚡️ This is a MAJOR feature upgrade! AI decision-making capability significantly enhanced!**

#### 📊 Multi-Timeframe Technical Analysis (Core Feature)

- ✨ **Added 1-Hour Timeframe Data** - 30 × 1-hour candles (30-hour history) + Latest 10 indicator trend values
- 📈 **Enhanced 15-Minute Data** - 16 × 15-minute candles (4-hour history) + Latest 10 indicator trend values + Current real-time candle
- ⏰ **Real-Time Candle Data** - AI receives the forming candle (open, current price, high/low, volume, elapsed time)
- 🎯 **Multi-Timeframe Cross-Validation** - Analyzes short-term (15-min) and mid-term (1-hour) simultaneously, avoids short-term noise
- 🧠 **AI Smart Comparison** - Automatically compares data across different timeframes to identify real trends

**Real Example:**
```
AI Decision Reasoning:
"15-minute RSI 57.2 is in neutral zone, MACD declining from highs but still positive,
 1-hour RSI 31.0 shows oversold but price hasn't confirmed bounce,
 ATR shows low volatility"
```
✅ AI can accurately distinguish between short-term and mid-term signals for more rational decisions!

#### 🔧 Other Improvements

- 🔧 **Removed AI Hard-Coded Instructions** - Deleted subjective judgments like "bullish alignment"/"oscillation", 100% objective data
- 📊 **Time Series Optimization** - Clearly marked all data in "old→new" order
- 🔧 **Fixed .env Loading Path** - Resolved configuration file reading issues
- ✨ **Enhanced Startup Script** - Supports system Python3, no virtual environment needed
- ✅ **Complete Testing** - Multi-timeframe data acquisition and AI analysis quality fully tested

---

### ✨ **v2.0 (2025-10-27) - Core Features**
- 📈 **16 K-line Data** - Complete 4-hour short-term data (16 × 15-minute)
- 🎯 **Mandatory K-line + Indicator Analysis** - AI must analyze both K-line patterns and technical indicators
- 📊 **Real-time Current K-line Data** - AI can see forming K-lines (OHLC, volume, volatility)
- 🧠 **AI Decision Memory** - AI sees last 3 decisions (45-minute history), avoids contradictory decisions
- 💾 **Local Trading History** - Auto-saves to trading_stats.json
- 📝 **AI Decision Logs** - Records all decisions to ai_decisions.json
- 🔄 **Binance API Retry Mechanism** - 5 retries + 30s timeout, auto-handles temporary network issues
- 🌐 **BTC Market Reference** - 15-minute BTC data as market sentiment reference

---
#### Bug #2: BNB Precision Error
**Issue:** Code used 3 decimal places `round(amount, 3)`, but BNB only supports 2 decimals, causing order failures.

**Fix:**
- Calculation precision: `round(amount, 3)` → `round(amount, 2)`
- Print format: `.3f` / `.4f` → `.2f`

**Impact:** Prevents `APIError(code=-1111): Precision is over the maximum` error

</details>

---

## ✨ Key Features

### 🧠 **AI-Driven Decisions**
- **DeepSeek AI Analysis** - Advanced LLM-based intelligent market analysis
- **Fully Autonomous** - AI independently analyzes technical indicators without human intervention
- **Dynamic Position Management** - AI intelligently adjusts position sizes based on market conditions

### 📊 **Technical Analysis Engine**
- **Multi-dimensional Indicators** - RSI, MACD, SMA20/50, Bollinger Bands, ATR volatility
- **🚀 Multi-Timeframe Analysis** - 15-minute (short-term) + 1-hour (mid-term) K-lines, cross-validation to avoid misjudgment
- **K-line Pattern Analysis** - 16 historical K-lines (4-hour history) + real-time current K-line
- **Time Series Data** - Last 10 values of indicator trends (old→new, clearly showing trend evolution)
- **BTC Market Reference** - Bitcoin market sentiment as auxiliary judgment

### 🛡️ **Risk Management System**
- **Smart Risk Control** - Maximum 80% position limit with mandatory 20% buffer
- **Leverage Protection** - Fixed 3x leverage for controlled risk
- **Minimum Trade Amount** - Automatic exchange minimum trade requirements check
- **Error Tolerance** - Trade amount precision handling and reasonableness validation

### 🔧 **Technical Architecture**
- **Binance Futures** - Supports Binance futures trading
- **Single Coin Per Instance** - Each program instance trades one coin (default: BNB/USDT). For multiple coins, run multiple instances simultaneously
- **Easy Coin Switching** - Simply modify the `symbol` parameter in code to trade any other coin
- **Persistent Operation** - tmux session management for remote server deployment
- **Complete Logging** - Automatic log rotation with detailed trading records

## 🚀 Quick Start

### 📋 System Requirements
- Python 3.11+
- Linux/macOS/Windows
- Binance account (futures permissions)
- DeepSeek API key

### ⚡ One-Click Installation
```bash
# Clone the project
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot

# Run installation script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 🔧 Manual Installation
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp config/env.example .env
# Edit .env file with your API keys
```

## ⚙️ Configuration

### 🔑 API Key Configuration
Configure in `.env` file:
```env
# DeepSeek AI API
DEEPSEEK_API_KEY=your_deepseek_api_key

# Binance API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret
```

### 📊 Trading Configuration
Modify `TRADE_CONFIG` in `src/deepseekBNB.py`:
```python
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',        # Trading pair
    'leverage': 3,                # Leverage multiplier
    'timeframe': '15m',           # K-line period
    'test_mode': False,           # Live/Test mode
    'position_management': {
        'max_position_percent': 80,  # Maximum position percentage
        'min_position_percent': 5,   # Minimum position percentage
        'force_reserve_percent': 20, # Mandatory buffer funds
    }
}
```

## 🎯 Usage

### 🖥️ Local Operation
```bash
# Activate virtual environment
source venv/bin/activate

# Start trading bot
python src/deepseekBNB.py
```

### 🖥️ Remote Server Deployment
```bash
# Create persistent session with tmux
tmux new -s trading-bot

# Run in tmux
source venv/bin/activate
python src/deepseekBNB.py

# Detach session (program continues running)
# Ctrl+b then press d

# Reconnect to session
tmux attach -t trading-bot
```

### 🚀 Quick Start Script
```bash
# Use provided start script
chmod +x scripts/start_trading.sh
./scripts/start_trading.sh
```

## 📈 AI Decision Process

### 🤖 Information AI Receives
1. **K-line Data** - Recent 16 x 15-minute K-lines (short-term market view)
2. **Technical Indicators** - SMA, RSI, MACD, Bollinger Bands, etc.
3. **Account Information** - Total equity, free balance, margin usage ratio
4. **Position Status** - Current position direction, quantity, P&L
5. **Trading History** - Historical trading records and statistics
6. **Leverage Mechanism** - 3x leverage explanation and calculation method
7. **🔮 Multi-timeframe Analysis** - Coming in next version, supporting 4-hour long-term trend analysis

### 🎯 AI Decision Output
```json
{
    "signal": "BUY|SELL|HOLD",
    "reason": "Analysis reasoning",
    "stop_loss": specific_price,
    "take_profit": specific_price,
    "confidence": "HIGH|MEDIUM|LOW",
    "position_percent": integer_from_0_to_100
}
```

### 💰 Position Calculation
- AI returns percentage → System calculates margin
- Actual position = Margin × 3x leverage
- Automatic risk control limits and precision handling

## 📊 Technical Indicators

### 📈 Moving Averages
- **SMA5/20/50** - Short, medium-term trend analysis
- **EMA12/26** - Exponential moving averages
- **Price Position Relationship** - Percentage position relative to moving averages

### 🎯 Momentum Indicators
- **RSI** - Relative Strength Index (overbought/oversold judgment)
- **MACD** - Moving Average Convergence Divergence
- **Volume Ratio** - Current volume / 20-period average volume ratio

### 🎚️ Bollinger Bands Analysis
- **Upper/Lower Bands** - Dynamic support/resistance levels
- **Position Percentage** - Price position within Bollinger Bands
- **Volatility Analysis** - Market volatility degree

### 💰 Support/Resistance
- **Static Levels** - Based on historical highs/lows
- **Dynamic Levels** - Based on Bollinger Bands
- **Price Relationship** - Percentage distance from key levels

## 🛡️ Risk Management

### ⚠️ Important Reminders
- **Sub-account Recommendation** - Strongly recommend using sub-accounts to limit risk
- **Capital Management** - Only invest funds you can afford to lose
- **API Security** - Safely store API keys with appropriate permissions
- **Operation Monitoring** - Regularly check bot operation status

### 🔒 Risk Control Mechanisms
- **Position Limits** - Maximum 80% fund usage
- **Capital Reserve** - Mandatory 20% buffer funds
- **Minimum Trade Amount** - Automatic exchange requirement checks
- **Precision Handling** - Automatic trade amount precision adjustment

## 📁 Project Structure

```
ai-trading-bot/
├── README.md                 # Project description
├── README_CN.md             # Chinese detailed documentation
├── README_EN.md             # English detailed documentation
├── LICENSE                   # Open source license
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
├── config/                  # Configuration directory
│   ├── env.example        # Environment variable example
│   └── trading_config.json # Trading configuration example
├── src/                     # Source code
│   ├── deepseekBNB.py      # Main trading bot
│   ├── indicators.py       # Technical indicators module
│   └── utils.py            # Utility functions
├── docs/                    # Documentation
│   ├── installation.md     # Installation guide
│   ├── configuration.md    # Configuration guide
│   └── trading_guide.md    # Trading guide
├── examples/               # Examples
│   └── basic_usage.py     # Basic usage example
└── scripts/                # Scripts
    ├── setup.sh           # Installation script
    └── start_trading.sh   # Start script
```

## 🤝 Contributing

### 🐛 Bug Reports
- Use GitHub Issues to report bugs
- Provide detailed error information and logs
- Describe your system environment

### 💡 Feature Suggestions
- Welcome new feature suggestions
- Describe usage scenarios in detail
- Consider implementation feasibility

### 🔧 Code Contributions
1. Fork the project
2. Create feature branch
3. Submit changes
4. Create Pull Request

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE) - see the LICENSE file for details.

## ⚠️ Disclaimer

**Important Risk Warning:**

- 🚨 **Investment Risk** - Cryptocurrency trading involves significant risks
- 💰 **Capital Loss** - May result in total capital loss
- 🤖 **AI Decisions** - Bot decisions do not guarantee profits
- 🔒 **Personal Responsibility** - All risks from using this software are borne by the user
- 📊 **Testing Recommendation** - Recommend testing with small funds first
- 🛡️ **Sub-account** - Strongly recommend using sub-accounts to limit risk

**This software is for learning and research purposes only and does not constitute investment advice. Please fully understand the risks before use and invest carefully.**

## 💰 Support & Thanks

If you have profited from this project, welcome to support:

## 💰 Support the Project

If you've profited from this project, consider supporting:

**Wallet Address (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

---

<div align="center">

**⭐ If this project helps you, please give it a Star! ⭐**

Made with ❤️ by AI Trading Community

</div>

