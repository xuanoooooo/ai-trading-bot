# 🤖 AI自动交易机器人 - DeepSeek智能交易

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Trading](https://img.shields.io/badge/Trading-Cryptocurrency-orange.svg)](https://binance.com)

> 🚀 **基于DeepSeek AI的智能加密货币交易机器人，支持动态仓位管理和全自动交易决策**

## 📖 文档语言 / Documentation Language

<div align="center">

[![English](https://img.shields.io/badge/English-🇺🇸-blue.svg)](README_EN.md)
[![中文](https://img.shields.io/badge/中文-🇨🇳-red.svg)](README_CN.md)

</div>

## ⚠️ **重要：必须使用单向持仓模式**
**请确保您的币安账户设置为单向持仓模式（One-Way Mode），双向持仓模式（Hedge Mode）会导致交易失败！**

## 💰 如果您通过这个项目获得了收益，欢迎支持一下：
## 💰 **钱包地址BEP20/BSC**
### `0x59B7c28c236E6017df28e7F376B84579872A4E33`

<img width="1124" height="877" alt="图片" src="https://github.com/user-attachments/assets/b014a85a-7791-4af1-a9dd-a6faf277c8ac" />

## 🚀 快速开始（最简单）

### 📝 1. 修改交易配置
在 `src/deepseekBNB.py` 中修改：
```python
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',        # 交易对
    'leverage': 3,                # 杠杆倍数
    'timeframe': '15m',           # K线周期
    'test_mode': False,           # 实盘/测试模式
    'position_management': {
        'max_position_percent': 80,  # 最大仓位百分比
        'min_position_percent': 5,   # 最小仓位百分比
        'force_reserve_percent': 20, # 强制预留资金
    }
}
```

### 🔑 2. 配置API密钥
创建 `.env` 文件，填入您的API密钥：
```env
# DeepSeek API 密钥
DEEPSEEK_API_KEY=your_deepseek_api_key

# Binance API 配置
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret

# OKX API 配置（可选）
OKX_API_KEY=your_okx_api_key
OKX_SECRET=your_okx_secret
OKX_PASSWORD=your_okx_password
```

### ▶️ 3. 运行
```bash
# 安装依赖
pip install -r requirements.txt

# 启动机器人
python src/deepseekBNB.py
```

**下载这2个文件基本上就能跑了！** 🎉

---

## 🔥 最新更新 (2025-10-25)

### ✨ **重大升级**
- 🎯 **AI仓位管理优化** - AI现在可以根据市场情况智能调整仓位百分比（0-80%）
- 🔧 **动态资金管理** - 系统自动计算保证金，AI无需关心币种数量
- 📊 **完整账户信息** - AI决策时可查看可用余额、保证金占用率、持仓盈亏
- 🛡️ **增强风控** - 精度处理、最小交易量检查、合理性验证

### 🐛 **重要BUG修复**
- ✅ **修复反向平仓逻辑错误** - 持多仓+SELL信号现在只平仓，不再错误开空仓
- ✅ **修复BNB精度问题** - 正确使用2位小数精度，避免 `Precision error`
- ✅ **修复加仓逻辑** - 明确AI提示词，避免意外重复开仓

### 📝 **详细说明**
<details>
<summary>点击查看详细更新内容</summary>

#### Bug #1: 反向平仓错误（严重）
**问题：** 之前版本在持有多仓时收到SELL信号，会先平掉多仓，然后再开空仓。这违背了AI的原意（可能只想平仓观望）。

**修复：**
- 持多仓 + SELL信号 → **只平多仓**（不开新仓）
- 持空仓 + BUY信号 → **只平空仓**（不开新仓）

**影响：** 避免意外的双向交易和额外手续费

#### Bug #2: BNB精度错误
**问题：** 代码使用3位小数精度 `round(amount, 3)`，但BNB只支持2位小数，导致订单失败。

**修复：**
- 计算精度：`round(amount, 3)` → `round(amount, 2)`
- 打印格式：`.3f` / `.4f` → `.2f`

**影响：** 避免 `APIError(code=-1111): Precision is over the maximum` 错误

</details>

---

## ✨ 核心特性

### 🧠 **AI驱动决策**
- **DeepSeek AI分析** - 基于先进大语言模型的智能市场分析
- **完全自主决策** - AI独立分析技术指标，无人工干预
- **动态仓位管理** - AI根据市场情况智能调整仓位大小

### 📊 **技术分析引擎**
- **多维度指标** - SMA、EMA、MACD、RSI、布林带、成交量分析
- **支撑阻力识别** - 自动计算静态和动态支撑阻力位
- **趋势分析** - 价格动量、趋势连续性分析
- **实时数据** - 15分钟K线数据，96根历史数据点

### 🛡️ **风险管理系统**
- **智能风控** - 最大80%仓位限制，强制20%资金预留
- **杠杆保护** - 固定3倍杠杆，风险可控
- **最小交易量** - 自动检查交易所最小交易要求
- **容错机制** - 交易数量精度处理和合理性验证

### 🔧 **技术架构**
- **币安合约** - 支持币安期货交易
- **多币种支持** - 可配置交易对（BNB/USDT、DOGE/USDT等）
- **持久化运行** - tmux会话管理，支持远程服务器部署
- **完整日志** - 自动日志轮转，详细交易记录

## 🚀 快速开始

### 📋 系统要求
- Python 3.11+
- Linux/macOS/Windows
- 币安账户（期货权限）
- DeepSeek API密钥

### ⚡ 一键安装
```bash
# 克隆项目
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot

# 运行安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 🔧 手动安装
```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp config/env.example .env
# 编辑 .env 文件，填入您的API密钥
```

## ⚙️ 配置说明

### 🔑 API密钥配置
在 `.env` 文件中配置：
```env
# DeepSeek AI API
DEEPSEEK_API_KEY=your_deepseek_api_key

# 币安API密钥
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret
```

### 📊 交易配置
在 `src/deepseekBNB.py` 中修改 `TRADE_CONFIG`：
```python
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',        # 交易对
    'leverage': 3,                # 杠杆倍数
    'timeframe': '15m',           # K线周期
    'test_mode': False,           # 实盘/测试模式
    'position_management': {
        'max_position_percent': 80,  # 最大仓位百分比
        'min_position_percent': 5,   # 最小仓位百分比
        'force_reserve_percent': 20, # 强制预留资金
    }
}
```

## 🎯 使用方法

### 🖥️ 本地运行
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动交易机器人
python src/deepseekBNB.py
```

### 🖥️ 远程服务器部署
```bash
# 使用tmux创建持久会话
tmux new -s trading-bot

# 在tmux中运行
source venv/bin/activate
python src/deepseekBNB.py

# 断开会话（程序继续运行）
# Ctrl+b 然后按 d

# 重新连接会话
tmux attach -t trading-bot
```

### 🚀 快速启动脚本
```bash
# 使用提供的启动脚本
chmod +x scripts/start_trading.sh
./scripts/start_trading.sh
```

## 📈 AI决策流程

### 🤖 AI接收信息
1. **K线数据** - 最近96根15分钟K线（24小时历史数据）
2. **技术指标** - SMA、RSI、MACD、布林带等
3. **账户信息** - 总权益、可用余额、保证金占用率
4. **持仓状态** - 当前持仓方向、数量、盈亏
5. **杠杆机制** - 3倍杠杆说明和计算方式

### 🎯 AI返回决策
```json
{
    "signal": "BUY|SELL|HOLD",
    "reason": "分析理由",
    "stop_loss": 具体价格,
    "take_profit": 具体价格,
    "confidence": "HIGH|MEDIUM|LOW",
    "position_percent": 0到100的整数
}
```

### 💰 仓位计算
- AI返回百分比 → 系统计算保证金
- 实际仓位 = 保证金 × 3倍杠杆
- 自动风控限制和精度处理

## 📊 技术指标详解

### 📈 移动平均线
- **SMA5/20/50** - 短期、中期、长期趋势
- **EMA12/26** - 指数移动平均线
- **价格位置关系** - 相对均线的百分比位置

### 🎯 动量指标
- **RSI** - 相对强弱指数（超买/超卖判断）
- **MACD** - 移动平均收敛发散
- **成交量比率** - 当前成交量与平均成交量比值

### 🎚️ 布林带分析
- **上轨/下轨** - 动态支撑阻力位
- **位置百分比** - 价格在布林带中的位置
- **波动性分析** - 市场波动程度

### 💰 支撑阻力
- **静态水平** - 基于历史高低点
- **动态水平** - 基于布林带
- **价格关系** - 距离关键水平的百分比

## 🛡️ 风险管理

### ⚠️ 重要提醒
- **子账户建议** - 强烈建议使用子账户限制风险
- **资金管理** - 只投入可承受损失的资金
- **API安全** - 妥善保管API密钥，设置适当权限
- **监控运行** - 定期检查机器人运行状态

### 🔒 风控机制
- **仓位限制** - 最大80%资金使用率
- **资金预留** - 强制20%缓冲资金
- **最小交易量** - 自动检查交易所要求
- **精度处理** - 交易数量自动精度调整

## 📁 项目结构

```
ai-trading-bot/
├── README.md                 # 项目说明
├── README_CN.md             # 中文详细文档
├── README_EN.md             # 英文详细文档
├── LICENSE                   # 开源许可证
├── requirements.txt         # Python依赖
├── .gitignore              # Git忽略文件
├── config/                  # 配置目录
│   ├── env.example        # 环境变量示例
│   └── trading_config.json # 交易配置示例
├── src/                     # 源代码
│   ├── deepseekBNB.py      # 主交易机器人
│   ├── indicators.py       # 技术指标模块
│   └── utils.py            # 工具函数
├── docs/                    # 文档
│   ├── installation.md     # 安装指南
│   ├── configuration.md    # 配置说明
│   └── trading_guide.md    # 交易指南
├── examples/               # 示例
│   └── basic_usage.py     # 基础使用示例
└── scripts/                # 脚本
    ├── setup.sh           # 安装脚本
    └── start_trading.sh   # 启动脚本
```

## 🤝 贡献指南

### 🐛 报告问题
- 使用GitHub Issues报告bug
- 提供详细的错误信息和日志
- 说明您的系统环境

### 💡 功能建议
- 欢迎提出新功能建议
- 详细描述使用场景
- 考虑实现的可行性

### 🔧 代码贡献
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 [Apache 2.0许可证](LICENSE) - 详见LICENSE文件

## ⚠️ 免责声明

**重要风险提示：**

- 🚨 **投资有风险** - 加密货币交易存在重大风险
- 💰 **资金损失** - 可能造成全部资金损失
- 🤖 **AI决策** - 机器人决策不保证盈利
- 🔒 **个人责任** - 使用本软件的所有风险由用户承担
- 📊 **测试建议** - 建议先用小资金测试
- 🛡️ **子账户** - 强烈建议使用子账户限制风险

**本软件仅供学习和研究使用，不构成投资建议。使用前请充分了解风险，谨慎投资。**

## 💰 支持与感谢

如果您通过这个项目获得了收益，欢迎支持一下：

## 💰 **钱包地址BEP20/BSC**
### `0x59B7c28c236E6017df28e7F376B84579872A4E33`

- 💝 **感谢支持** - 如果挣到钱的兄弟们愿意就念我个好
- 📖 **文档** - 查看docs/目录获取详细使用说明
- 🔧 **技术问题** - 请查看日志文件排查问题
- ⚠️ **风险提醒** - 投资有风险，请谨慎使用

---

**⭐ 如果这个项目对您有帮助，请给个Star支持一下！**
