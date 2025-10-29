# 🤖 AI自动交易机器人 - 单币种版本（多币种请运行多个实例）

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Trading](https://img.shields.io/badge/Trading-Cryptocurrency-orange.svg)](https://binance.com)

> 🚀 **基于DeepSeek AI的BNB智能交易机器人，使用币安原生库python-binance**

## 📦 项目定位

这是一个**单币种AI交易系统**（多币种请同时运行多个程序实例），特点：
- ✅ **单币种交易** - 默认BNB/USDT合约（代码示例），可自行修改为其他币种
- ✅ **多币种方案** - 需要多币种？同时运行多个程序实例即可，每个实例交易一个币种
- ✅ **币安原生库** - 使用python-binance库（非CCXT），性能更优
- ✅ **BTC大盘参考** - 保留比特币作为市场情绪参考

## 📖 语言选择 / Language Selection

<div align="center">

| [🇨🇳 中文文档](README_CN.md) | [🇺🇸 English](README_EN.md) |
|:---:|:---:|
| **简体中文** | **English** |

</div>

---

## ⚠️ **重要提示**

### 1. 必须使用单向持仓模式
**请确保您的币安账户设置为单向持仓模式（One-Way Mode），双向持仓模式（Hedge Mode）会导致交易失败！**

### 2. 网络访问说明
**⚠️ 美国IP和大陆IP无法访问币安API，请自行解决网络问题。本项目不会回复此类网络访问问题。**

---

## 💰 如果您通过这个项目获得了收益，欢迎支持一下

**钱包地址 (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/deepseek-trading-bot.git
cd deepseek-trading-bot

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥（创建.env文件）
cp config/env.example .env
# 编辑.env，填入你的API密钥

# 4. 启动交易（推荐使用脚本）
bash scripts/start_trading.sh

# 或直接运行
cd src && python deepseekBNB.py
```

---

## 🔥 最新更新

### 🚀 **v2.1.0 (2025-10-29) - 多时段分析重大升级**

> **⚡️ 这是一次重大功能升级！AI决策能力大幅提升！**

#### 📊 多时段技术分析（核心功能）

- ✨ **新增1小时周期数据** - 30根1小时K线（30小时历史）+ 最新10个指标趋势值
- 📈 **15分钟数据增强** - 16根15分钟K线（4小时历史）+ 最新10个指标趋势值 + 当前实时K线
- ⏰ **实时K线数据** - AI获取当前正在形成的K线（开盘价、当前价、最高/最低、成交量、已运行时间）
- 🎯 **多时段交叉验证** - 同时分析短期（15分钟）和中期（1小时），避免被短期波动误导
- 🧠 **AI智能对比** - 自动对比不同周期数据，识别真实趋势

**实际案例：**
```
AI决策理由：
"15分钟RSI 57.2处于中性区域，MACD从高位回落但仍为正值，
 1小时RSI 31.0显示超卖但价格未确认反弹，
 ATR显示波动率较低"
```
✅ AI能准确区分短期和中期信号，做出更理性的判断！

#### 🔧 同期优化

- 🔧 **移除AI硬性指导** - 删除"多头排列"/"震荡"等主观判断，100%客观数据
- 📊 **时间序列优化** - 明确标注所有数据"从旧→新"顺序
- 🔧 **修复.env加载路径** - 解决配置文件读取问题
- ✨ **启动脚本增强** - 支持系统Python3，无需虚拟环境
- ✅ **完整测试验证** - 多时段数据获取、AI分析质量全面测试通过

---

### ✨ **v2.0 (2025-10-27) - 核心特性**
- 📈 **16根K线数据** - 完整的4小时短期数据（16×15分钟）
- 🎯 **强制K线+指标分析** - AI必须同时分析K线形态和技术指标
- 📊 **当前K线实时数据** - AI可以看到正在形成的K线（开高低收、成交量、波动幅度）
- 🧠 **AI决策历史记忆** - AI能看到最近3次决策（45分钟历史），避免矛盾决策
- 💾 **交易历史本地保存** - 自动保存到trading_stats.json
- 📝 **AI决策日志** - 记录所有决策到ai_decisions.json
- 🔄 **Binance API重试机制** - 5次重试+30秒超时，自动处理临时网络问题
- 🌐 **BTC大盘参考** - 15分钟周期BTC数据作为市场情绪参考

---
---

## ✨ 核心特性

### 🧠 **AI驱动决策**
- **DeepSeek AI分析** - 基于先进大语言模型的智能市场分析
- **完全自主决策** - AI独立分析技术指标，无人工干预
- **连续决策记忆** - AI能看到最近3次决策，避免频繁反转

### 📊 **技术分析引擎**
- **多维度指标** - RSI、MACD、SMA20/50、布林带、ATR波动率
- **🚀 多时段分析** - 15分钟K线（短期）+ 1小时K线（中期），交叉验证避免误判
- **K线形态分析** - 16根历史K线（4小时历史数据） + 当前实时K线
- **时间序列数据** - 最近10个值的指标趋势（从旧→新，清晰展示趋势演变）
- **BTC大盘参考** - 比特币市场情绪作为辅助判断

### 🛡️ **风险管理系统**
- **固定杠杆** - 3倍杠杆，风险可控
- **资金管理** - 默认使用30%可用余额开仓
- **最小交易量** - 自动检查交易所最小交易要求（0.01 BNB）
- **网络重试** - API连接失败自动重试，提高稳定性

### 🔧 **技术架构**
- **币安原生库** - python-binance，性能优于CCXT
- **单币种专注** - 代码简洁，易于理解和二次开发
- **完整日志** - 自动轮转日志，最大10MB，保留3个备份
- **统计数据** - 实时胜率、盈亏、交易次数统计

---

## 📋 系统要求

- **Python**: 3.11+
- **操作系统**: Linux / macOS / Windows
- **API密钥**: 币安期货合约API（需要开通合约交易权限）

---

## 📁 项目结构

```
├── src/
│   ├── deepseekBNB.py              # 主交易程序
│   └── trading_statistics.py       # 交易统计模块
├── config/
│   ├── trading_config.json         # 交易配置文件
│   └── env.example                 # API密钥配置模板
├── scripts/
│   ├── start_trading.sh            # 启动脚本
│   └── setup.sh                    # 环境配置脚本
├── docs/
│   ├── 币种配置说明.md             # 如何修改交易币种（重要）
│   └── COIN_CONFIG.md              # Coin configuration guide (EN)
├── requirements.txt                # Python依赖
├── .env                            # API密钥（需自行创建）
└── README.md                       # 项目说明
```

---

## 🎯 AI交易决策流程

1. **数据获取** - 获取BNB市场数据和BTC大盘参考
2. **AI分析** - DeepSeek分析当前K线、历史K线、技术指标
3. **决策输出** - BUY_OPEN（开多）/ SELL_OPEN（开空）/ CLOSE（平仓）/ HOLD（观望）
4. **执行交易** - 根据决策执行相应操作
5. **记录保存** - 保存交易记录和AI决策日志

---

## ⚙️ 配置说明

### 交易配置 (`config/trading_config.json`)

```json
{
  "trading": {
    "symbol": "BNBUSDT",        // 交易对
    "leverage": 3,               // 杠杆倍数
    "min_order_qty": 0.01,       // 最小交易数量
    "test_mode": false           // 测试模式
  },
  "position_management": {
    "default_position_percent": 30,  // 默认仓位
    "max_position_percent": 50,      // 最大仓位
    "reserve_percent": 20            // 预留资金
  }
}
```

---

## 📊 数据文件说明

### `trading_stats.json` - 交易统计
- 总交易次数
- 胜率统计
- 总盈亏
- 最近200笔交易记录

### `ai_decisions.json` - AI决策日志
- 决策时间
- 操作类型
- 决策理由
- 信心程度

### `current_runtime.json` - 运行状态
- 程序启动时间
- AI调用次数
- 最后更新时间

---

## 🔍 监控和日志

```bash
# 查看实时日志
tail -f bnb_trader.log

# 查看AI决策
cat ai_decisions.json | jq '.decisions[-5:]'

# 查看交易统计
cat trading_stats.json | jq '.total_trades, .win_rate, .total_pnl'
```

---

## 🛡️ 风险提示

⚠️ **加密货币交易存在高风险，请谨慎使用：**

1. **资金风险** - 可能导致本金亏损
2. **杠杆风险** - 3倍杠杆会放大盈亏
3. **市场风险** - 市场波动可能导致快速亏损
4. **技术风险** - 网络问题或API故障可能影响交易
5. **AI决策风险** - AI决策不保证盈利

**建议：**
- ✅ 从小金额开始测试
- ✅ 定期检查账户和持仓
- ✅ 设置合理的止损策略
- ✅ 不要投入无法承受损失的资金

---

## 🐛 常见问题

### Q1: 如何修改交易币种（从BNB改为ETH/DOGE等）？
**A**: 详见 **[📖 币种配置说明文档](docs/币种配置说明.md)** 或 **[EN Version](docs/COIN_CONFIG.md)**

### Q2: API连接超时？
**A**: 检查网络连接，程序已内置5次重试机制。

### Q3: 如何切换到测试模式？
**A**: 修改`config/trading_config.json`中的`test_mode`为`true`。

---

## 📚 进阶使用

### 添加自定义指标
在`calculate_technical_indicators()`函数中添加新指标

### 调整AI提示词
修改`analyze_portfolio_with_ai()`中的`prompt`变量

### 多币种扩展
基于本项目架构扩展支持多币种交易

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

本项目采用 Apache 2.0 许可证

---

## ⚖️ 免责声明

本软件仅供学习和研究使用。使用本软件进行实盘交易的任何盈亏由用户自行承担。作者不对使用本软件造成的任何损失负责。

**加密货币交易具有高风险，请谨慎投资！**

---

## 💰 支持项目

如果您通过这个项目获得了收益，欢迎支持一下：

**钱包地址 (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

---

<div align="center">

**⭐ 如果这个项目对你有帮助，欢迎Star支持！⭐**

Made with ❤️ by AI Trading Community

</div>
