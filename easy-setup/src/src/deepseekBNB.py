#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Trading Bot - BNB单币种自动交易系统
基于币安原生库 python-binance

Author: AI Trading Bot
License: MIT
"""

import os
import time
import schedule
from openai import OpenAI
from datetime import datetime, timedelta
import json
import re
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import math

from trading_statistics import TradingStatistics

# 加载环境变量（从项目根目录）
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# 记录程序启动时间和调用次数
PROGRAM_START_TIME = datetime.now()
INVOCATION_COUNT = 0
RUNTIME_FILE = 'current_runtime.json'

# 配置日志
log_handler = RotatingFileHandler(
    'bnb_trader.log',
    maxBytes=10*1024*1024,
    backupCount=3,
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, console_handler]
)

# 语言设置（CN/EN）
LANG = os.getenv('BOT_LANG', 'CN').upper()

I18N = {
    'CN': {
        'connecting_binance': "🔗 正在连接Binance API...",
        'binance_init_ok': "✅ Binance客户端初始化成功",
        'binance_retry': "⚠️ Binance连接失败 (尝试 {attempt}/{max}): {err}",
        'wait_retry': "   等待 {sec} 秒后重试...",
        'binance_fail': "❌ 无法连接到Binance API，请检查网络连接",
        'init_fail': "❌ 初始化失败，程序退出",
        'bot_started': "BNB自动交易机器人启动成功！",
        'leverage': "杠杆",
        'period': "交易周期",
        'test_mode': "🧪 当前为测试模式",
        'live_mode': "🚨 实盘交易模式，请谨慎操作！",
        'schedule': "执行频率: 每15分钟一次",
        'run_time': "执行时间",
        'ai_raw': "AI原始回复",
        'ai_decision': "📊 AI交易决策",
        'action': "操作",
        'reason': "理由",
        'position_value': "开仓金额",
        'confidence': "信心程度",
        'risk_level': "风险等级",
        'hold': "💤 观望，不执行交易",
        'test_only': "🧪 测试模式，仅模拟",
        'buy_close_short': "📈 平空仓",
        'sell_close_long': "📉 平多仓",
        'buy_open': "📈 开多仓",
        'sell_open': "📉 开空仓",
        'qty_too_small': "⚠️ 开仓数量 {qty:.4f} BNB < 最小要求 {min_qty} BNB，跳过开仓",
        'trade_ok': "✅ 交易执行成功",
        'trade_fail': "❌ 交易执行失败: {err}",
    },
    'EN': {
        'connecting_binance': "🔗 Connecting to Binance API...",
        'binance_init_ok': "✅ Binance client initialized",
        'binance_retry': "⚠️ Binance connection failed (attempt {attempt}/{max}): {err}",
        'wait_retry': "   Retrying in {sec} seconds...",
        'binance_fail': "❌ Unable to connect to Binance API, please check your network",
        'init_fail': "❌ Initialization failed, exiting",
        'bot_started': "BNB Auto Trading Bot started!",
        'leverage': "Leverage",
        'period': "Trading interval",
        'test_mode': "🧪 Test mode enabled",
        'live_mode': "🚨 Live trading mode, proceed with caution!",
        'schedule': "Schedule: every 15 minutes",
        'run_time': "Run at",
        'ai_raw': "AI Raw Response",
        'ai_decision': "📊 AI Trading Decision",
        'action': "Action",
        'reason': "Reason",
        'position_value': "Position Value",
        'confidence': "Confidence",
        'risk_level': "Risk Level",
        'hold': "💤 HOLD, no trade executed",
        'test_only': "🧪 Test mode, simulation only",
        'buy_close_short': "📈 Close SHORT",
        'sell_close_long': "📉 Close LONG",
        'buy_open': "📈 Open LONG",
        'sell_open': "📉 Open SHORT",
        'qty_too_small': "⚠️ Quantity {qty:.4f} BNB < minimum {min_qty} BNB, skip",
        'trade_ok': "✅ Trade executed",
        'trade_fail': "❌ Trade failed: {err}",
    }
}

def tr(key: str) -> str:
    return I18N.get(LANG, I18N['CN']).get(key, key)

def print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    logging.info(message)

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 重试连接Binance
print(tr('connecting_binance'))
binance_client = None
max_retries = 5
retry_delay = 3

for attempt in range(max_retries):
    try:
        binance_client = Client(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_SECRET'),
            requests_params={'timeout': 30}
        )
        print(tr('binance_init_ok'))
        break
    except Exception as e:
        print(tr('binance_retry').format(attempt=attempt + 1, max=max_retries, err=str(e)[:100]))
        if attempt < max_retries - 1:
            print(tr('wait_retry').format(sec=retry_delay))
            time.sleep(retry_delay)
        else:
            print(tr('binance_fail'))
            exit(1)

if binance_client is None:
    print(tr('init_fail'))
    exit(1)

# 交易配置
TRADE_CONFIG = {
    'symbol': 'BNBUSDT',  # BNB/USDT合约
    'leverage': 3,  # 3倍杠杆
    'min_order_qty': 0.01,  # 最小交易数量
}

# 初始化交易统计
trading_stats = TradingStatistics('trading_stats.json')

# AI决策记录文件
AI_DECISIONS_FILE = 'ai_decisions.json'


def save_current_runtime():
    """保存当前运行状态"""
    try:
        runtime_data = {
            'program_start_time': PROGRAM_START_TIME.isoformat(),
            'invocation_count': INVOCATION_COUNT,
            'last_update': datetime.now().isoformat()
        }
        with open(RUNTIME_FILE, 'w', encoding='utf-8') as f:
            json.dump(runtime_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存运行时状态失败: {e}")


def save_ai_decision(coin, action, reason, confidence, position_value=0, risk_level='MEDIUM'):
    """保存AI决策到文件"""
    try:
        if os.path.exists(AI_DECISIONS_FILE):
            with open(AI_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {'decisions': []}
        
        decision = {
            'time': datetime.now().isoformat(),
            'coin': coin,
            'action': action,
            'reason': reason,
            'confidence': confidence,
            'position_value': position_value,
            'risk_level': risk_level
        }
        data['decisions'].append(decision)
        
        # 只保留最近100条
        data['decisions'] = data['decisions'][-100:]
        
        with open(AI_DECISIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存AI决策失败: {e}")


def calculate_technical_indicators(df):
    """计算技术指标"""
    try:
        # 移动平均线
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()

        # MACD
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # 布林带
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # ATR
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr_14'] = df['true_range'].rolling(14).mean()

        df = df.bfill().ffill()
        return df
    except Exception as e:
        print(f"技术指标计算失败: {e}")
        return df


def get_btc_market_reference():
    """获取BTC大盘参考数据（15分钟周期）"""
    try:
        # 获取BTC 15分钟K线
        klines = binance_client.futures_klines(
            symbol='BTCUSDT',
            interval='15m',
            limit=50
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = calculate_technical_indicators(df)

        current = df.iloc[-1]
        
        # 计算趋势强度
        sma20 = current['sma_20']
        sma50 = current['sma_50']
        price = current['close']
        
        if price > sma20 and sma20 > sma50:
            trend = "多头"
            strength = ((price - sma50) / sma50 * 100)
        elif price < sma20 and sma20 < sma50:
            trend = "空头"
            strength = ((sma50 - price) / sma50 * 100)
        else:
            trend = "震荡"
            strength = 0

        return {
            'price': current['close'],
            'rsi': current['rsi'],
            'macd': current['macd'],
            'trend': trend,
            'strength': abs(strength)
        }
    except Exception as e:
        print(f"⚠️ 获取BTC数据失败: {e}")
        return None


def get_bnb_1h_data():
    """获取BNB 1小时数据"""
    try:
        # 获取30根1小时K线（确保有足够数据计算指标）
        klines = binance_client.futures_klines(
            symbol='BNBUSDT',
            interval='1h',
            limit=30
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = calculate_technical_indicators(df)
        current_data = df.iloc[-1]
        
        return {
            'rsi': current_data['rsi'],
            'macd': current_data['macd'],
            'macd_signal': current_data['macd_signal'],
            'sma_20': current_data['sma_20'],
            'sma_50': current_data['sma_50'],
            'rsi_series': df['rsi'].tail(10).tolist(),
            'macd_series': df['macd'].tail(10).tolist(),
        }
    except Exception as e:
        print(f"❌ 获取BNB 1小时数据失败: {e}")
        return None


def get_bnb_market_data():
    """获取BNB完整市场数据（15分钟）"""
    try:
        current_time = datetime.now()
        
        # 获取17根15分钟K线（最后一根是当前未完成的）
        klines = binance_client.futures_klines(
            symbol='BNBUSDT',
            interval='15m',
            limit=17
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = calculate_technical_indicators(df)
        
        # 当前K线（未完成）
        current_kline = klines[-1]
        current_open = float(current_kline[1])
        current_high = float(current_kline[2])
        current_low = float(current_kline[3])
        current_close = float(current_kline[4])
        current_volume = float(current_kline[5])
        current_change = ((current_close - current_open) / current_open * 100) if current_open > 0 else 0
        
        kline_start_time = datetime.fromtimestamp(int(current_kline[0])/1000)
        kline_end_time = kline_start_time + timedelta(minutes=15)
        elapsed_min = (current_time - kline_start_time).total_seconds() / 60
        
        # 计算24小时涨跌
        ticker_24h = binance_client.futures_ticker(symbol='BNBUSDT')
        change_24h = float(ticker_24h['priceChangePercent'])
        
        # 资金费率
        funding_rate_data = binance_client.futures_funding_rate(symbol='BNBUSDT', limit=1)
        funding_rate = float(funding_rate_data[0]['fundingRate']) if funding_rate_data else 0
        
        # 持仓量
        open_interest_data = binance_client.futures_open_interest(symbol='BNBUSDT')
        open_interest = float(open_interest_data['openInterest'])
        
        # 获取当前持仓
        position = get_current_position()
        
        current_data = df.iloc[-1]
        
        # 计算15分钟涨跌（从16根前到现在）
        if len(df) >= 17:
            price_16_ago = df.iloc[-17]['close']
            change_15m = ((current_close - price_16_ago) / price_16_ago * 100)
        else:
            change_15m = 0
        
        return {
            'price': current_close,
            'change_24h': change_24h,
            'change_15m': change_15m,
            'funding_rate': funding_rate,
            'open_interest': open_interest,
            'position': position,
            # 当前K线实时数据
            'current_kline': {
                'open': current_open,
                'high': current_high,
                'low': current_low,
                'close': current_close,
                'volume': current_volume,
                'change': current_change,
                'elapsed_min': elapsed_min,
                'start_time': kline_start_time.strftime('%H:%M'),
                'end_time': kline_end_time.strftime('%H:%M')
            },
            # 历史16根K线
            'historical_klines': klines[-17:-1],
            # 技术指标
            'rsi': current_data['rsi'],
            'macd': current_data['macd'],
            'macd_signal': current_data['macd_signal'],
            'atr': current_data['atr_14'],
            'bb_position': current_data['bb_position'],
            'sma_20': current_data['sma_20'],
            'sma_50': current_data['sma_50'],
            # 时间序列（最近10个值，从旧→新）
            'rsi_series': df['rsi'].tail(10).tolist(),
            'macd_series': df['macd'].tail(10).tolist(),
            'atr_series': df['atr_14'].tail(10).tolist(),
        }
    except Exception as e:
        print(f"❌ 获取BNB数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_current_position():
    """获取当前BNB持仓"""
    try:
        positions = binance_client.futures_position_information(symbol='BNBUSDT')

        for pos in positions:
            position_amt = float(pos['positionAmt'])
            if position_amt != 0:
                    return {
                    'side': 'LONG' if position_amt > 0 else 'SHORT',
                    'amount': abs(position_amt),
                    'entry_price': float(pos['entryPrice']),
                    'unrealized_pnl': float(pos['unRealizedProfit']),
                    'leverage': int(pos['leverage'])
                }
        return None
    except Exception as e:
        print(f"⚠️ 获取持仓失败: {e}")
        return None


def get_account_balance():
    """获取账户余额"""
    try:
        account = binance_client.futures_account()
        for asset in account['assets']:
            if asset['asset'] == 'USDT':
                return {
                    'total': float(asset['walletBalance']),
                    'available': float(asset['availableBalance']),
                    'unrealized_pnl': float(asset['unrealizedProfit'])
                }
        return None
    except Exception as e:
        print(f"⚠️ 获取余额失败: {e}")
        return None


def analyze_portfolio_with_ai(market_data, bnb_1h_data, btc_data):
    """使用AI分析市场并做出交易决策"""
    global INVOCATION_COUNT
    INVOCATION_COUNT += 1
    
    # 保存运行时状态
    save_current_runtime()
    
    current_time = datetime.now()
    runtime_minutes = (current_time - PROGRAM_START_TIME).total_seconds() / 60
    
    # 构建当前K线文本
    ck = market_data['current_kline']
    if ck['change'] > 0:
        kline_body = "🟢 阳线"
    elif ck['change'] < 0:
        kline_body = "🔴 阴线"
    else:
        kline_body = "➖ 平线"
    
    volatility = ((ck['high'] - ck['low']) / ck['open'] * 100) if ck['open'] > 0 else 0
    
    current_kline_text = f"""
