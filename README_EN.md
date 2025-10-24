# 🤖 AI Trading Bot - DeepSeek Automated Trading

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Trading](https://img.shields.io/badge/Trading-Cryptocurrency-orange.svg)](https://binance.com)

> 🚀 **Intelligent cryptocurrency trading bot powered by DeepSeek AI with dynamic position management and fully automated trading decisions**

## 📖 Documentation Language / 文档语言

<div align="center">

[![English](https://img.shields.io/badge/English-🇺🇸-blue.svg)](README_EN.md)
[![中文](https://img.shields.io/badge/中文-🇨🇳-red.svg)](README_CN.md)

</div>

<img width="1124" height="877" alt="图片" src="https://github.com/user-attachments/assets/4e31f5dd-94eb-4590-b5a6-88f725b865c8" />

## ⚠️ **IMPORTANT: Must Use One-Way Position Mode**
**Please ensure your Binance account is set to One-Way Position Mode, Hedge Mode will cause trading failures!**

## 💰 If you have profited from this project, welcome to support:
## 💰 **Wallet AddressBEP20/BSC**
# `0x59B7c28c236E6017df28e7F376B84579872A4E33`

## 🚀 Quick Start (Simplest)

### 📝 1. Modify Trading Configuration
Edit in `src/deepseekBNB.py`:
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

### 🔑 2. Configure API Keys
Create `.env` file with your API keys:
```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret

# OKX API Configuration (Optional)
OKX_API_KEY=your_okx_api_key
OKX_SECRET=your_okx_secret
OKX_PASSWORD=your_okx_password
```

### ▶️ 3. Run
```bash
# Install dependencies
pip install -r requirements.txt

# Start trading bot
python src/deepseekBNB.py
```

**Download these 2 files and you're basically ready to go!** 🎉

---

## ✨ Key Features

### 🧠 **AI-Driven Decisions**
- **DeepSeek AI Analysis** - Advanced LLM-based intelligent market analysis
- **Fully Autonomous** - AI independently analyzes technical indicators without human intervention
- **Dynamic Position Management** - AI intelligently adjusts position sizes based on market conditions

### 📊 **Technical Analysis Engine**
- **Multi-dimensional Indicators** - SMA, EMA, MACD, RSI, Bollinger Bands, Volume analysis
- **Support/Resistance Detection** - Automatic calculation of static and dynamic levels
- **Trend Analysis** - Price momentum and trend continuity analysis
- **Real-time Data** - 15-minute K-line data with 96 historical data points

### 🛡️ **Risk Management System**
- **Smart Risk Control** - Maximum 80% position limit with mandatory 20% buffer
- **Leverage Protection** - Fixed 3x leverage for controlled risk
- **Minimum Trade Amount** - Automatic exchange minimum trade requirements check
- **Error Tolerance** - Trade amount precision handling and reasonableness validation

### 🔧 **Technical Architecture**
- **Binance Futures** - Supports Binance futures trading
- **Multi-currency Support** - Configurable trading pairs (BNB/USDT, DOGE/USDT, etc.)
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
1. **K-line Data** - Recent 5 x 15-minute K-lines
2. **Technical Indicators** - SMA, RSI, MACD, Bollinger Bands, etc.
3. **Account Information** - Total equity, free balance, margin usage ratio
4. **Position Status** - Current position direction, quantity, P&L
5. **Leverage Mechanism** - 3x leverage explanation and calculation method

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
- **SMA5/20/50** - Short, medium, long-term trends
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

## 💰 **Wallet Address BEP20/BSC**
# `0x59B7c28c236E6017df28e7F376B84579872A4E33`

- 💝 **Thanks for Support** - If profitable brothers are willing to remember me kindly
- 📖 **Documentation** - Check docs/ directory for detailed usage instructions
- 🔧 **Technical Issues** - Please check log files to troubleshoot problems
- ⚠️ **Risk Reminder** - Investment has risks, please use carefully

---

**⭐ If this project helps you, please give it a Star!**

