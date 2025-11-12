# 🤖 AI 多币种合约交易系统

> 基于 DeepSeek AI 的自主加密货币合约交易系统，支持 7 个主流币种的多空交易、动态调仓和风险管理。

## ⚡ 快速开始

### 1. 环境配置

#### 创建 `.env` 文件

```bash
# 币安 API（必需）
BINANCE_API_KEY=[REDACTED_BINANCE_KEY]
BINANCE_SECRET=[REDACTED_BINANCE_SECRET]

# AI 服务（必需，支持 OpenAI 兼容格式）
OPENAI_API_KEY=[REDACTED_OPENAI_KEY]
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat
```

#### 配置币种参数 `config/coins_config.json`

完整配置文件：

```json
{
  "coins": [
    {
      "symbol": "BTC",
      "binance_symbol": "BTCUSDT",
      "precision": 3,              // 数量精度（0.001 BTC）
      "price_precision": 2,        // 价格精度（止损价格）
      "min_order_value": 50        // 最小开仓金额（USDT）
    },
    {
      "symbol": "ETH",
      "binance_symbol": "ETHUSDT",
      "precision": 3,
      "price_precision": 2,
      "min_order_value": 24
    },
    {
      "symbol": "SOL",
      "binance_symbol": "SOLUSDT",
      "precision": 1,
      "price_precision": 2,
      "min_order_value": 13
    },
    {
      "symbol": "BNB",
      "binance_symbol": "BNBUSDT",
      "precision": 2,
      "price_precision": 2,
      "min_order_value": 13
    },
    {
      "symbol": "XRP",
      "binance_symbol": "XRPUSDT",
      "precision": 0,              // 整数（不支持小数）
      "price_precision": 4,        // 低价币需要更高精度
      "min_order_value": 13
    },
    {
      "symbol": "ADA",
      "binance_symbol": "ADAUSDT",
      "precision": 0,
      "price_precision": 4,
      "min_order_value": 13
    },
    {
      "symbol": "DOGE",
      "binance_symbol": "DOGEUSDT",
      "precision": 0,
      "price_precision": 4,
      "min_order_value": 13
    }
  ],
  "portfolio_rules": {
    "leverage": 5,                 // 杠杆倍数（全局设置）
    "min_cash_reserve_percent": 10 // 资金保留比例
  }
}
```

**参数说明**：
- `precision`: 下单数量的小数位数（币安要求）
- `price_precision`: 止损价格的小数位数
- `min_order_value`: 最小开仓金额（USDT），必须 ≥ 13
- `leverage`: 杠杆倍数，程序启动时自动设置到币安
- `min_cash_reserve_percent`: 强制保留的资金比例
- `check_interval_minutes`: AI 决策间隔（分钟），1=激进 5=平衡 10=稳健

> 💡 **提示**：所有配置参数都可以修改，详见 `config/配置说明.md`。修改后重启生效。

### 2. 启动交易

```bash
cd /root/DS/duobizhong
./start_portfolio.sh              # 启动交易程序
tmux attach -t portfolio          # 查看运行状态
```

### 3. 启动监控面板（可选）

```bash
cd keshihua
./start_web.sh                    # 启动 Web 看板

# 本地访问（SSH 隧道）
ssh -L 5000:localhost:5000 user@server
# 浏览器打开: http://localhost:5000
```

### 4. 停止程序

```bash
pkill -f portfolio_manager.py     # 停止交易
pkill -f web_app.py               # 停止看板
```

---

## 🎯 核心功能

### 交易能力
- **7 币种管理**：BTC、ETH、SOL、BNB、XRP、ADA、DOGE
- **多空灵活**：支持做多做空，AI 自主决策方向
- **动态调仓**：根据市场变化自动调整持仓
- **5x 杠杆**：固定杠杆，系统自动管理

### 风险控制
- **自动止损**：开仓即在交易所下止损单
- **动态调整**：AI 可随时移动止损价格（撤旧+重挂）
- **资金保护**：强制保留 10% 资金作为缓冲
- **止损记录**：记录并反馈给 AI，避免重复错误

### AI 决策
- **多周期分析**：5分钟（执行）+ 15分钟（战术）+ 1小时（策略）+ 4小时（战略）
- **完整数据**：K线 + 技术指标 + 市场情绪 + 持仓状态
- **策略外置**：交易策略在 `prompts/default.txt`，修改无需改代码
- **自主学习**：记录历史决策和统计数据，持续优化

### 可视化
- **实时监控**：账户、持仓、盈亏、价格
- **交易历史**：最近交易记录和 AI 决策日志
- **盈亏曲线**：累计盈亏趋势图
- **止损状态**：显示每个持仓的止损单状态

