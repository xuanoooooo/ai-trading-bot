# 🔧 Coin Configuration Guide - How to Change Trading Coin

## 📌 Overview

This project defaults to trading **BNB/USDT**. If you want to trade other coins (ETH, DOGE, SOL, etc.), you need to modify several places.

---

## 🎯 Files and Locations to Modify

### 1️⃣ **Main Configuration** `src/deepseekBNB.py`

#### Location 1: Trading Config (around line 92)

```python
# Trading configuration
TRADE_CONFIG = {
    'symbol': 'BNBUSDT',      # ← Change here: Trading pair
    'leverage': 3,             # ← Optional: Leverage
    'min_order_qty': 0.01,     # ← Must change: Min order quantity (see table below)
}
```

#### Location 2: Market Data Text (around line 517)

```python
market_text = f"""
【BNB/USDT Market Data】  # ← Change display name
```

#### Location 3: AI Prompt (around line 530)

```python
prompt = f"""
You are a professional day trader, responsible for BNB/USDT contract trading (3x leverage).  # ← Change coin name
```

---

## 📊 Common Coin Configuration Reference

| Coin | symbol | min_order_qty | Precision | Note |
|------|--------|---------------|-----------|------|
| BNB | BNBUSDT | 0.01 | 2 decimals | Binance Coin |
| ETH | ETHUSDT | 0.001 | 3 decimals | Ethereum |
| BTC | BTCUSDT | 0.001 | 3 decimals | Bitcoin |
| DOGE | DOGEUSDT | 10 | 0 decimals | Dogecoin |
| SOL | SOLUSDT | 0.1 | 1 decimal | Solana |
| XRP | XRPUSDT | 1 | 0 decimals | Ripple |

> ⚠️ **Important**: `min_order_qty` and precision must comply with Binance exchange rules!

---

## 🔍 How to Query Binance Exchange Rules

### Method 1: Binance Website
1. Login to [Binance Futures](https://www.binance.com/en/futures)
2. Search for your coin
3. Check trading rules (min quantity, price precision)

### Method 2: Query via API (Recommended)

Run this Python code:

```python
from binance.client import Client

client = Client(api_key='your_key', api_secret='your_secret')
info = client.futures_exchange_info()

# Find specific symbol
symbol = 'ETHUSDT'
for s in info['symbols']:
    if s['symbol'] == symbol:
        print(f"Symbol: {s['symbol']}")
        print(f"Precision: {s['quantityPrecision']}")
        for f in s['filters']:
            if f['filterType'] == 'LOT_SIZE':
                print(f"Min Qty: {f['minQty']}")
                print(f"Step Size: {f['stepSize']}")
```

---

## 📝 Complete Example: Change from BNB to ETH

### Step 1: Modify `src/deepseekBNB.py` line 92

```python
TRADE_CONFIG = {
    'symbol': 'ETHUSDT',      # BNB to ETH
    'leverage': 3,
    'min_order_qty': 0.001,   # ETH min 0.001
}
```

### Step 2: Modify Precision Handling (around line 661)

Find `calculate_position_size()` function:

```python
# 2. Precision handling: ETH uses 3 decimals
amount = round(raw_amount, 3)  # BNB is 2, ETH is 3

# 3. Min quantity check
min_safe_amount = 0.001  # ETH min 0.001 (BNB is 0.01)
```

### Step 3: Modify Display Text (lines 517 and 530)

```python
# Line 517
market_text = f"""
【ETH/USDT Market Data】  # Change to ETH

# Line 530
prompt = f"""
You are a professional day trader, responsible for ETH/USDT contract trading (3x leverage).  # Change to ETH
```

### Step 4: Modify Log Filename (optional, line 33)

```python
log_handler = RotatingFileHandler(
    'eth_trader.log',  # Change to eth_trader.log
    maxBytes=10*1024*1024,
    backupCount=3,
    encoding='utf-8'
)
```

### Step 5: Restart Program

```bash
# Stop current program
pkill -f deepseekBNB.py

# Start with new config
cd src && python deepseekBNB.py
```

---

## ⚠️ Common Errors and Solutions

### Error 1: `APIError(code=-1111): Precision is over the maximum`

**Cause**: Order quantity precision doesn't meet requirements

**Solution**: Check and modify `round(amount, X)`:
- BNB: 2 decimals
- ETH/BTC: 3 decimals
- DOGE/XRP: 0 decimals (integer)

### Error 2: `APIError(code=-1013): Filter failure: LOT_SIZE`

**Cause**: Order quantity is less than minimum

**Solution**: Increase `min_order_qty` or position percentage

### Error 3: `Symbol XXXUSDT not found`

**Cause**: Wrong symbol or Binance doesn't support this contract

**Solution**: 
1. Check spelling (must be uppercase, e.g., ETHUSDT)
2. Confirm Binance has this futures contract

---

## 🎯 Recommended Coin Selection Criteria

Good coins for AI trading:
- ✅ **High liquidity** - Large 24h trading volume
- ✅ **Moderate volatility** - Not too wild, not too flat
- ✅ **Major coins** - BTC, ETH, BNB, etc.
- ❌ **Avoid small caps** - Easy to manipulate, low liquidity

**Recommended for beginners**:
1. BNB - Moderate volatility, good liquidity (default)
2. ETH - Major coin, high volume
3. SOL - Emerging major, higher volatility

**Not recommended**:
- Coins ranked outside top 100 by market cap
- 24h trading volume < $10M
- Daily volatility > ±20%

---

## 📞 Need Help?

If you encounter issues after modification:
1. Check log file `bnb_trader.log` (or your renamed file)
2. Confirm your Binance account has futures trading enabled for that coin
3. Confirm the coin has perpetual futures on Binance

---

## 🔗 Related Resources

- [Binance Futures Trading Rules](https://www.binance.com/en/futures/trading-rules)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [python-binance Documentation](https://python-binance.readthedocs.io/)

---

**💡 Tip**: After changing coins, test with small amounts for a few days to observe AI performance before scaling up.