【当前K线实时状态】（15分钟周期进行中）
- 时间窗口: {ck['start_time']} - {ck['end_time']} (已运行 {ck['elapsed_min']:.0f}/15分钟)
- 开盘价: ${ck['open']:.2f}
- 当前价: ${ck['close']:.2f}
- 本K最高: ${ck['high']:.2f}
- 本K最低: ${ck['low']:.2f}
- 成交量: {ck['volume']:.2f}
- K线状态: {kline_body} ({ck['change']:+.2f}%)
- 波动幅度: {volatility:.2f}%"""
    
    # 构建历史K线文本
    kline_text = "\n【历史16根K线】（按时间顺序：从旧→新，共4小时历史数据）："
    for i, kline in enumerate(market_data['historical_klines'], 1):
        open_p = float(kline[1])
        high_p = float(kline[2])
        low_p = float(kline[3])
        close_p = float(kline[4])
        change = ((close_p - open_p) / open_p * 100) if open_p > 0 else 0
        body = "🟢" if close_p > open_p else "🔴" if close_p < open_p else "➖"
        kline_text += f"\n  K{i}: {body} O${open_p:.2f} H${high_p:.2f} L${low_p:.2f} C${close_p:.2f} ({change:+.2f}%)"
    
    # 构建技术指标文本（15分钟）
    rsi_series_text = ", ".join([f"{x:.1f}" for x in market_data['rsi_series'][-5:]])
    macd_series_text = ", ".join([f"{x:.4f}" for x in market_data['macd_series'][-5:]])
    atr_series_text = ", ".join([f"{x:.2f}" for x in market_data['atr_series'][-5:]])
    
    # 构建1小时数据文本
    if bnb_1h_data:
        rsi_series_1h_text = ", ".join([f"{x:.1f}" for x in bnb_1h_data['rsi_series'][-5:]])
        macd_series_1h_text = ", ".join([f"{x:.4f}" for x in bnb_1h_data['macd_series'][-5:]])
        bnb_1h_text = f"""

