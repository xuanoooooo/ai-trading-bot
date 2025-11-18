# 🚀 AI多币种投资组合管理系统

## 🎯 核心特性

- **AI投资组合经理**: 自主决策、动态调仓、多空灵活
- **提示词完全分离**: 代码只传递数据，策略完全在外部文件，修改策略无需改代码 ⭐NEW
- **自动止损保护**: 开仓即下止损单到交易所，AI可动态调整
- **客观信息反馈**: 记录止损触发历史，客观告知AI市场事件
- **四周期分析**: 5分钟(执行) + 15分钟(战术) + 1小时(策略) + 4小时(战略) + BTC大盘
- **完整统计**: 分币种+整体 + 持仓同步
- **可视化看板**: Web实时监控(Flask)，直接读取币安API数据
- **技术指标分析**: RSI、MACD、ATR、EMA、布林带等多维度指标

## 📈 已完成改进

### 📊 多周期K线数据传递 (v2.8.0) ⭐NEW

**核心改进**: 为AI提供完整的多周期K线原始数据，增强形态识别和趋势判断能力

**新增K线数据**：
- **5分钟周期**：最近13根K线（~1小时，执行层）
  - 用途：捕捉短期入场时机、识别即时形态
- **15分钟周期**：最近16根K线（4小时，战术层）
  - 用途：战术级别趋势判断、支撑阻力识别
- **1小时周期**：最近10根K线（~10小时，策略层）
  - 用途：中期趋势分析、关键价格位判断
- **4小时周期**：最近6根K线（24小时，战略层）
  - 用途：日级趋势方向、大周期形态识别

**技术指标（按周期精确列出，实际传给 AI 的字段）**：
- 5分钟（执行层）：
  - 仅原始 OHLCV（不计算指标，避免小周期噪音过拟合）
- 15分钟（战术层）：
  - `EMA20, EMA50`
  - `RSI(14)`
  - `MACD(12,26,9)`（含 DIF、DEA/Signal、Histogram）
  - `BollingerBands(20, 2)`（上轨/中轨/下轨）
- 1小时（策略层）：
  - `EMA20, EMA50`
  - `RSI(14)`
  - `MACD(12,26,9)`（含时间序列）
  - `ATR(14)`
  - `BollingerBands(20, 2)`
- 4小时（战略层）：
  - `EMA20, EMA50`
  - `ATR(14)`

**情绪与交易所数据**：
- 资金费率（Funding Rate）
- 持仓量/未平仓合约（Open Interest）
- 24h 涨跌、15m 涨跌

**K线数据格式**：
```
【15分钟K线】最近 16 根:
  K1: 🟢 O:3245.50 H:3250.00 L:3240.00 C:3248.00 (+0.08%) V:1234.5
  K2: 🔴 O:3248.00 H:3252.00 L:3242.00 C:3244.00 (-0.12%) V:1456.7
  ...
```

**优势**：
- ✅ AI可直接观察K线形态（吞没、十字星、锤子线等）
- ✅ 多周期K线配合技术指标，提供完整的市场视角
- ✅ 每个周期覆盖合理时间跨度，避免信息冗余
- ✅ K线数量经过优化，平衡信息量与Token成本

**代码位置**：
- `market_scanner.py`: 各周期K线数据获取（Line 157-296）
- `portfolio_manager.py`: K线格式化与传递（Line 234-254, 394-435）

---

### 🎯 提示词架构重大优化 (v2.7.0)

**核心理念**: System Message（不变的规则）vs User Message（变化的数据）

#### 硬编码提示词（System Message - 不可外部修改）

位置：`portfolio_manager.py:510-577`

**包含内容**：
1. **基础身份定位**
   - 专业加密货币投资组合经理

2. **返回格式要求**（JSON结构）
   - 字段定义：coin, action, reason, position_value, stop_loss, take_profit
   - 数据类型和格式规范
   - 示例 JSON 结构

3. **移动止损机制说明**（新增）
   - HOLD 时填入新 stop_loss 价格即可
   - 系统自动取消旧止损单 + 创建新止损单
   - AI 无需执行多个操作，只需提供新价格

4. **硬性规则（红线）**
   - 资金保护：必须保留 10% 总资产作为手续费和风险缓冲
   - 最大可用公式：`总资产 × 90% - 已用保证金`
   - 杠杆固定：5x 杠杆，由系统管理（通过 `config/coins_config.json` 的 `portfolio_rules.leverage` 配置）
   - 最小开仓金额：全局 13 USDT + 币种特定限制（动态读取配置文件）
   - 止损必填：所有开仓和持仓必须提供止损价格

**为什么硬编码这些**：
- ✅ 确保 AI 响应格式正确（JSON 解析不出错）
- ✅ 防止 AI 违反系统安全限制（资金保护）
- ✅ 技术机制说明（移动止损如何工作）
- ✅ 这些是系统层面的约束，不是交易策略

---

#### 外部可修改提示词（prompts/default.txt）

位置：`prompts/default.txt`（外部交易策略文件）