---

## 📊 AI 数据输入

### 多周期 K 线数据
| 周期 | K线数量 | 时间跨度 | 用途 |
|------|---------|---------|------|
| 5分钟 | 13根 | ~1小时 | 捕捉入场时机、识别短期形态 |
| 15分钟 | 16根 | 4小时 | 战术决策、支撑阻力判断 |
| 1小时 | 10根 | ~10小时 | 中期趋势、策略调整 |
| 4小时 | 6根 | 24小时 | 日级趋势、大方向判断 |

### 技术指标
- **趋势指标**：EMA(20)、EMA(50)、SMA(20)、SMA(50)
- **动量指标**：RSI(14)、MACD
- **波动指标**：ATR(14)、布林带
- **市场情绪**：资金费率、持仓量

### 其他数据
- 账户状态（总资产、可用余额、已用保证金）
- 当前持仓（浮盈浮亏、止损止盈价格）
- 历史统计（胜率、盈亏、各币种表现）
- 止损触发记录（最近30分钟）
- **最近 AI 决策记录**（最近 3 条）：时间、币种、操作、理由、信心度
- BTC 大盘数据（市场领导者）

---

## 🔧 交易策略配置

### `prompts/default.txt` - 交易策略

这是 AI 的交易策略文件，包含：
- 交易原则（风险管理、信号质量、持仓纪律）
- 入场标准（多空信号、确认条件）
- 仓位管理（强中弱信号的仓位配置）
- 止损止盈策略（ATR 参考、追踪止盈）

**修改策略**：
```bash
vim prompts/default.txt           # 直接编辑
./start_portfolio.sh              # 重启生效
```

---

## 📁 项目结构

```
duobizhong/
├── portfolio_manager.py          # 交易主程序（AI决策、下单、风控）
├── market_scanner.py             # 市场数据获取（K线、指标）
├── portfolio_statistics.py       # 统计模块（盈亏、胜率）
├── config/
│   └── coins_config.json         # 币种配置
├── prompts/
│   └── default.txt               # 交易策略（外部可修改）
├── keshihua/
│   ├── web_app.py                # Flask 看板后端
│   ├── templates/index.html      # 前端页面
│   └── start_web.sh              # 看板启动脚本
├── start_portfolio.sh            # 交易程序启动脚本
├── 清理历史记录.sh               # 重置 AI 历史数据
├── portfolio_stats.json          # 统计数据（自动生成）
├── ai_decisions.json             # AI 决策日志（自动生成）
└── .env                          # 环境变量（需手动创建）
```

---

## 🛠️ 常用操作

### 查看日志
```bash
tail -f portfolio_manager.log     # 实时日志
tail -f keshihua/web_app.log      # 看板日志
```

### 连接运行中的程序
```bash
tmux attach -t portfolio          # 连接交易程序
# 按 Ctrl+B 然后 D 断开连接（程序继续运行）
```

### 清理历史记录
```bash
./清理历史记录.sh                 # 自动备份并清空历史
# 用途：让 AI 从零开始、测试新策略、系统重置
```

### 切换 AI 服务商
修改 `.env` 文件的三行配置即可：
```bash
# DeepSeek
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat

# OpenAI
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o

# SiliconFlow
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL_NAME=deepseek-ai/DeepSeek-V2.5
```

---

## 🔐 安全设计

### 两层控制机制

系统采用**双层安全设计**，确保资金安全：

#### 1️⃣ 硬编码的提示词（AI 约束层）
这是告诉 AI 的"规则说明"，AI 需要遵守但**不会自动执行**：

**资金保护规则**：
- 必须保留至少 10% 的账户总资产作为手续费和风险缓冲
- 最大可用保证金 = 账户总资产 × 90% - 已用保证金
- 示例：总资产 100 USDT，已用 50 USDT → 最多还能用 40 USDT

**最小开仓金额**：
- 全局限制：任何币种不得低于 13 USDT（硬编码，不可突破）
- 币种限制：BTC 50 USDT、ETH 24 USDT、其他 13 USDT
- 实际生效：取两者中的较大值

**止损必填**：
- 所有开仓（OPEN_LONG/OPEN_SHORT）和持仓（HOLD）必须提供止损价格

**返回格式要求**：
- 必须返回符合规范的 JSON 格式
- 包含 decisions、strategy、risk_level、confidence 字段
- **语言要求**：所有文本字段必须使用简体中文，每个 reason 不超过 80 字

