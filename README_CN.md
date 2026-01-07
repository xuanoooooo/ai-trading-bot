# 🚀 AI多币种投资组合管理系统

[English](README.md) | 简体中文

> ⚠️ **重要提示**：本项目通过 CCXT 库支持**多交易所**（Gate.io/Binance/OKX/Bybit）。请确保交易所账户设置为**单向持仓模式**。

## 💬 作者的话

"经历了生活的大亏损、在币圈也没获得什么结果，我对自己的水平彻底失望。与其每天假装看盘实则在赌，不如把决策交给 AI——至少它不会因为行情波动而梭哈。这个项目源于一个简单的期望：AI 再不完美也比我强。"

## 💰 支持项目

如果这个项目对你有帮助，欢迎支持。

**网络**：BEP20 / BSC
**钱包地址**：`0x59B7c28c236E6017df28e7F376B84579872A4E33`

---
20251126小更新：
-
1.增加最近3次的盈利情况（亏损情况）的连续传递，方便AI判断是否值得继续hold。
2.删除了仓位名义价值的百分比盈利率，仅使用保证金ROE，方便AI判断真实盈利。

## 📥 安装与部署

### 推荐目录结构

为了与项目中的路径配置保持一致，建议按照以下目录结构部署：

```bash
# 克隆项目
git clone https://github.com/xuanoooooo/ai-trading-bot.git duobizhong

# 或者手动创建目录
mkdir -p duobizhong
cd duobizhong
# 然后将项目文件放入此目录
```

**重要说明**：
- 项目内部的路径配置使用了 `duobizhong` 作为项目根目录名称
- 如果使用其他目录名，需要修改以下文件中的 `PROJECT_ROOT` 变量：
  - `src/core/portfolio_manager.py` (第50行)
  - `src/core/market_scanner.py` (第12行)
- README 中的示例命令（如 `/root/ziyong/duobizhong`）仅供参考，请根据实际路径调整

### 环境要求

- Python 3.7+
- tmux (必须安装，用于后台运行)
- 交易所账户（Gate.io/Binance/OKX/Bybit）
- OpenAI 兼容 API (DeepSeek/SiliconFlow/Groq/OpenAI 等)

### 快速开始

1. **安装依赖**
```bash
pip3 install ccxt openai python-dotenv schedule pandas flask flask-cors
```

2. **配置环境变量**
```bash
cp .env.example .env
vim .env  # 填入你的 API 密钥

# 在 config/coins_config.json 中配置交易所
vim config/coins_config.json  # 设置 "exchange": "gateio" 或 "binance"
```

3. **启动交易程序**
```bash
./scripts/start_portfolio.sh
```

详细部署说明请参考下方的"服务器迁移指南"章节。

## 🎯 核心特性

- **多交易所支持**: 通过 CCXT 支持 Gate.io/Binance/OKX/Bybit，配置文件切换 ⭐NEW
- **AI投资组合经理**: 自主决策、动态调仓、多空灵活
- **提示词完全分离**: 代码只传递数据，策略完全在外部文件，修改策略无需改代码
- **自动止损保护**: 开仓即下止损单到交易所，AI可动态调整
- **客观信息反馈**: 记录止损触发历史，客观告知AI市场事件
- **四周期分析**: 5分钟(执行) + 15分钟(战术) + 1小时(策略) + 4小时(战略) + BTC大盘
- **完整统计**: 分币种+整体 + 持仓同步
- **可视化看板**: Web实时监控(Flask)，直接读取交易所API数据
- **技术指标分析**: RSI、MACD、ATR、EMA、布林带等多维度指标

## 📈 核心架构设计

### 🎯 提示词架构优化 - 代码与策略完全分离 ⭐核心特性

**核心理念**: System Message（不变的规则）vs User Message（变化的数据）

这是项目最重要的架构设计，实现了**代码与策略的完全解耦**：
- **修改交易策略**：只需编辑外部文本文件 `prompts/default.txt`，无需改动任何代码
- **调整系统规则**：资金保护、止损机制等硬性约束保持在代码中，确保安全
- **灵活切换**：可创建多个策略文件（激进/保守/稳健），随时切换测试

#### 📋 三层提示词结构

**1️⃣ System Message - 系统硬性规则**（代码中，不可修改）

位置：`portfolio_manager.py:510-577`

**包含内容**：
- **JSON 格式规范**：确保 AI 返回可解析的标准 JSON 结构
- **移动止损机制**：HOLD 时填入新价格，系统自动更新止损单
- **硬性安全规则**：
  - 资金保护：必须保留 10% 总资产作为缓冲
  - 杠杆固定：5x 杠杆（通过配置文件 `coins_config.json` 管理）
  - 最小开仓：全局 13 USDT + 币种特定限制（动态读取配置）
  - 止损必填：所有开仓必须提供止损价格