**包含内容**：
- 📋 交易身份与定位（日内交易者、多币种管理）
- 🎯 决策权限与理念（自主决策、观望也是决策）
- 📊 多周期分析框架（5m/15m/1h/4h 如何使用）
- 🎲 入场信号标准（做多/做空的具体条件）
- 💰 仓位管理建议（强中弱信号的仓位配置）
- ⏱️ 持仓时间与交易频率（日内为主、降低频率）
- 🛡️ 止损止盈管理策略（ATR 参考、追踪止盈）
- 📈 性能优化目标（夏普比率、学习改进）
- 🧠 决策独立性原则（保持客观、理性决策）

**如何修改策略**：
```bash
# 1. 编辑外部提示词文件
vim prompts/default.txt

# 2. 创建多个策略版本
cp prompts/default.txt prompts/aggressive.txt   # 激进策略
cp prompts/default.txt prompts/conservative.txt # 保守策略

# 3. 切换策略（修改代码中的文件路径）
vim src/core/portfolio_manager.py  # 修改文件路径
# 或者直接替换 default.txt 内容

# 4. 重启程序生效
pkill -f portfolio_manager.py
./scripts/start_portfolio.sh
```

---

#### 动态数据（User Message - 每次变化）

位置：`portfolio_manager.py:478-507`

**包含内容**：
- ⏰ 系统运行状态（启动时间、运行时长、调用次数）
- 💰 当前资金状况
  - 账户总资产（总余额）
  - 已用保证金（当前持仓占用）
  - 剩余可用余额（实时同步币安）
  - 保证金使用率（风险监控）
  - 当前杠杆（5x）
- 📊 市场数据
  - BTC 大盘数据（价格、指标、K线）
  - 各币种市场数据（技术指标、K线、资金费率）
  - 当前持仓情况（浮盈浮亏、止损止盈价格）
  - 历史统计（胜率、盈亏）
  - 最近决策记录

**优势**：
- ✅ AI 看到原始数据，完整透明
- ✅ 资金计算公式在 System Message，数据在 User Message
- ✅ 将来调整 10% 保留比例，只需修改 System Message

---

#### 资金计算逻辑修正（重要）

**旧逻辑（错误）**：
```python
可用保证金 = free_balance * 0.9
# 问题：持仓后 free_balance 减少，可用额度会不断缩水
```

**新逻辑（正确）**：
```python
最大可用 = 总资产 × 90% - 已用保证金

示例：
初始：total=100, used=0  → 可用 = 90-0  = 90
开仓50：total=100, used=50 → 可用 = 90-50 = 40
再开30：total=100, used=80 → 可用 = 90-80 = 10
亏损2U：total=98,  used=80 → 可用 = 88.2-80 = 8.2
```

**AI 看到的数据**：
```
- 账户总资产: 100.00 USDT
- 已用保证金: 50.00 USDT
- 剩余可用余额: 50.00 USDT
```

**AI 遵守的规则**（System Message）：
```
最大可用保证金 = 账户总资产 × 90% - 已用保证金
示例：总资产 100 USDT，已用 50 USDT → 最多还能用 40 USDT
```

---

#### 配置文件动态读取

**最小开仓金额**：从 `coins_config.json` 动态读取，自动插入 System Message
```python
# 代码自动生成（portfolio_manager.py:472-476）
coin_limits_text = "BTC 50 | ETH 24 | SOL 13 | BNB 13 | ..."

# 插入到 System Message（Line 571）
币种限制：{coin_limits_text}
```

**优势**：
- ✅ 修改配置文件，AI 立即看到新值
- ✅ 配置文件是唯一数据源
- ✅ 不需要手动同步两个地方

---

#### OpenAI 格式 API 配置（新增）

**灵活切换服务商**：
```bash
# .env 文件配置
OPENAI_API_KEY=[REDACTED_OPENAI_KEY]
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat

# 支持的服务商示例（修改上面三行即可切换）：
# DeepSeek:     https://api.deepseek.com          | deepseek-chat
# SiliconFlow:  https://api.siliconflow.cn/v1     | deepseek-ai/DeepSeek-V2.5
# Together AI:  https://api.together.xyz/v1       | meta-llama/Meta-Llama-3.1-70B-Instruct
# Groq:         https://api.groq.com/openai/v1    | llama-3.1-70b-versatile
# OpenAI:       https://api.openai.com/v1         | gpt-4o
```

**代码实现**（portfolio_manager.py:58-61, 578）：
```python
deepseek_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL')
)

# 调用时使用模型名称
model=os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
```

**优势**：
- ✅ 切换服务商只需修改 .env（API密钥、端点、模型名称）
- ✅ 无需修改代码
- ✅ 支持所有 OpenAI 兼容格式的 API

---

### 🎯 币安交易精度设置 ✅

**完全修复并优化，可放心使用**

**🔒 全局最小金额限制（硬编码）**：
- **13 USDT 统一底线**：任何币种开仓不得低于13美元 ⭐NEW
- 双重保护：全局限制 + 币种特定限制
- 代码位置：`portfolio_manager.py:574-579`
- 安全设计：即使币种配置被修改，也不会低于13美元