> ⚠️ **注意**：这些是 AI 的"道德约束"，AI 可以违反（虽然不应该），系统不会强制拦截。如果 AI 返回不合规的决策，可能导致执行失败。

#### 2️⃣ 硬编码的开仓逻辑（系统强制层）
这是系统**自动执行**的代码逻辑，无论 AI 说什么都会按这个流程走：

**开仓流程**（代码位置：`portfolio_manager.py:808-883`）：
1. 执行市价单开仓
2. 立即下止损单到交易所
3. 记录持仓信息

**多仓执行**：
- 开仓：`BUY` 市价单
- 止损：`SELL` 止损单（`STOP_MARKET` + `reduceOnly=True`）

**空仓执行**：
- 开仓：`SELL` 市价单
- 止损：`BUY` 止损单（`STOP_MARKET` + `reduceOnly=True`）

**精度处理**：
- 价格精度：`round(stop_loss, price_precision)`
- 数量精度：根据 `coins_config.json` 配置自动处理
- 智能舍入：自动选择 floor/ceil，最小化误差

> ✅ **保证**：这是强制执行的，AI 无法改变。即使 AI 决策有误，系统也会按照安全的方式执行。

### 止损机制
- **开仓即下单**：在交易所下真实止损单，非程序模拟
- **自动更新（移动止损）**：AI 在持仓状态下给出新的 `stop_loss` 时，系统会执行两步：
  1) 取消旧的止损单；2) 以新价格重新下 `STOP_MARKET` 止损单（`reduceOnly`）。
- **触发记录**：记录止损事件并反馈给 AI，避免重复错误

---

## 📈 系统架构

### 数据流
```
币安 API → market_scanner.py → portfolio_manager.py → AI 决策 → 执行交易
                                        ↓
                            portfolio_statistics.py（统计）
                                        ↓
                            portfolio_stats.json（持久化）
                                        ↓
                            keshihua/web_app.py（可视化）
```

### 提示词架构
- **System Message**（硬编码）：返回格式、硬性规则、技术机制
- **User Message**（动态数据）：市场数据、持仓状态、历史统计
- **外部策略**（`prompts/default.txt`）：交易理念、入场标准、仓位管理

### 调用频率
- **默认**：每 10 分钟调用一次 AI
- **可调整**：1分钟（激进）→ 10分钟（平衡）→ 15分钟（稳健）
- **数据实时**：每次调用都获取最新市场数据

---

## 🐛 常见问题

### Q: 持仓数据不同步？
A: 程序启动时会自动同步币安持仓，以币安为准。详见 `持仓同步说明.md`

### Q: 看板显示"加载失败"？
A: 检查 Web 服务是否运行：`ps aux | grep web_app.py`，重启：`pkill -f web_app.py && cd keshihua && ./start_web.sh`

### Q: 订单被拒绝（精度错误）？
A: 检查配置文件：`cat config/coins_config.json`，查看日志：`tail -50 portfolio_manager.log | grep "⚠️\|❌"`

### Q: 如何修改交易策略？
A: 编辑 `prompts/default.txt`，重启程序生效。可创建多个版本（如 `aggressive.txt`、`conservative.txt`）并切换。

### Q: 如何备份数据？
A: 重要文件：`.env`（API密钥）、`prompts/default.txt`（策略）、`config/coins_config.json`（配置）、`portfolio_stats.json`（历史数据）

---

## 📝 版本历史

### v2.8.0 (2025-11-12)
- ✨ 新增多周期 K 线数据传递（5m/15m/1h/4h）
- 🎯 增强 AI 形态识别和趋势判断能力

### v2.7.0
- 🔧 提示词架构优化（System/User Message 分离）
- 📝 策略完全外置到 `prompts/default.txt`

### v2.6.0
- 🛡️ 完善止损触发记录和反馈机制
- 📊 优化资金计算逻辑

### v2.5.0
- 🎨 新增 Web 可视化看板
- 📈 实时监控账户、持仓、盈亏

---

## 📚 相关文档

- `快速开始交易程序.md` - 详细启动步骤
- `持仓同步说明.md` - 同步机制详解
- `终端连接.md` - tmux 使用指南
- `keshihua/SSH隧道使用说明.md` - 安全访问看板

---

## ⚠️ 免责声明

本系统仅供学习和研究使用。加密货币交易存在高风险，可能导致本金损失。使用本系统进行实盘交易的一切后果由用户自行承担。

---

## 📧 技术支持

遇到问题？
1. 查看日志：`tail -f portfolio_manager.log`
2. 检查配置：`.env` 和 `config/coins_config.json`
3. 查阅相关文档（见上方"相关文档"）