【1小时技术指标】
- RSI: {bnb_1h_data['rsi']:.1f} | 时间序列: [{rsi_series_1h_text}]
- MACD: {bnb_1h_data['macd']:.4f} | 时间序列: [{macd_series_1h_text}]
- SMA20: ${bnb_1h_data['sma_20']:.2f} | SMA50: ${bnb_1h_data['sma_50']:.2f}"""
    else:
        bnb_1h_text = ""
    
    # SMA位置关系（客观数据）
    sma20 = market_data['sma_20']
    sma50 = market_data['sma_50']
    price = market_data['price']
    
    # 资金费率（客观数据）
    funding_rate = market_data['funding_rate']
    if funding_rate > 0.0001:
        funding_text = "多头付费"
    elif funding_rate < -0.0001:
        funding_text = "空头付费"
    else:
        funding_text = "中性"
    
    # BTC大盘参考
    btc_text = ""
    if btc_data:
        btc_text = f"""
【BTC大盘参考】（15分钟周期）
- 价格: ${btc_data['price']:,.2f}
- RSI: {btc_data['rsi']:.1f}
- MACD: {btc_data['macd']:.4f}
- 趋势: {btc_data['trend']} (强度{btc_data['strength']:.2f}%)"""
    
    # 持仓信息
    position_text = ""
    if market_data['position']:
        pos = market_data['position']
        pnl_percent = (pos['unrealized_pnl'] / (pos['amount'] * pos['entry_price'] / TRADE_CONFIG['leverage'])) * 100 if pos['entry_price'] > 0 else 0
        position_text = f"""
    【当前持仓】