**数量精度（Precision）配置**：
- BTC: 3位小数 (0.001) ✅
- ETH: 3位小数 (0.001) ✅
- SOL: 1位小数 (0.1) ✅
- BNB: 2位小数 (0.01) ✅
- XRP/ADA/DOGE: 整数 (1) ✅

**最小下单金额（币种特定，高于全局13美元）**：
- BTC: 50 USDT
- ETH: 24 USDT
- SOL/BNB/XRP/ADA/DOGE: 13 USDT（统一为全局限制）

**价格精度（Price Precision）**：
- BTC/ETH/SOL/BNB: 2位小数（止损价格格式化）
- XRP/ADA/DOGE: 4位小数（低价币需更高精度）

**智能算法实现**：
- ✅ **全局13美元硬编码**：任何币种都不能低于此值（安全底线）⭐NEW
- ✅ 智能取整：自动选择floor/ceil，最小化误差
- ✅ 误差控制：实测误差≤15%
- ✅ 双重检查：先检查全局限制，再检查币种限制
- ✅ 配置位置：`config/coins_config.json`
- ✅ 计算函数：`portfolio_manager.py:571-611`

**测试验证结果**：
```
全局限制测试：
SOL $5    ❌ 被拒绝（< 13）  |  SOL $10   ❌ 被拒绝（< 13）
SOL $13   ✅ 通过            |  DOGE $8   ❌ 被拒绝（< 13）
DOGE $13  ✅ 通过            |  BNB $10   ❌ 被拒绝（< 13）

精度误差测试：
BTC:  误差 6.00%  ✅  |  ETH:  误差 0.80%  ✅
SOL:  误差 15.00% ✅  |  BNB:  误差 0.00%  ✅
XRP:  误差 2.40%  ✅  |  ADA:  误差 0.00%  ✅
DOGE: 误差 1.00%  ✅
```

## 📁 项目结构

```
duobizhong/
├── src/core/                      # ⭐NEW 核心交易逻辑
│   ├── portfolio_manager.py       # 投资组合管理主程序
│   ├── market_scanner.py          # 市场数据扫描器
│   └── portfolio_statistics.py    # 投资组合统计模块
├── web/                           # ⭐NEW Web可视化界面
│   ├── web_app.py                 # Flask后端应用
│   ├── templates/index.html       # 前端页面模板
│   ├── static/                    # CSS/JS资源
│   └── start_web.sh               # Web服务启动脚本
├── scripts/                       # ⭐NEW 脚本目录
│   ├── start_portfolio.sh         # 交易程序启动脚本
│   └── 清理历史记录.sh            # 历史记录清理脚本
├── data/                          # ⭐NEW 数据文件目录
│   ├── ai_decisions.json          # AI决策历史记录
│   ├── portfolio_stats.json      # 投资组合统计数据
│   └── current_runtime.json       # 当前运行状态
├── config/                        # 配置文件目录
│   └── coins_config.json          # 币种配置(精度、最小金额)
├── prompts/                       # 提示词目录
│   └── default.txt                # 默认交易策略（完全外置）
└── docs/                          # 文档目录
    └── ...
```

## 🚀 快速启动

### 交易程序

```bash
cd /root/ziyong/duobizhong
./scripts/start_portfolio.sh       # 启动
tmux attach -t portfolio           # 查看
pkill -f portfolio_manager.py      # 停止
```

### 可视化看板

```bash
cd /root/ziyong/duobizhong/web
./start_web.sh                    # 启动(后台运行)
pkill -f web_app.py              # 停止

# SSH隧道访问(本地安全)
ssh -L 5000:localhost:5000 user@server
```

## 🎯 核心特性

- **AI投资组合经理**: 自主决策、动态调仓、多空灵活
- **自动止损保护**: 开仓即下止损单到交易所，AI可动态调整
- **客观信息反馈**: 记录止损触发历史，客观告知AI市场事件
- **三周期分析**: 15分钟K线(短期) + 1小时K线(中期) + 4小时K线(长期趋势) + BTC大盘
- **完整统计**: 分币种+整体 + 持仓同步
- **可视化看板**: Web实时监控(Flask)，直接读取币安API数据

## 📁 项目结构

```
duobizhong/
├── src/core/                      # ⭐NEW 核心交易逻辑
│   ├── portfolio_manager.py       # 投资组合管理主程序
│   ├── market_scanner.py          # 市场数据扫描器
│   └── portfolio_statistics.py    # 投资组合统计模块
├── web/                           # ⭐NEW Web可视化界面
│   ├── web_app.py                 # Flask后端应用
│   ├── templates/index.html       # 前端页面模板
│   ├── static/                    # CSS/JS资源
│   └── start_web.sh               # Web服务启动脚本
├── scripts/                       # ⭐NEW 脚本目录
│   ├── start_portfolio.sh         # 交易程序启动脚本
│   └── 清理历史记录.sh            # 历史记录清理脚本
├── data/                          # ⭐NEW 数据文件目录
│   ├── ai_decisions.json          # AI决策历史记录
│   ├── portfolio_stats.json      # 投资组合统计数据
│   └── current_runtime.json       # 当前运行状态
├── config/                        # 配置文件目录
│   └── coins_config.json          # 币种配置(精度、最小金额)
├── prompts/                       # 提示词目录
│   └── default.txt                # 默认交易策略（完全外置）
└── docs/                          # 文档目录
    └── ...
```

