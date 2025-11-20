# 🎨 AI交易机器人可视化系统

基于Flask的Web监控界面，实时显示交易机器人的运行状态。

## ✨ 核心特性

- 🔝 **实时价格滚动条**: BTC、BNB、ETH、SOL、XRP、DOGE价格实时滚动
- 💰 **账户总览**: 总资金、可用资金、总盈亏、胜率、运行时长
- 🪙 **当前持仓**: 所有持仓币种、方向、浮盈浮亏
- 🤖 **AI决策日志**: 最近10条AI决策，包括理由和策略
- 📜 **交易历史**: 最近20笔交易记录
- 📈 **盈亏曲线**: 累计盈亏折线图

## 🏗️ 架构设计

```
交易程序 (portfolio_manager.py)  →  数据文件 (JSON)  →  Web服务 (web_app.py)  →  浏览器
   [独立运行]                        [共享数据]            [只读取]            [展示]
```

**完全隔离**：
- ✅ 交易程序独立运行，不受前端影响
- ✅ Web服务只读取数据，不执行交易
- ✅ 前端关闭，交易继续

## 🚀 快速开始

### 1. 启动交易程序（必须先启动）

```bash
cd /root/ziyong/duobizhong
./scripts/start_portfolio.sh
```

### 2. 启动Web服务

```bash
cd /root/ziyong/duobizhong/web
./start_web.sh
```

### 3. 访问界面（通过SSH隧道）

**在本地电脑执行**：
```bash
ssh -L 5000:localhost:5000 root@your-server-ip
```

**保持SSH连接，然后浏览器访问**：
```
http://localhost:5000
```

**为什么使用SSH隧道？**
- 🔒 更安全：Web服务只监听本地（127.0.0.1），外网无法访问
- 🔐 加密传输：所有数据通过SSH加密
- 🚫 防止攻击：不暴露端口到公网

## 📁 文件说明

```
web/
├── web_app.py              # Flask后端服务
├── templates/
│   └── index.html          # HTML模板
├── static/
│   ├── style.css           # 暗黑终端风格样式
│   └── app.js              # 前端逻辑（每5秒刷新）
├── start_web.sh            # Web服务启动脚本
└── README.md               # 本文件
```

## 🔌 API接口

Web服务提供以下API接口（仅供前端调用）：

| 接口 | 说明 |
|-----|------|
| `/api/stats` | 获取统计数据（胜率、总盈亏、运行时长） |
| `/api/account` | 获取账户信息（总资金、可用资金） |
| `/api/positions` | 获取当前持仓 |
| `/api/trades` | 获取交易历史 |
| `/api/prices` | 获取实时价格 |
| `/api/ai_decisions` | 获取AI决策日志 |

## 🎨 界面风格

- 🌑 暗黑主题（黑色背景 + 绿色文字）
- 🖥️ 终端风格字体（Courier New）
- 🔄 自动刷新（每5秒）
- 📱 响应式设计

## 🔧 管理命令

```bash
# 查看Web服务日志
tmux attach -t web

# 断开会话（服务继续运行）
Ctrl+B 然后按 D

# 停止Web服务
tmux kill-session -t web

# 或在会话内
Ctrl+C 然后 exit
```

## 📊 数据来源

1. **统计数据**: `../portfolio_stats.json`
2. **AI决策**: `../ai_decisions.json` 
3. **实时价格**: 币安公开API
4. **账户信息**: 币安API（只读）

## ⚠️ 注意事项

1. **安全性**：
   - Web服务只监听127.0.0.1（仅本地访问）
   - 只读取数据，无交易权限
   - 通过SSH隧道访问更安全

2. **隔离性**：前端崩溃不影响交易程序

3. **端口**：默认5000，如需修改可编辑web_app.py

4. **数据延迟**：最多5秒延迟（自动刷新间隔）

## 🛠️ 故障排查

### Web服务无法启动

```bash
# 检查端口是否被占用
netstat -tuln | grep 5000

# 查看详细错误
tmux attach -t web
```

### 数据不显示

- 确保交易程序正在运行
- 检查 `portfolio_stats.json` 文件是否存在
- 检查 `ai_decisions.json` 文件是否存在

### 实时价格不显示

- 检查网络连接
- 可能是币安API限流（等待恢复）

## 🔄 更新说明

**v1.0.0** (2025-10-25)
- 🚀 初始版本发布
- ✨ 完整的监控界面
- 🤖 AI决策日志展示
- 📊 盈亏曲线图

---

**重要提示**：此Web服务仅用于监控，不执行任何交易操作。所有交易由独立的 `portfolio_manager.py` 程序执行。

