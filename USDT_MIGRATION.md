# USDC → USDT 迁移说明

## 修改内容

本次更新将所有交易对从 **USDC** 改为 **USDT**，以适应主流用户习惯和提高流动性。

---

## 修改的文件

### 1. 配置文件

**config/coins_config.json**
- ✅ 所有交易对从 `XXXUSDC` 改为 `XXXUSDT`
- ✅ 添加了 BTC 和 ADA
- ✅ 调整币种顺序：BTC → ETH → SOL → BNB → XRP → ADA → DOGE

---

### 2. 源代码文件

#### src/portfolio_manager.py
**修改内容：**
- ✅ 账户余额检查：`asset['asset'] == 'USDT'`（第182行）
- ✅ 所有显示金额的地方：`USDC` → `USDT`
  - 账户信息显示（第268-270行）
  - 持仓信息显示（第289行）
  - 未实现盈亏显示（第302行）
  - 止损触发显示（第320行）
  - 市场分析显示（第446-449行）
  - AI Prompt 说明（第577行）
  - 开仓金额显示（第789行）
  - 持仓盈亏显示（第817行）

#### src/market_scanner.py
**修改内容：**
- ✅ BTC数据获取：所有 `BTCUSDC` → `BTCUSDT`
  - 获取BTC价格（第331行）
  - 获取15分钟K线（第336行）
  - 获取1小时K线（第359行）
  - 获取4小时K线（第379行）
  - 获取资金费率（第399行）
  - 获取持仓量（第405行）
- ✅ **关键逻辑修改**：持仓解析（第478行）
  ```python
  coin = symbol.replace('USDT', '')  # 从 USDC 改为 USDT
  ```

#### src/portfolio_statistics.py
**修改内容：**
- ✅ 所有显示金额的地方：`USDC` → `USDT`
  - 交易记录（第240行）
  - 历史统计（第346, 348行）
  - 各币种表现（第357, 408行）
  - 最近交易（第373行）
  - 汇总信息（第400行）
  - 止损触发（第439行）

---

## 逻辑变更说明

### 关键修改点

#### 1. 账户余额检查
**旧代码：**
```python
if asset['asset'] == 'USDC':
    usdc_balance = float(asset['availableBalance'])
```

**新代码：**
```python
if asset['asset'] == 'USDT':
    usdt_balance = float(asset['availableBalance'])
```

#### 2. 持仓币种解析（最关键！）
**旧代码：**
```python
symbol = pos.get('symbol', '')
coin = symbol.replace('USDC', '')  # BTCUSDC → BTC
```

**新代码：**
```python
symbol = pos.get('symbol', '')
coin = symbol.replace('USDT', '')  # BTCUSDT → BTC
```

**为什么这是关键：**
- 如果交易对是 `BTCUSDT`，用 `replace('USDC', '')` 不会匹配
- 会返回完整的 `BTCUSDT`，导致币种识别错误
- 所有持仓、盈亏计算都会失败

#### 3. BTC市场数据获取
**旧代码：**
```python
btc_ticker = self.binance_client.futures_ticker(symbol='BTCUSDC')
btc_klines = self.binance_client.futures_klines(symbol='BTCUSDC', ...)
```

**新代码：**
```python
btc_ticker = self.binance_client.futures_ticker(symbol='BTCUSDT')
btc_klines = self.binance_client.futures_klines(symbol='BTCUSDT', ...)
```

**为什么重要：**
- BTC作为大盘参考，必须使用正确的交易对
- 否则所有大盘分析都会失败

---

## 用户升级步骤

### 如果你是从USDC版本升级：

1. **备份数据**（重要！）
   ```bash
   cp -r /root/DS/duobizhong /root/DS/duobizhong_backup_usdc
   ```

2. **更新配置文件**
   ```bash
   # 编辑 config/coins_config.json
   # 确保所有 binance_symbol 都是 USDT 结尾
   ```

3. **清空历史记录**（可选，但推荐）
   ```bash
   rm -f src/portfolio_stats.json
   rm -f src/ai_decisions.json
   rm -f src/current_runtime.json
   ```

4. **币安账户确认**
   - 确保你的币安账户已开通 USDT 合约交易
   - USDT 合约流动性更好，是主流选择

5. **重新启动程序**
   ```bash
   bash scripts/start_trading.sh
   bash scripts/start_dashboard.sh
   ```

---

## 常见问题

### Q1: 为什么改成USDT？
**A:** 
- USDT是主流稳定币，流动性最好
- 大部分用户习惯使用USDT
- USDT合约交易量远大于USDC

### Q2: 我的USDC持仓怎么办？
**A:**
- 建议先手动平掉所有USDC持仓
- 然后切换到USDT交易
- 或者在币安将USDC换成USDT

### Q3: 只修改配置文件可以吗？
**A:**
- **不可以！** 必须同时修改代码
- 特别是 `market_scanner.py` 第478行的 `replace('USDT', '')`
- 否则持仓识别会失败

### Q4: 旧的USDC版本还能用吗？
**A:**
- 可以，但不推荐
- 旧版本已备份到 GitHub `single-coin-version` 分支
- 新用户应该直接使用USDT版本

---

## 测试检查清单

升级后请检查：

- [ ] 程序能正常启动，无报错
- [ ] 能正确获取账户USDT余额
- [ ] 能正确获取BTC市场数据
- [ ] 能正确识别持仓币种（日志中显示 BTC、ETH 等，而不是 BTCUSDT）
- [ ] AI能正常分析并给出决策
- [ ] 开仓后能正确显示持仓和盈亏
- [ ] 看板能正确显示所有数据

---

## 回滚方法

如果升级后出现问题：

```bash
# 1. 停止程序
pkill -f portfolio_manager
pkill -f web_app

# 2. 恢复备份
rm -rf /root/DS/duobizhong
cp -r /root/DS/duobizhong_backup_usdc /root/DS/duobizhong

# 3. 重新启动
cd /root/DS/duobizhong
python portfolio_manager.py
```

---

## 总结

✅ **核心变更**：
1. 配置文件：交易对名称
2. 代码逻辑：币种解析、余额检查、BTC数据获取
3. 显示文本：所有金额单位

✅ **测试重点**：
- 持仓识别是否正确
- BTC大盘数据是否正常
- 账户余额是否正确

✅ **用户影响**：
- 新用户：无影响，直接使用
- 老用户：需要清空历史数据，重新开始