## 🚀 快速启动

### 交易程序

```bash
cd /root/ziyong/duobizhong
./scripts/start_portfolio.sh       # 启动
tmux attach -t portfolio           # 查看
pkill -f portfolio_manager.py      # 停止
```

### 可视化看板

```bash
cd /root/ziyong/duobizhong/web
./start_web.sh                    # 启动(后台运行)
pkill -f web_app.py              # 停止

# SSH隧道访问(本地安全)
ssh -L 5000:localhost:5000 user@server
# 浏览器: http://localhost:5000
```

## 🎯 AI决策机制

### 系统信息（传递给AI）
```
╔════════════════════════════════════════════════════════════╗
║          📊 AI投资组合管理系统 - 第 120 次调用          ║
╚════════════════════════════════════════════════════════════╝

⚠️ 系统运行状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 程序启动时间: 2025-10-26 10:00:00
⏰ 当前时间: 2025-10-26 18:00:00
⏱️  本次已运行: 8.0小时 (480分钟)
🔄 本次调用次数: 120 次

📊 数据说明:
⚠️ 所有K线和技术指标数据按时间排列: 最旧 → 最新
⚠️ 指标趋势用箭头(→)连接，显示最近10个值的变化

📈 数据周期:
- 15分钟K线: 短期分析（最近16根 = 4小时，含时间序列）
- 1小时K线: 中期趋势（最近10根 = 10小时，含时间序列）
- 4小时K线: 长期趋势（轻量级，仅关键指标）
- 指标时间序列: 最近10个值（15分钟 = 2.5小时，1小时 = 10小时）

⏰ AI调用频率:
- 每10分钟调用一次AI进行决策
- 分析的仍然是15分钟K线数据（质量稳定，噪音少）
- 当前K线的数据是动态更新的（反映此时此刻的市场状态）
- 💡 调用间隔可灵活调整：1分钟（激进）→ 10分钟（平衡）→ 15分钟（稳健）
```

### AI身份定位
```
【交易身份】
- 管理类型：多币种投资组合（BNB/ETH/SOL/XRP/DOGE）
- K线数据：15分钟(短期) + 1小时(中期) + 4小时(长期)
- 调用频率：每10分钟
- 交易方向：做多做空同样积极，不偏好任何方向
- 交易风格：专业日内交易者

【核心目标】
通过专业技术分析，捕捉市场中的超额收益机会（alpha）。
```

### 输入数据（v2.6 优化版）⭐NEW
- **运行状态**: 启动时间、运行时长、调用次数（给AI时间尺度感）
- **统计**: 胜率、各币种表现、最近交易
- **止损触发记录**: 最近30分钟内的止损事件（币种、方向、止损价、持仓时长、盈亏）
- **BTC大盘**:
  - 价格、15m涨跌、资金费率、持仓量
  - 15分钟: RSI/MACD/ATR + 时间序列（最近10个值）
  - 1小时: RSI/MACD/ATR/SMA20/50 + 时间序列
  - 4小时: RSI/MACD/SMA20/50（轻量级，无时间序列）
- **组合状态**: 总资金、持仓、分币种盈亏(含浮盈浮亏、止损止盈价格)
- **各币种市场数据**:
  - 基础: 价格、24h/15m涨跌、资金费率、持仓量
  - **多周期K线数据** ⭐NEW:
    - 5分钟: 最近13根K线（~1小时，执行层）
    - 15分钟: 最近16根K线（4小时，战术层）
    - 1小时: 最近10根K线（~10小时，策略层）
    - 4小时: 最近6根K线（24小时，战略层）
  - **技术指标**:
    - 15分钟: RSI/MACD/ATR/EMA20/50/布林带
    - 1小时: RSI/MACD/ATR/EMA20/50/布林带
    - 4小时: RSI/MACD/EMA20/50/ATR

### AI权限
- ✅ 完全控制所有币种仓位
- ✅ 可开/平/加仓、多空切换
- ✅ 自主决定持仓数量和资金分配

### 交易理念（传递给AI）
- 您是投资组合的唯一决策者
- 根据技术指标、盈亏情况、市场趋势、BTC大盘自主判断
- 基于实际市场波动设定合理预期
- **不做硬编码规则**: 无固定止盈止损要求，让AI基于技术分析自主决策

### 硬性限制
- 单币种无上限 | 现金 ≥ 10%
- 最小金额: BNB 12 | ETH 24 | SOL/XRP/DOGE 6 USDC
- 止损必填: AI每次开仓/HOLD必须给出止损价格（开仓时自动下单到交易所）

### 可用操作
`OPEN_LONG` | `OPEN_SHORT` | `CLOSE` | `ADD` | `HOLD`

### 止损止盈机制 ⭐
- **止损（必须）**: AI给出价格 → 自动在币安下止损单 → 触发自动平仓 → AI知道被止损
- **止盈（建议）**: AI给出价格 → 仅记录 → AI每10分钟自己评估是否平仓
- **动态调整**: AI可在每次决策时修改止损价格（系统自动更新订单）