- 方向: {pos['side']}
- 数量: {pos['amount']:.2f} BNB
- 开仓价: ${pos['entry_price']:.2f}
- 未实现盈亏: {pos['unrealized_pnl']:+.2f} USDT ({pnl_percent:+.2f}%)"""
    else:
        position_text = "\n【当前持仓】无持仓"
    
    # 读取最近的AI决策历史
    last_decisions_text = ""
    try:
        if os.path.exists(AI_DECISIONS_FILE):
            with open(AI_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                decisions_data = json.load(f)
                recent_decisions = decisions_data.get('decisions', [])[-3:]
                
                if recent_decisions:
                    last_decisions_text = "\n【最近AI决策记录】（最近45分钟）"
                    for i, dec in enumerate(reversed(recent_decisions), 1):
                        time_str = dec.get('time', 'N/A')[:19] if dec.get('time') else 'N/A'
                        coin = dec.get('coin', 'N/A')
                        action = dec.get('action', 'N/A')
                        reason = dec.get('reason', 'N/A')
                        confidence = dec.get('confidence', 'N/A')
                        
                        last_decisions_text += f"""
{i}. {time_str} - {coin}
   操作: {action}
   理由: {reason}
   信心: {confidence}
"""
    except Exception as e:
        print(f"⚠️ 读取历史决策失败: {e}")
    
    # 账户余额
    balance = get_account_balance()
    balance_text = ""
    if balance:
        balance_text = f"""
