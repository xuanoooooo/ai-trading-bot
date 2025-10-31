# 🤖 AI多币种自动交易系统

<div align="center">

**让AI替你盯盘交易 | 24/7全自动运行 | 多币种投资组合管理**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-purple.svg)](https://www.deepseek.com/)

[🇨🇳 中文](README_CN.md) | [🇺🇸 English](README_EN.md)

</div>

---

## 💭 作者的话

> *"经历了生活的大亏损、在币圈也没获得什么结果，我对自己的水平彻底失望。*  
> *与其每天假装看盘实则在赌，不如把决策交给AI——至少它不会因为行情波动而梭哈。*  
> *这个项目源于一个简单的期望：AI再不完美也比我强。"*

### ⚠️ 重要提醒

**AI交易无法保证盈利，市场有风险，投资需谨慎。**  
本项目仅供学习交流，使用者需自行承担交易风险。  
请理性看待AI的决策能力，合理控制仓位，切勿盲目信任。

**没有收费也没有挂邀请码，只求各位给星星** ⭐

---

## 📖 项目简介

这是一个基于 **DeepSeek AI** 的全自动加密货币交易系统，支持 **多币种投资组合管理** 和 **实时可视化看板**。

**与单币种版本的区别**：
- ✅ **多币种管理** - 同时管理多个币种（BTC、ETH、SOL等）
- ✅ **智能分配** - AI自动分配资金，平衡投资组合
- ✅ **市场扫描** - 每小时扫描市场，寻找最佳交易机会
- ✅ **Web看板** - 实时查看所有持仓和收益情况

---

## 🎯 核心特性

### 🧠 **AI驱动决策**

- **DeepSeek AI分析** - 基于先进大语言模型的智能市场分析
- **完全自主决策** - AI独立分析技术指标，无人工干预
- **投资组合管理** - 考虑整体仓位，避免过度集中

### 📊 **技术分析引擎**

- **多维度指标** - RSI、MACD、EMA20/50、布林带、ATR波动率
- **多时段分析** - 1小时K线（中期）+ 4小时K线（长期），交叉验证
- **K线形态分析** - 16根历史K线 + 当前实时K线
- **时间序列数据** - 最近10个值的指标趋势（从旧→新）

### 🛡️ **风险管理系统**

- **智能仓位分配** - 每个币种默认20%资金，最多5个持仓
- **自动止损止盈** - 止损3%，止盈8%（可配置）
- **杠杆控制** - 默认3倍杠杆，可调整1-5倍
- **最大回撤保护** - 自动控制总风险

### 📈 **实时可视化看板**

- **Web界面** - Flask驱动的实时看板
- **持仓监控** - 查看所有持仓的盈亏情况
- **AI决策记录** - 查看每次决策的理由和信心度
- **收益曲线** - 可视化收益变化趋势
- **交易统计** - 胜率、总盈亏、交易次数等

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-trading-bot.git
cd ai-trading-bot
```

### 2. 安装依赖

```bash
# 运行安装脚本
bash scripts/install.sh

# 或手动安装
pip install -r requirements.txt
```

### 3. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
nano .env
```

**需要的API密钥：**
- **DeepSeek API Key**: 在 [DeepSeek平台](https://platform.deepseek.com/) 获取
- **Binance API Key**: 在 [币安](https://www.binance.com/) 账户设置中创建
  - ⚠️ 需要开通合约交易权限
  - ⚠️ API需要开启交易权限

### 4. 配置交易币种

编辑 `config/coins_config.json`：

```json
{
  "default_coins": ["BTC", "ETH", "SOL", "BNB"],
  "max_positions": 5,
  "position_size_pct": 20.0,
  "leverage": 3,
  "stop_loss_pct": 3.0,
  "take_profit_pct": 8.0
}
```

### 5. 启动交易程序

```bash
cd src
python portfolio_manager.py
```

**或使用脚本：**

```bash
bash scripts/start_trading.sh
```

### 6. 启动可视化看板（可选）

```bash
cd dashboard
python web_app.py
```

**或使用脚本：**

```bash
bash scripts/start_dashboard.sh
```

然后访问: **http://localhost:5000**

---

## 📊 系统架构

```
ai-trading-bot/
├── src/                          # 核心代码
│   ├── portfolio_manager.py      # 投资组合管理器（主程序）
│   ├── market_scanner.py         # 市场数据扫描器
│   └── portfolio_statistics.py   # 交易统计模块
├── dashboard/                    # Web可视化看板
│   ├── web_app.py               # Flask应用
│   ├── static/                  # 静态资源（CSS/JS）
│   └── templates/               # HTML模板
├── config/                       # 配置文件
│   └── coins_config.json        # 币种配置
├── scripts/                      # 启动脚本
│   ├── install.sh               # 安装脚本
│   ├── start_trading.sh         # 启动交易
│   └── start_dashboard.sh       # 启动看板
├── .env.example                 # 环境变量模板
├── requirements.txt             # Python依赖
├── LICENSE                      # Apache 2.0许可证
└── README.md                    # 项目说明
```

---

## 🧠 AI决策流程

### 工作流程：

1. **市场扫描**（每小时） → 扫描配置的币种，获取K线和技术指标
2. **AI分析** → DeepSeek分析市场数据和当前投资组合状态
3. **决策生成** → AI给出操作建议：
   - `OPEN_LONG` - 开多仓
   - `OPEN_SHORT` - 开空仓
   - `CLOSE` - 平仓
   - `HOLD` - 继续持有
   - `WAIT` - 观望
4. **风险检查** → 验证决策是否符合风险控制规则
5. **执行交易** → 通过币安API执行交易
6. **记录保存** → 保存决策过程和交易结果

---

## ⚠️ 风险提示

### 🚨 重要警告

**加密货币交易存在极高风险，请务必注意：**

| ⚠️ 风险类型 | 说明 |
|---------|------|
| **本金风险** | 可能导致本金全部亏损 |
| **杠杆风险** | 杠杆会放大盈亏，亏损可能超过本金 |
| **市场风险** | 市场剧烈波动可能导致快速亏损 |
| **技术风险** | 网络故障、API问题可能影响交易 |
| **AI决策风险** | AI不保证盈利，可能做出错误决策 |

### ✅ 安全建议

1. **小金额测试** - 从100-500 USDT开始
2. **设置止损** - 严格执行止损策略
3. **分散投资** - 不要把所有资金放在一个币种
4. **定期检查** - 每天至少检查一次账户
5. **风险承受能力** - 只投入你能承受损失的资金

---

## 💰 支持项目

如果这个项目对你有帮助，欢迎支持一下：

**钱包地址 (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

您的支持是我持续更新的动力 ❤️

---

## 📄 许可证

本项目采用 [Apache 2.0](LICENSE) 许可证

---

## ⚖️ 免责声明

本软件仅供学习和研究使用。使用本软件进行实盘交易的任何盈亏由用户自行承担。作者不对使用本软件造成的任何损失负责。

**加密货币交易具有高风险，请谨慎投资！**

---

<div align="center">

**⭐ 如果这个项目对你有帮助，欢迎Star支持！⭐**

**没有收费，没有邀请码，只求各位给个星星** 🌟

Made with ❤️ by AI Trading Community

</div>