## 📊 核心设计

### 数据原则
- ✅ **只给客观数据**: 硬性限制+完整数据，不硬编码交易规则和趋势判断
- ✅ **三周期架构**: 15分钟(短期信号) + 1小时(中期趋势) + 4小时(长期方向) + BTC(大盘)
- ✅ **时间序列**: 给AI展示指标变化趋势（最近10个值），而非单个快照
- ✅ **市场情绪**: 资金费率（多空情绪）+ 持仓量（参与度）
- ✅ **波动率**: ATR指标帮助AI判断市场状态和设置合理止损
- ✅ **自动同步**: 启动时同步币安持仓，以币安为准

### 容错机制
- **智能舍入**: 自动选择floor/ceil使仓位接近目标
- **15%容差**: 允许实际仓位与目标有合理偏差
- **动态精度**: 从币安API查询各币种精度

## 🖥️ 可视化看板

### 功能
- 📊 账户总览: 资金、盈亏(已实现+浮盈浮亏)、胜率、交易数（直接读币安API）
- 🪙 当前持仓: 实时显示5个币种持仓+浮盈浮亏+止损止盈价格（含止损单状态✅）
- 📜 交易历史: 最近15笔交易记录
- 🤖 AI决策日志: 最近10条AI决策及理由
- 📈 盈亏曲线: 累计盈亏趋势图(仅在新交易时更新，避免闪烁)
- 💹 实时价格: 顶部滚动显示BTC/BNB/ETH/SOL/XRP/DOGE价格

### 技术栈
- **后端**: Flask(仅监听localhost，SSH隧道访问)
- **数据源**: 直接读取币安API（账户、持仓）+ 本地文件（止损止盈、交易历史）
- **前端**: Chart.js + 原生JS + 暗色终端主题
- **更新频率**: 10秒(持仓/统计/价格) | 有新交易时(曲线)

## 📝 常用命令

```bash
# 交易程序
tail -f portfolio_manager.log     # 查看日志
tmux attach -t portfolio           # 连接会话
pkill -f portfolio_manager.py      # 停止程序

# 看板
tail -f web/web_app.log       # 查看日志
pkill -f web_app.py                # 停止看板
```

---

### 🔄 清理历史记录（让AI从零开始）

**使用场景**：
- 想让AI从零开始学习（清空所有历史决策和统计）
- 测试新的交易策略（`prompts/default.txt`）
- 系统重置（删除所有运行记录）

**运行方法**：
```bash
cd /root/ziyong/duobizhong
./scripts/清理历史记录.sh
```

**脚本会做什么**：
1. ✅ 自动停止所有运行程序（portfolio_manager + web_app）
2. ✅ 自动备份现有记录到 `backups/backup_YYYYMMDD_HHMMSS/` 目录
   - `ai_decisions.json`（AI决策历史）
   - `portfolio_stats.json`（持仓和交易统计）
   - `current_runtime.json`（运行时状态）
   - `portfolio_manager.log`（程序日志）
3. ✅ 删除所有历史文件
4. ⚠️ 提醒确认币安账户无持仓（重要！）
5. 📋 询问是否立即启动程序

**交互示例**：
```bash
$ ./清理历史记录.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗑️  AI历史记录清理工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  此操作将删除以下文件：
   - ai_decisions.json       (AI决策历史)
   - portfolio_stats.json    (持仓和交易统计)
   - current_runtime.json    (运行时状态)
   - portfolio_manager.log   (程序日志)

📦 删除前会自动备份到 backups/ 目录

是否继续？[y/N] y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣  停止所有运行中的程序
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛑 停止交易程序...
✅ 交易程序已停止

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2️⃣  备份现有记录
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 备份目录: backups/backup_20251111_134530
   ✅ 已备份: ai_decisions.json
   ✅ 已备份: portfolio_stats.json
   ✅ 已备份: current_runtime.json
   ✅ 已备份: portfolio_manager.log

📦 已备份 4 个文件到: backups/backup_20251111_134530

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3️⃣  删除历史记录文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🗑️  已删除: ai_decisions.json
   🗑️  已删除: portfolio_stats.json
   🗑️  已删除: current_runtime.json
   🗑️  已删除: portfolio_manager.log

✅ 已删除 4 个历史记录文件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4️⃣  检查币安账户持仓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  重要提醒：
   请确认币安账户没有未平仓的持仓！
   如果有持仓，请先手动平仓或使用程序平仓。

💡 启动程序后，系统会自动同步币安持仓状态

确认币安账户已清空？[y/N] y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 清理完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 操作摘要：
   - 已停止所有运行程序
   - 已备份 4 个文件到: backups/backup_20251111_134530
   - 已删除 4 个历史记录文件
   - 系统已重置，AI将从零开始

🚀 下一步：
   启动程序: ./start_portfolio.sh
   查看日志: tmux attach -t portfolio

💾 备份位置: backups/backup_20251111_134530
   如需恢复数据，可从备份目录复制文件

是否立即启动交易程序？[y/N]
```