【账户状态】
- 总权益: {balance['total']:.2f} USDT
- 可用余额: {balance['available']:.2f} USDT
- 未实现盈亏: {balance['unrealized_pnl']:+.2f} USDT"""
    
    # 统计信息
    stats_text = trading_stats.generate_stats_text_for_ai()
    
    market_text = f"""
【系统运行状态】
- 启动时间: {PROGRAM_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}
- 运行时长: {runtime_minutes:.1f}分钟
- AI调用次数: {INVOCATION_COUNT}次

【BNB/USDT市场数据】
- 价格: ${market_data['price']:,.2f} | 24h涨跌: {market_data['change_24h']:+.2f}% | 15m涨跌: {market_data['change_15m']:+.2f}%
- 资金费率: {funding_rate:.6f} ({funding_text}) | 持仓量: {market_data['open_interest']:,.0f}{current_kline_text}

【15分钟技术指标】
- RSI: {market_data['rsi']:.1f} | 时间序列: [{rsi_series_text}]
- MACD: {market_data['macd']:.4f} | 时间序列: [{macd_series_text}]
- ATR: {market_data['atr']:.2f} | 时间序列: [{atr_series_text}]
- 价格: ${price:.2f} | SMA20: ${sma20:.2f} | SMA50: ${sma50:.2f}
- 布林带位置: {market_data['bb_position']:.2%}{bnb_1h_text}{kline_text}{btc_text}{balance_text}{position_text}{stats_text}{last_decisions_text}
"""
    
    prompt = f"""
你是一位专业的日内交易员，负责BNB/USDT合约交易（3倍杠杆）。

{market_text}

【数据周期】
- 15分钟K线数据
- 历史16根K线（4小时历史数据，从旧→新）

【决策要求】
1. 综合分析当前K线实时状态、历史K线形态、技术指标、BTC大盘
2. 给出交易决策：BUY_OPEN（开多）/ SELL_OPEN（开空）/ CLOSE（平仓）/ HOLD（观望）
3. 决定开仓金额（position_value，单位USDT）：
   - 根据信号强度和信心程度决定
   - 强信号高信心：可用余额的40-50%
   - 中等信号中信心：可用余额的20-30%
   - 弱信号低信心：可用余额的10-20%
   - CLOSE和HOLD时填0
4. 说明决策理由（包含K线形态和技术指标分析）
5. 评估信心程度：HIGH（>80%胜率预期）/ MEDIUM（60-80%）/ LOW（<60%）
6. 评估风险等级：HIGH（市场剧烈波动）/ MEDIUM（正常波动）/ LOW（稳定环境）