**为什么硬编码**：✅ 保证系统安全 | ✅ 确保格式正确 | ✅ 防止违反交易所规则

---

**2️⃣ User Message - 外部交易策略**（可自由修改，无需改代码）

位置：`prompts/default.txt`

**包含内容**：
- 📋 交易身份与风格定位（日内/波段/长线）
- 🎯 决策权限与理念（自主决策、观望也是决策）
- 📊 多周期分析框架（如何使用 5m/15m/1h/4h 数据）
- 🎲 入场信号标准（做多/做空的具体技术条件）
- 💰 仓位管理策略（强/中/弱信号的仓位配置）
- ⏱️ 持仓时间与频率控制
- 🛡️ 止损止盈策略（ATR 参考、追踪止盈）
- 📈 性能目标（夏普比率、最大回撤）

**如何修改策略**：
```bash
# 1. 直接编辑策略文件
vim prompts/default.txt

# 2. 创建多个策略版本测试
cp prompts/default.txt prompts/aggressive.txt   # 激进策略
cp prompts/default.txt prompts/conservative.txt # 保守策略

# 3. 重启程序即可生效
pkill -f portfolio_manager.py && ./scripts/start_portfolio.sh
```

**优势**：✅ 零代码修改 | ✅ 快速测试策略 | ✅ 版本管理方便

---

**3️⃣ 动态市场数据**（每次调用实时更新）

位置：`portfolio_manager.py:478-507`

**包含内容**：
- ⏰ 系统状态：启动时间、运行时长、调用次数
- 💰 资金状况：总资产、已用保证金、可用余额、保证金使用率
- 📊 **多周期市场数据**（见下文详细说明）
- 🏦 当前持仓：浮盈浮亏、止损止盈价格
- 📈 历史统计：胜率、盈亏记录
- 📝 最近决策：AI 的历史决策及结果

**资金计算逻辑**（重要）：
```
最大可用保证金 = 总资产 × 90% - 已用保证金

示例：
- 初始：total=100, used=0  → 可用 = 90-0  = 90
- 开仓50：total=100, used=50 → 可用 = 90-50 = 40
- 再开30：total=100, used=80 → 可用 = 90-80 = 10
```

---

#### 📊 多周期K线与技术指标体系

为 AI 提供完整的多周期市场视角，支持从短期执行到长期战略的全方位分析：

**K线数据覆盖**：
- **5分钟** (13根, ~1小时)：执行层，捕捉短期入场时机
- **15分钟** (16根, 4小时)：战术层，判断短期趋势
- **1小时** (10根, ~10小时)：策略层，中期趋势分析
- **4小时** (6根, 24小时)：战略层，日级趋势方向

**技术指标配置**：
- **15分钟/1小时**：EMA20/50, RSI(14), MACD, ATR(14), 布林带
- **4小时**：EMA20/50, ATR(14)（轻量级，避免信息冗余）
- **市场情绪**：资金费率、持仓量、24h/15m涨跌幅

**数据格式示例**：
```
【15分钟K线】最近 16 根:
  K1: 🟢 O:3245.50 H:3250.00 L:3240.00 C:3248.00 (+0.08%) V:1234.5
  K2: 🔴 O:3248.00 H:3252.00 L:3242.00 C:3244.00 (-0.12%) V:1456.7
  ...
```

**优势**：✅ AI 可观察 K 线形态 | ✅ 多周期趋势共振 | ✅ 平衡信息量与成本

**代码位置**：
- `market_scanner.py:157-296` - 各周期数据获取
- `portfolio_manager.py:234-254, 394-435` - 数据格式化与传递

---

#### 🔧 配置文件动态读取 & OpenAI API 兼容

**最小开仓金额**：从 `coins_config.json` 动态读取，自动同步到 AI 提示词
```python
# 自动生成并插入 System Message
币种限制：BTC 50 | ETH 24 | SOL 13 | BNB 13 | ...
```

**灵活切换 AI 服务商**：
```bash
# .env 文件配置（支持所有 OpenAI 兼容 API）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat

# 支持的服务商示例：
# DeepSeek:     https://api.deepseek.com          | deepseek-chat
# SiliconFlow:  https://api.siliconflow.cn/v1     | deepseek-ai/DeepSeek-V2.5
# Groq:         https://api.groq.com/openai/v1    | llama-3.1-70b-versatile
# OpenAI:       https://api.openai.com/v1         | gpt-4o
```