**注意事项**：
- ⚠️ **必须先清空币安持仓**，否则程序启动时会自动同步并继续管理这些持仓
- 💾 所有数据会自动备份到 `backups/` 目录，可以随时恢复
- 🔄 清理后夏普比率重置为0（默认"正常"风险等级）
- 📊 启动程序后AI会从零开始积累交易历史

**如何恢复备份**：
```bash
# 查看所有备份
ls -lh backups/

# 恢复某个备份
cp backups/backup_20251111_134530/* .
```

---

### 🔄 手动清空统计（不推荐）

如果只想清空统计而不想用脚本：
```bash
# 备份
cp portfolio_stats.json portfolio_stats_backup_$(date +%Y%m%d_%H%M%S).json

# 删除
rm data/portfolio_stats.json data/ai_decisions.json data/current_runtime.json
```

## 🐛 常见问题

### 持仓不同步
启动时自动同步，以币安为准。详见 `持仓同步说明.md`

### 看板显示"加载失败"
检查：1) Web服务是否运行 2) 重启: `pkill -f web_app.py && cd web && ./start_web.sh`

### 盈亏曲线闪烁
已优化：仅在新交易时更新，不再每5秒刷新

### 精度错误/数量计算异常
**✅ 已完全修复**，所有币种精度配置符合币安要求：
- 配置文件：`config/coins_config.json`
- 智能舍入：自动选择floor/ceil，最小化误差
- 误差控制：实测≤15%，大部分<6%
- 最小金额：BTC 50 | ETH 24 | BNB 12 | SOL/XRP/ADA/DOGE 6 USDT
- 详细说明：见上文"币安交易精度设置"章节

### 订单被拒绝（金额或精度错误）
1. 检查配置文件是否被修改：`cat config/coins_config.json`
2. 查看错误日志：`tail -50 portfolio_manager.log | grep "⚠️\|❌"`
3. 如果出现"数量为0"错误，可能是目标金额低于最小限制
4. 所有配置已验证，正常情况下不会出现此类错误

## 📝 重要文件说明

- `portfolio_stats.json`: 统计数据(含止损触发历史，保留7天)
- `ai_decisions.json`: AI决策日志(看板读取)
- `config/coins_config.json`: 币种配置(精度、最小金额、杠杆)
- `prompts/default.txt`: **外部交易策略文件** ⭐修改策略从这里开始
- `清理历史记录.sh`: **清理脚本** ⭐让AI从零开始，自动备份旧记录
- `持仓同步说明.md`: 同步机制详解
- `快速开始交易程序.md`: 启动/停止命令
- `web/快速开始看板.md`: 看板命令
- `web/SSH隧道使用说明.md`: 安全访问方法

### portfolio_stats.json 数据结构
```json
{
  "trade_history": [...],           // 交易历史
  "stop_loss_history": [            // 止损触发历史（新增）
    {
      "timestamp": "2025-10-29T14:49:09",
      "coin": "BNB",
      "side": "short",
      "entry_price": 1117.65,
      "stop_price": 1120.0,
      "pnl": -1.88,
      "duration_minutes": 3
    }
  ],
  "current_positions": {...}        // 当前持仓（含stop_order_id）
}
```

## 📦 服务器迁移指南

### 🎯 迁移前检查清单

**当前服务器操作**：
```bash
# 1. 停止所有运行程序
pkill -f portfolio_manager.py
pkill -f web_app.py

# 2. 备份重要数据（可选，如果想保留历史）
cd /root/ziyong/duobizhong
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  portfolio_stats.json \
  ai_decisions.json \
  current_runtime.json \
  portfolio_manager.log \
  .env

# 3. 打包整个项目
cd /root/ziyong
tar -czf duobizhong_migration.tar.gz duobizhong/

# 4. 下载到本地
# scp root@old-server:/root/ziyong/duobizhong_migration.tar.gz ./
```

---

### 🚀 新服务器部署步骤

#### 1️⃣ **系统环境准备**

**必须的系统工具**：
- `python3` & `python3-pip` - Python运行环境
- `tmux` - 终端复用器（必须，用于后台运行交易程序）
- `git` - 版本控制（可选）

```bash
# 更新系统（Ubuntu/Debian）
apt update && apt upgrade -y

# 安装必要工具（tmux 必须安装）
apt install -y python3 python3-pip tmux git

# 验证 tmux 安装
tmux -V

# 安装Python依赖（推荐全局安装，无需虚拟环境）
pip3 install python-binance openai python-dotenv schedule pandas flask flask-cors

# 验证Python依赖安装
python3 -c "import binance; import openai; import dotenv; print('✅ 依赖安装成功')"
```

#### 2️⃣ **上传并解压项目**
```bash
# 上传文件到新服务器
# scp duobizhong_migration.tar.gz root@new-server:/root/

# 解压项目
cd /root
mkdir -p DS
cd DS
tar -xzf ../duobizhong_migration.tar.gz

# 确认文件完整性
ls -lh duobizhong/
```

#### 3️⃣ **配置环境变量**
```bash
cd /path/to/duobizhong   # 进入你的项目根目录（将此路径替换为你本地或服务器上的实际路径）

# 创建或编辑根目录下的 .env 文件
vim .env
```

