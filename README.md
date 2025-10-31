# 🤖 AI多币种自动交易系统

<div align="center">

**让AI替你盯盘交易**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-purple.svg)](https://www.deepseek.com/)

### 📖 选择语言

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

## 💭 作者的话

> *"经历了生活的大亏损、在币圈也没获得什么结果，我对自己的水平彻底失望。*  
> *与其每天假装看盘实则在赌，不如把决策交给AI——至少它不会因为行情波动而梭哈。*  
> *这个项目源于一个简单的期望：AI再不完美也比我强。"*

---

## 💰 支持项目

<div align="center">

**如果这个项目对你有帮助，欢迎支持**

**钱包地址 (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

您的支持是持续更新的动力 ❤️

**没有收费也没有挂邀请码，只求各位给星星** ⭐

</div>

---

## ⚠️ 重要提醒

**市场有风险，投资需谨慎。**

本项目仅供学习交流使用。

**⚠️ 币安账户必须设置：**
- ✅ **单向持仓模式**（One-way Mode）
- ❌ 不支持双向持仓（Hedge Mode）
- 💡 设置路径：币安合约 → 偏好设置 → 持仓模式

---

## 🎯 项目亮点

### 🆚 单币种 VS 多币种

| 特性 | 单币种版本 | 多币种版本（本项目）|
|------|----------|-----------------|
| **管理方式** | 只交易1个币 | **同时管理5-8个币种** ✨ |
| **风险** | 集中风险 | **分散风险** 🛡️ |
| **机会** | 单一机会 | **多市场捕捉** 📈 |
| **收益** | 依赖单币 | **更稳定** 💪 |

---

## ✨ 核心功能

### 🧠 AI全自动决策
- DeepSeek AI智能分析
- 完全解放双手，24/7运行
- 自动开仓、平仓、止损止盈

### 📊 多币种管理
- 同时管理BTC、ETH、SOL等
- 智能资金分配
- 风险分散，不怕单币暴跌

### 🎨 实时看板
- Web界面直观展示
- 持仓、盈亏一目了然
- AI决策记录可查询

### 🛡️ 风险控制
- 单币种不超过20%
- 自动止损3%、止盈8%
- 最多持有5个币种

### 📈 技术分析
- RSI、MACD、EMA、布林带
- 1小时+4小时双周期验证
- AI有理有据做决策

---

## 🚀 快速开始

### 步骤1：克隆项目

```bash
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot
```

### 步骤2：安装依赖

```bash
bash scripts/install.sh
# 或者
pip install -r requirements.txt
```

### 步骤3：配置

```bash
cp .env.example .env
nano .env  # 填入API密钥
```

**获取密钥：**
- DeepSeek: https://platform.deepseek.com/
- Binance: https://www.binance.com/ (需要开通合约交易)

**⚠️ 币安账户设置（重要！）：**
- ✅ 必须使用 **单向持仓模式**（One-way Mode）
- ❌ 不支持双向持仓（Hedge Mode）
- 💡 设置路径：币安合约 → 偏好设置 → 持仓模式

**⚠️ 重要提示：**
- ✅ 默认使用 `deepseek-chat`（快速且便宜）
- ✅ 默认币种：BTC、ETH、SOL、BNB、XRP、ADA、DOGE（USDT交易对）
- ✅ 建议使用默认配置
- ❌ 不要使用单价低于$1的币种（如SHIB）

---

### 🔧 配置说明

**📁 配置文件位置：** `config/coins_config.json`

#### 1️⃣ 币种配置

**默认币种（7个）：** BTC, ETH, SOL, BNB, XRP, ADA, DOGE

**如何添加新币种（例如添加 MATIC）：**

**添加前（默认7个币种）：**
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

**添加 MATIC 后（8个币种）：**
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
    {"symbol": "MATIC", "binance_symbol": "MATICUSDT", "precision": 0, "price_precision": 4, "min_order_value": 6}  ⬅️ 新增
  ]
}
```

**参数说明：**
- `symbol`: 币种简称（显示用）
- `binance_symbol`: 币安交易对（必须是 **USDT** 结尾）
- `precision`: 数量小数位（访问币安合约页面查看订单簿）
- `price_precision`: 价格小数位
- `min_order_value`: 该币种最小开仓金额（USDT）

**⚠️ 选币规则：**
- ✅ 必须是 USDT 交易对
- ✅ 币种单价 ≥ $1（避免 SHIB、PEPE 等低价币）
- ✅ 24h 交易量 > 1亿美元
- 💡 推荐：AVAX, LINK, DOT, ATOM, LTC, UNI

---

#### 2️⃣ 风控参数配置

在 `config/coins_config.json` 的 `portfolio_rules` 部分：

```json
"portfolio_rules": {
  "leverage": 3,                    // 杠杆倍数（1-5倍，建议3倍）
  "min_cash_reserve_percent": 10,   // 最低保留资金百分比（10 表示保留10%）
  "max_single_coin_percent": 100    // 单币种最大仓位百分比（100 表示不限制）
}
```

**参数说明：**

**`leverage`**: 杠杆倍数
- 3 = 使用 3 倍杠杆
- 建议 2-3 倍（过高风险大）

**`min_cash_reserve_percent`**: 最低保留资金百分比
- 10 = 保留 10% 可用资金不用于开仓
- 例如：总资金 100 USDT，设为 10，则至少保留 10 USDT，最多用 90 USDT 开仓
- 建议：10-20（保留 10-20% 作为缓冲）

**`max_single_coin_percent`**: 单币种最大仓位百分比
- 100 = 允许单币种使用 100% 可用资金（不限制）
- 50 = 单币种最多用 50% 可用资金
- 30 = 单币种最多用 30% 可用资金
- AI会在此限制内自主分配

**💡 建议配置：**
- 保守型：`leverage: 2`, `min_cash_reserve_percent: 20`, `max_single_coin_percent: 30`
- 均衡型：`leverage: 3`, `min_cash_reserve_percent: 10`, `max_single_coin_percent: 50`
- 激进型：`leverage: 5`, `min_cash_reserve_percent: 10`, `max_single_coin_percent: 100`

---

#### 3️⃣ 其他重要参数

在 `src/portfolio_manager.py` 的 `PORTFOLIO_CONFIG` 部分：

```python
PORTFOLIO_CONFIG = {
    'leverage': 3,                    # 杠杆倍数（与 coins_config.json 中保持一致）
    'check_interval_minutes': 5,      # 扫描间隔（5分钟）
    'test_mode': False                # False=实盘模式，True=测试模式
}
```

**参数说明：**
- `leverage`: 杠杆倍数（建议与 `coins_config.json` 中的 `leverage` 保持一致）
- `check_interval_minutes`: AI分析间隔（5分钟，匹配5分钟K线周期）
- `test_mode`: 测试模式开关
  - `False`: 实盘模式，真实下单
  - `True`: 测试模式，只分析不下单（推荐新手先用测试模式）

**📖 更多配置详情：**
- [中文完整说明](README_CN.md#步骤4配置交易币种和ai模型)
- [English Guide](README_EN.md#4-configure-ai-model--trading-coins)

### 步骤4：启动交易

```bash
bash scripts/start_trading.sh
# 或者
cd src && python portfolio_manager.py
```

### 步骤5：启动看板（可选）

```bash
bash scripts/start_dashboard.sh
# 访问: http://localhost:5000
```

---

## 📸 系统界面预览

### 🎨 Web可视化看板

**实时监控持仓和AI决策**

![Web Dashboard](docs/images/看板截图.png)

**看板功能：**
- 💰 **左侧**：当前持仓，实时盈亏
- 🤖 **右侧**：AI决策日志，分析理由
- 🎨 **深色主题**：护眼舒适
- 🔄 **自动刷新**：每30秒更新
- 💚💔 **颜色标识**：绿色盈利，红色亏损

---

### 💻 终端日志模式

**详细执行日志，适合服务器监控**

![Terminal Logs](docs/images/日志截图.png)

**日志功能：**
- 📝 **详细日志**：每次AI分析和交易执行
- 🔍 **实时显示**：SSH远程实时监控
- 💡 **轻量级**：资源占用极低
- 📊 **完整信息**：市场数据、决策、结果

---

## 📊 工作原理

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

---

## 🗂️ 项目结构

```
ai-trading-bot/
├── src/                          # 核心代码
│   ├── portfolio_manager.py     # 主程序
│   ├── market_scanner.py        # 市场扫描
│   └── portfolio_statistics.py  # 统计
├── dashboard/                    # Web看板
│   ├── web_app.py               # Flask应用
│   ├── static/                  # 静态文件
│   └── templates/               # 模板
├── config/                       # 配置
│   └── coins_config.json        # 币种配置
├── scripts/                      # 脚本
│   ├── install.sh               # 安装
│   ├── start_trading.sh         # 启动交易
│   └── start_dashboard.sh       # 启动看板
├── .env.example                  # 环境模板
└── requirements.txt              # 依赖
```

---

## 📚 完整文档

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

## 🤝 贡献

欢迎贡献！

**开发计划：**
- [ ] 支持更多交易所（OKX、Bybit）
- [ ] Telegram通知
- [ ] 回测功能
- [ ] 移动端看板

---

## 💰 支持项目

<div align="center">

**如果这个项目对你有帮助，欢迎支持**

**钱包地址 (BEP20/BSC)**
```
0x59B7c28c236E6017df28e7F376B84579872A4E33
```

您的支持是持续更新的动力 ❤️

</div>

---

## 📄 许可证

Apache 2.0 许可证

---

## 📞 相关链接

- [🇨🇳 完整中文文档](README_CN.md)
- [🇺🇸 Full English Docs](README_EN.md)
- [📝 更新日志](CHANGELOG.md)
- [🐛 Issues](https://github.com/xuanoooooo/ai-trading-bot/issues)
- [🔀 Pull Requests](https://github.com/xuanoooooo/ai-trading-bot/pulls)

---

<div align="center">

**如果有帮助请给星！** ⭐

**没有收费，没有邀请码** 🌟

Made with ❤️ by AI Trading Community

</div>