**优势**：✅ 修改配置立即生效 | ✅ 唯一数据源 | ✅ 无需手动同步

---

### 🎯 币安交易精度设置 ✅

**精度配置**：
- **数量精度**：BTC/ETH 0.001 | SOL 0.1 | BNB 0.01 | XRP/ADA/DOGE 整数
- **价格精度**：BTC/ETH/SOL/BNB 2位 | XRP/ADA/DOGE 4位
- **最小金额**：全局 13 USDT | BTC 50 | ETH 24

**智能舍入算法**：
- ✅ 自动选择 floor/ceil，最小化误差（实测 ≤15%）
- ✅ 全局 13 USDT 硬编码保护（任何币种不得低于此值）
- ✅ 配置文件：`config/coins_config.json`

**测试验证**：全部币种精度符合币安要求，无订单拒绝问题

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

## 🖥️ 可视化看板

### 功能
- 📊 账户总览: 资金、盈亏(已实现+浮盈浮亏)、胜率、交易数
- 🪙 当前持仓: 实时显示币种持仓+浮盈浮亏+止损止盈价格
- 📜 交易历史: 最近15笔交易记录
- 🤖 AI决策日志: 最近10条AI决策及理由
- 📈 盈亏曲线: 累计盈亏趋势图
- 💹 实时价格: BTC/ETH/SOL/BNB/XRP/ADA/DOGE

### 技术栈
- **后端**: Flask (仅监听 localhost，SSH 隧道访问)
- **数据源**: 币安API（账户、持仓）+ 本地文件（交易历史）
- **前端**: Chart.js + 原生JS + 暗色主题
- **更新频率**: 10秒（持仓/统计/价格）| 有新交易时（曲线）

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

### 🔄 清理历史记录

**使用场景**：让 AI 从零开始学习 | 测试新策略 | 系统重置

**运行方法**：
```bash
cd /root/ziyong/duobizhong
./scripts/清理历史记录.sh
```

**功能**：
- ✅ 自动停止所有运行程序
- ✅ 备份到 `backups/backup_YYYYMMDD_HHMMSS/`
- ✅ 清空 AI 决策历史、统计数据、运行日志
- ⚠️ 提醒检查币安账户无持仓

**恢复备份**：
```bash
ls -lh backups/  # 查看所有备份
cp backups/backup_20251111_134530/* data/  # 恢复指定备份
```

---

## 🐛 常见问题

**持仓不同步**：启动时自动同步，以币安为准

**看板加载失败**：检查 Web 服务是否运行，重启：`pkill -f web_app.py && cd web && ./start_web.sh`

**精度/订单错误**：已完全修复，配置文件：`config/coins_config.json`

**数量为0错误**：目标金额低于最小限制（全局 13 USDT | BTC 50 | ETH 24）

## 📝 重要文件

- `config/coins_config.json` - 币种配置（精度、最小金额、杠杆）
- `prompts/default.txt` - **外部交易策略** ⭐修改策略从这里开始
- `data/portfolio_stats.json` - 统计数据（含止损触发历史）
- `data/ai_decisions.json` - AI 决策日志
- `scripts/清理历史记录.sh` - 清理脚本

## 📦 服务器迁移指南

### 系统环境准备

```bash
# 安装必要工具（Ubuntu/Debian）
apt update && apt install -y python3 python3-pip tmux git

# 安装Python依赖
pip3 install ccxt openai python-dotenv schedule pandas flask flask-cors
```

### 配置环境变量

```bash
cp .env.example .env
vim .env
```

**必填配置**：
- 交易所 API 密钥（选择其一）：
  - `GATEIO_API_KEY` / `GATEIO_SECRET` - Gate.io
  - `BINANCE_API_KEY` / `BINANCE_SECRET` - 币安
  - `OKX_API_KEY` / `OKX_SECRET` / `OKX_PASSWORD` - OKX
  - `BYBIT_API_KEY` / `BYBIT_SECRET` - Bybit
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL_NAME` - AI服务商
- 在 `config/coins_config.json` 中设置交易所：`"exchange": "gateio"` （或 binance/okx/bybit）

**支持的AI服务商**：DeepSeek | SiliconFlow | Groq | OpenAI（任何 OpenAI 兼容 API）

### 启动程序

```bash
chmod +x scripts/start_portfolio.sh web/start_web.sh
./scripts/start_portfolio.sh  # 启动交易程序
```

详细迁移步骤请参考项目 docs 目录。

## 🚨 风险提示

加密货币交易高风险，5倍杠杆放大盈亏。建议测试模式先行，持续监控。本项目仅供学习研究，风险自负。

---