**必填配置**：
```bash
# 币安API（必须）
BINANCE_API_KEY=[REDACTED_BINANCE_KEY]
BINANCE_SECRET=[REDACTED_BINANCE_SECRET]

# OpenAI 格式 API（必须）
OPENAI_API_KEY=[REDACTED_OPENAI_KEY]
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat

# 其他支持的服务商（切换只需修改上面三行）：
# DeepSeek:     https://api.deepseek.com          | deepseek-chat
# SiliconFlow:  https://api.siliconflow.cn/v1     | deepseek-ai/DeepSeek-V2.5
# Together AI:  https://api.together.xyz/v1       | meta-llama/Meta-Llama-3.1-70B-Instruct
# Groq:         https://api.groq.com/openai/v1    | llama-3.1-70b-versatile
# OpenAI:       https://api.openai.com/v1         | gpt-4o
```

**验证配置**：
```bash
# 测试币安API连接
python3 << 'EOF'
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv('./.env')  # 从项目根目录加载 .env，避免在代码或文档中使用绝对路径
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET'))
ticker = client.futures_ticker(symbol='BTCUSDT')
print(f"✅ 币安API连接成功！BTC价格: ${float(ticker['lastPrice']):,.2f}")
EOF
```

#### 4️⃣ **启动脚本权限**
```bash
cd /root/ziyong/duobizhong
chmod +x scripts/start_portfolio.sh

cd web
chmod +x start_web.sh
```

#### 5️⃣ **决定是否清空历史记录**

**选项A：全新开始（推荐）**
```bash
cd /root/ziyong/duobizhong
rm -f data/ai_decisions.json data/portfolio_stats.json data/current_runtime.json
# 程序启动时会自动创建新文件
```

**选项B：保留历史数据**
```bash
# 保持解压后的文件不动即可
# 程序会继续累积统计
```

#### 6️⃣ **启动程序**
```bash
# 启动交易程序
cd /root/ziyong/duobizhong
./scripts/start_portfolio.sh

# 查看启动日志（前30行）
tmux attach -t portfolio

# 启动Web看板（可选）
cd /root/ziyong/duobizhong/web
./start_web.sh
```

---

### 🔍 **验证部署成功**

```bash
# 1. 检查交易程序是否运行
ps aux | grep portfolio_manager.py

# 2. 检查日志是否正常
tail -20 /root/ziyong/duobizhong/portfolio_manager.log

# 3. 检查是否能获取市场数据
grep "扫描市场数据" /root/ziyong/duobizhong/portfolio_manager.log

# 4. 检查AI是否正常调用
grep "AI决策" /root/ziyong/duobizhong/portfolio_manager.log

# 5. 检查数据文件是否正确创建
ls -la /root/ziyong/duobizhong/data/
```

---

### ⚙️ **关键配置文件位置**

| 文件 | 路径 | 作用 | 是否需要备份 |
|------|------|------|-------------|
| `.env` | `/root/ziyong/duobizhong/.env` | API密钥配置（OpenAI + 币安） | ✅ **必须** |
| `coins_config.json` | `/root/ziyong/duobizhong/config/` | 币种精度、最小金额、杠杆配置 | ✅ 推荐 |
| `default.txt` | `/root/ziyong/duobizhong/prompts/` | 交易策略（外部提示词） | ✅ **必须** |
| `portfolio_stats.json` | `/root/ziyong/duobizhong/data/` | 历史统计数据 | 📊 可选 |
| `ai_decisions.json` | `/root/ziyong/duobizhong/data/` | AI决策日志 | 📊 可选 |
| `portfolio_manager.py` | `/root/ziyong/duobizhong/src/core/` | 主程序 | ✅ **必须** |
| `market_scanner.py` | `/root/ziyong/duobizhong/src/core/` | 市场数据模块 | ✅ **必须** |
| `web_app.py` | `/root/ziyong/duobizhong/web/` | 可视化看板 | ✅ **必须** |

---

### 📝 **配置文件详解**

#### `coins_config.json` - 币种交易参数
```json
{
  "coins": [
    {
      "symbol": "BTC",
      "binance_symbol": "BTCUSDT",
      "precision": 3,           // 数量小数位（0.001 BTC）
      "price_precision": 2,      // 止损价格小数位（45000.00）
      "min_order_value": 50      // 最小开仓金额（USDT）
    }
  ],
  "portfolio_rules": {
    "leverage": 5,                    // 杠杆倍数（所有币种统一）
    "min_cash_reserve_percent": 10    // 资金保留比例（提示词规则）
  }
}
```

**参数说明**：
- `precision`: 下单数量的小数位数，必须符合币安要求
- `price_precision`: 止损价格的小数位数
- `min_order_value`: 币种最小开仓金额（动态读取到 AI 提示词）
- `leverage`: 所有币种统一杠杆（启动时设置）
- `min_cash_reserve_percent`: 保留比例（仅用于显示，实际规则在提示词）

**修改注意**：
- 修改后重启程序生效
- `min_order_value` 会自动同步到 AI 提示词
- 杠杆修改需重启，有持仓时可能报错

