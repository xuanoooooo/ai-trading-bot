# 🎁 AI多币种交易机器人 - 一键开箱版

**📢 零基础用户专用版本，开箱即用！**

---

## 🚀 快速开始（只需2步）

### 第一步：获取API密钥

#### 1. DeepSeek API密钥（AI大脑）

- 访问：https://platform.deepseek.com/
- 注册并登录
- 点击"API Keys"获取密钥
- 复制保存（格式：`sk-xxxxxxxx`）

#### 2. Binance API密钥（交易执行）

- 访问：https://www.binance.com/
- 登录 → API管理 → 创建API密钥
- ⚠️ **必须开通**：
  - ✅ 合约交易权限
  - ✅ 允许交易权限
- ⚠️ **必须设置**：单向持仓模式
  - 路径：币安合约 → 偏好设置 → 持仓模式 → **单向持仓**

---

### 第二步：配置并启动

#### 1. 修改配置文件

找到上一级目录的 **`.env`** 文件（用记事本打开）

只需填入3个密钥：

```bash
DEEPSEEK_API_KEY=sk-xxxxx        # 填入DeepSeek密钥
BINANCE_API_KEY=xxxxx            # 填入币安API Key  
BINANCE_SECRET=xxxxx             # 填入币安Secret Key
```

保存并关闭。

#### 2. 启动程序

**Windows用户（双击运行）：**
- 双击 `start.bat` → 启动交易程序
- 双击 `start_dashboard.bat` → 启动看板（可选）

**Linux/Mac用户（终端运行）：**
```bash
cd ..
bash scripts/start_trading.sh        # 启动交易
bash scripts/start_dashboard.sh      # 启动看板（可选）
```

#### 3. 查看运行

浏览器访问：**http://localhost:5000**

---

## ✅ 已为您配置好（无需修改）

### 交易币种（7个主流币）
- BTC（比特币）
- ETH（以太坊）  
- SOL（Solana）
- BNB（币安币）
- XRP（瑞波币）
- ADA（艾达币）
- DOGE（狗狗币）

### 风控参数
- **杠杆**：3倍（稳健水平）
- **扫描**：每5分钟分析一次
- **AI模型**：deepseek-chat（快速便宜）
- **保留资金**：10%（降低风险）

**⚠️ 强烈建议使用默认配置，不要随意修改！**

---

## 💡 使用建议

### 最低资金要求
- 币安账户：最低100 USDT
- 建议初始：200-500 USDT
- 小资金测试，熟悉后再加

### 运行环境
- 🏠 **本地电脑**：关机程序停止
- ☁️ **云服务器**：推荐，24/7运行

### 首次使用
1. 确保币安账户有余额（100+ USDT）
2. 确保DeepSeek账户有余额
3. 观察1-3天，了解AI决策
4. 检查看板，查看盈亏

---

## 🛑 如何停止程序？

**Windows用户：**
- 双击 `stop.bat`

**Linux/Mac用户：**
```bash
cd .. && bash scripts/stop_trading.sh      # 停止交易
bash scripts/stop_dashboard.sh             # 停止看板
```

**或按键盘：**
- `Ctrl + C`（停止当前程序）

---

## 🆘 常见问题

**❓ 程序找不到文件？**
→ 确保 .bat 文件在一键开箱版文件夹内运行

**❓ API错误？**
→ 检查 `.env` 文件中的密钥是否正确（不要有空格）

**❓ 权限不足？**
→ 检查币安API是否开通"合约交易"权限

**❓ 保证金不足？**
→ 确保币安合约账户有足够USDT（建议100+）

**❓ 想修改币种？**
→ 一键开箱版不建议修改，如需高级配置请查看[完整文档](../README.md)

---

## 📖 需要更多帮助？

- 📚 [查看详细文档](../README.md)
- 🌐 [English Version](../README_EN.md)  
- 💬 [常见问题](https://github.com/xuanoooooo/ai-trading-bot/issues)

---

## ⚠️ 风险提醒

**市场有风险，投资需谨慎。**

本项目仅供学习交流使用，AI不能保证盈利。
请理性投资，控制仓位，不要超出自己的承受能力。

---

**祝交易顺利！** 🎉