请严格按照以下JSON格式回复（不要有任何额外文本）：
{{
    "action": "BUY_OPEN|SELL_OPEN|CLOSE|HOLD",
    "reason": "K线：[形态描述] | 指标：[指标描述]",
    "position_value": 100,
    "confidence": "HIGH|MEDIUM|LOW",
    "risk_level": "HIGH|MEDIUM|LOW"
}}
    """

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的日内交易员，专注于技术分析和风险控制。"},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.1
        )

        result = response.choices[0].message.content
        print(f"\n{'='*60}")
        print(f"{tr('ai_raw')}: {result}")
        print(f"{'='*60}\n")

        # 提取JSON
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            decision = json.loads(json_str)
            
            # 保存决策
            save_ai_decision(
                coin='BNB',
                action=decision.get('action', 'HOLD'),
                reason=decision.get('reason', 'N/A'),
                confidence=decision.get('confidence', 'LOW'),
                position_value=decision.get('position_value', 0),
                risk_level=decision.get('risk_level', 'MEDIUM')
            )
            
            return decision
        else:
            print("⚠️ Unable to parse AI response, use HOLD" if LANG == 'EN' else "⚠️ 无法解析AI回复，使用HOLD")
            return {"action": "HOLD", "reason": "解析失败", "confidence": "LOW"}

    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "HOLD", "reason": f"AI调用失败: {e}", "confidence": "LOW"}


def execute_trade(decision, market_data):
    """执行交易"""
    action = decision.get('action', 'HOLD')

    print(f"\n{'='*60}")
    print(tr('ai_decision'))
    print(f"{'='*60}")
    print(f"{tr('action')}: {action}")
    print(f"{tr('reason')}: {decision.get('reason', 'N/A')}")
    print(f"{tr('position_value')}: {decision.get('position_value', 0)} USDT")
    print(f"{tr('confidence')}: {decision.get('confidence', 'N/A')}")
    print(f"{tr('risk_level')}: {decision.get('risk_level', 'N/A')}")
    print(f"{'='*60}\n")
    
    if action == 'HOLD':
        print(tr('hold'))
        return

    if TRADE_CONFIG.get('test_mode', False):
        print(tr('test_only'))
        return

    try:
        current_position = market_data['position']
        balance = get_account_balance()
        current_price = market_data['price']
        
        # 准备AI决策信号数据
        signal_data = {
            'reason': decision.get('reason', 'N/A'),
            'confidence': decision.get('confidence', 'N/A')
        }
        
        if action == 'BUY_OPEN':
            if current_position and current_position['side'] == 'SHORT':
                # 先平空仓，记录统计
                print(f"{tr('buy_close_short')}: {current_position['amount']:.2f} BNB")
                binance_client.futures_create_order(
                    symbol='BNBUSDT',
                    side='BUY',
                    type='MARKET',
                    quantity=current_position['amount']
                )
                # 记录平仓统计
                trading_stats.record_position_exit(
                    exit_price=current_price,
                    amount=current_position['amount'],
                    signal_data=signal_data
                )
                time.sleep(1)
            
            if not current_position or current_position['side'] == 'SHORT':
                # 开多仓（使用AI指定的开仓金额）
                if balance and balance['available'] > 10:
                    # 获取AI指定的开仓金额
                    ai_position_value = float(decision.get('position_value', 0))
                    
                    # 计算上限：可用余额 * 杠杆
                    max_position_value = balance['available'] * TRADE_CONFIG['leverage']
                    
                    # 边界检查：不能超过可用资金
                    position_value = min(ai_position_value, max_position_value)
                    
                    # 计算开仓数量
                    qty = position_value / market_data['price']
                    qty = math.floor(qty * 100) / 100  # 保留2位小数
                    
                    # 边界检查：必须满足最小数量要求
                    if qty >= TRADE_CONFIG['min_order_qty']:
                        actual_value = qty * market_data['price']
                        if LANG == 'EN':
                            print(f"{tr('buy_open')}: {qty:.2f} BNB (value ${actual_value:.2f})")
                            print(f"   AI: ${ai_position_value:.2f} | Used: ${actual_value:.2f}")
                        else:
                            print(f"{tr('buy_open')}: {qty:.2f} BNB (价值 ${actual_value:.2f})")
                            print(f"   AI建议: ${ai_position_value:.2f} | 实际使用: ${actual_value:.2f}")
                        binance_client.futures_create_order(
                            symbol='BNBUSDT',
                            side='BUY',
                            type='MARKET',
                            quantity=qty
                        )
                        # 记录开仓统计
                        trading_stats.record_position_entry(
                            side='BUY',
                            entry_price=current_price,
                            amount=qty,
                            signal_data=signal_data
                        )
                    else:
                        print(tr('qty_too_small').format(qty=qty, min_qty=TRADE_CONFIG['min_order_qty']))
        
        elif action == 'SELL_OPEN':
            if current_position and current_position['side'] == 'LONG':
                # 先平多仓，记录统计
                print(f"{tr('sell_close_long')}: {current_position['amount']:.2f} BNB")
                binance_client.futures_create_order(
                    symbol='BNBUSDT',
                    side='SELL',
                    type='MARKET',
                    quantity=current_position['amount']
                )
                # 记录平仓统计
                trading_stats.record_position_exit(
                    exit_price=current_price,
                    amount=current_position['amount'],
                    signal_data=signal_data
                )
                time.sleep(1)
            
            if not current_position or current_position['side'] == 'LONG':
                # 开空仓（使用AI指定的开仓金额）
                if balance and balance['available'] > 10:
                    # 获取AI指定的开仓金额
                    ai_position_value = float(decision.get('position_value', 0))
                    
                    # 计算上限：可用余额 * 杠杆
                    max_position_value = balance['available'] * TRADE_CONFIG['leverage']
                    
                    # 边界检查：不能超过可用资金
                    position_value = min(ai_position_value, max_position_value)
                    
                    # 计算开仓数量
                    qty = position_value / market_data['price']
                    qty = math.floor(qty * 100) / 100  # 保留2位小数
                    
                    # 边界检查：必须满足最小数量要求
                    if qty >= TRADE_CONFIG['min_order_qty']:
                        actual_value = qty * market_data['price']
                        if LANG == 'EN':
                            print(f"{tr('sell_open')}: {qty:.2f} BNB (value ${actual_value:.2f})")
                            print(f"   AI: ${ai_position_value:.2f} | Used: ${actual_value:.2f}")
                        else:
                            print(f"{tr('sell_open')}: {qty:.2f} BNB (价值 ${actual_value:.2f})")
                            print(f"   AI建议: ${ai_position_value:.2f} | 实际使用: ${actual_value:.2f}")
                        binance_client.futures_create_order(
                            symbol='BNBUSDT',
                            side='SELL',
                            type='MARKET',
                            quantity=qty
                        )
                        # 记录开仓统计
                        trading_stats.record_position_entry(
                            side='SELL',
                            entry_price=current_price,
                            amount=qty,
                            signal_data=signal_data
                        )
                    else:
                        print(tr('qty_too_small').format(qty=qty, min_qty=TRADE_CONFIG['min_order_qty']))
        
        elif action == 'CLOSE':
            if current_position:
                side = 'SELL' if current_position['side'] == 'LONG' else 'BUY'
                if LANG == 'EN':
                    print(f"🔒 Close: {current_position['side']} {current_position['amount']:.2f} BNB")
                else:
                    print(f"🔒 平仓: {current_position['side']} {current_position['amount']:.2f} BNB")
                binance_client.futures_create_order(
                    symbol='BNBUSDT',
                    side=side,
                    type='MARKET',
                    quantity=current_position['amount']
                )
                # 记录平仓统计
                trading_stats.record_position_exit(
                    exit_price=current_price,
                    amount=current_position['amount'],
                    signal_data=signal_data
                )
        
        print(tr('trade_ok'))
    
    except Exception as e:
        print(tr('trade_fail').format(err=e))
        import traceback
        traceback.print_exc()


def trading_bot():
    """主交易逻辑"""
    print("\n" + "=" * 60)
    print(f"{tr('run_time')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 设置杠杆（首次）
    try:
        binance_client.futures_change_leverage(
            symbol='BNBUSDT',
            leverage=TRADE_CONFIG['leverage']
        )
    except:
        pass
    
    # 获取市场数据
    market_data = get_bnb_market_data()
    if not market_data:
        print("⚠️ Failed to fetch market data, skip" if LANG == 'EN' else "⚠️ 获取市场数据失败，跳过本次")
        return

    # 获取1小时数据
    bnb_1h_data = get_bnb_1h_data()
    
    # 获取BTC参考
    btc_data = get_btc_market_reference()
    
    # AI分析
    decision = analyze_portfolio_with_ai(market_data, bnb_1h_data, btc_data)
    
    # 执行交易
    execute_trade(decision, market_data)


def main():
    """主函数"""
    print(tr('bot_started'))
    print(f"{tr('leverage')}: {TRADE_CONFIG['leverage']}x")
    print(f"{tr('period')}: 15m")

    if TRADE_CONFIG.get('test_mode', False):
        print(tr('test_mode'))
    else:
        print(tr('live_mode'))

    # 每15分钟执行一次
    schedule.every(15).minutes.do(trading_bot)
    print(tr('schedule'))

    # 立即执行一次
    trading_bot()

    # 循环执行
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