---

### 🧠 **AI助手快速上手指南**

当你协助新服务器部署时，关键信息：

1. **项目架构**：
   - 主程序：`portfolio_manager.py`（3分钟调用一次AI，可灵活调整）
   - 数据模块：`market_scanner.py`（获取K线+技术指标）
   - 统计模块：`portfolio_statistics.py`（跟踪盈亏）
   - Web看板：`web/web_app.py`（Flask可视化）

2. **系统依赖**（必须）：
   ```bash
   # tmux - 终端复用器（必须，用于后台运行）
   apt install -y tmux
   
   # Python依赖库（无需虚拟环境）
   pip3 install python-binance openai python-dotenv schedule pandas flask flask-cors
   ```

3. **必须配置**：
   - `.env` 文件中的 `BINANCE_API_KEY`、`BINANCE_SECRET`
   - OpenAI 兼容 API：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL_NAME`
   - 确保 `.env` 路径是 `/root/ziyong/duobizhong/.env`
   - 支持所有 OpenAI 兼容格式的 API 服务商（DeepSeek/SiliconFlow/Groq等）

4. **核心设计**：
   - 调用频率：每5分钟（可修改 `check_interval_minutes`）
   - 四周期分析：5分钟(执行) + 15分钟(战术) + 1小时(策略) + 4小时(战略)
   - AI完全自主决策，策略在外部文件配置（`prompts/default.txt`）
   - 使用币安原生库 `python-binance`（非CCXT）
   - 5倍杠杆，管理7个币种：BTC/ETH/SOL/BNB/XRP/ADA/DOGE（杠杆通过配置文件调整）
   - 提示词完全分离：修改策略无需改代码

5. **常见问题排查**：
   - API连接失败 → 检查 `.env` 配置和网络
   - 持仓不同步 → 启动时自动同步，以币安为准
   - 看板无数据 → 检查 `web_app.py` 是否运行

6. **快速测试**：
   ```bash
   # 测试币安API
   python3 -c "from binance.client import Client; import os; from dotenv import load_dotenv; load_dotenv('/root/ziyong/duobizhong/.env'); c = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET')); print(c.futures_ticker(symbol='BTCUSDT')['lastPrice'])"
   ```

---

### 📞 **SSH隧道访问看板**

如果需要从本地浏览器访问Web看板：
```bash
# 本地电脑执行
ssh -L 5000:localhost:5000 root@new-server-ip

# 浏览器访问
http://localhost:5000
```

---

### 🛠️ 路径配置错误修复 (v2.9.0) ⭐NEW

**问题发现**：项目中存在硬编码路径错误，导致文件访问失败

**修复内容**：

#### 🔧 核心模块路径标准化

**1. 项目根目录统一配置**
```python
# 在 portfolio_manager.py 和 market_scanner.py 中添加
import os
PROJECT_ROOT = '/root/ziyong/duobizhong'
```

**2. 文件路径统一使用 os.path.join()**
```python
# 修复前（硬编码错误路径）
stats_file = '/root/DS/duobizhong/data/portfolio_stats.json'

# 修复后（标准路径）
stats_file = os.path.join(PROJECT_ROOT, 'data', 'portfolio_stats.json')
```

**3. 外部提示词文件路径修正**
- 修复：`/root/DS/duobizhong/prompts/default.txt` → `/root/ziyong/duobizhong/prompts/default.txt`
- 确保AI提示词加载正常

#### 📁 数据文件目录标准化

**目录结构调整**：
- 将JSON数据文件从项目根目录移动到 `data/` 目录
- 符合项目架构规范：`src/`、`config/`、`data/`、`prompts/` 分离

**修复的文件路径**：
1. `portfolio_stats.json` → `data/portfolio_stats.json`
2. `ai_decisions.json` → `data/ai_decisions.json`
3. `current_runtime.json` → `data/current_runtime.json`

#### 🔄 导入错误修复

**相对导入问题**：
```python
# 修复前（相对导入失败）
from .portfolio_statistics import PortfolioStatistics

# 修复后（绝对导入）
from portfolio_statistics import PortfolioStatistics
```

**优势**：
- ✅ 解决Python模块导入错误
- ✅ 统一项目路径管理
- ✅ 提高代码可移植性
- ✅ 符合Python项目最佳实践

#### 📋 修复的技术问题

1. **脚本执行权限**：为 `start_portfolio.sh` 添加执行权限
2. **Python导入系统**：解决相对导入无父包错误
3. **文件路径标准化**：消除硬编码路径依赖
4. **跨平台兼容性**：使用 `os.path.join()` 确保路径正确

**代码位置**：
- `portfolio_manager.py`: 第18行导入修复，第50行PROJECT_ROOT定义
- `market_scanner.py`: 第9行导入修复，第12行PROJECT_ROOT定义
- 文件路径统一使用 `os.path.join(PROJECT_ROOT, ...)`

---

## 🚨 风险提示

加密货币交易高风险，5倍杠杆放大盈亏。建议测试模式先行，持续监控。本项目仅供学习研究，风险自负。

---
