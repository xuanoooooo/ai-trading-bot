#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Trading Bot - DeepSeek Automated Trading
AI交易机器人 - DeepSeek自动交易

Main trading bot with AI-driven decision making and dynamic position management.
主要交易机器人，具有AI驱动决策和动态仓位管理功能。

Author: AI Trading Bot
License: MIT
"""

import os
import time
import schedule
from openai import OpenAI
import ccxt
import pandas as pd
from datetime import datetime
import json
import re
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

# Configure logging - Auto rotation, max 10MB, keep 3 backups
# 配置日志 - 自动轮转，最大10MB，保留3个备份
log_handler = RotatingFileHandler(
    'bnb_trader.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3,  # Keep 3 backup files / 保留3个备份文件
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(message)s'))

# Also output to console / 同时输出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

# Configure logger / 配置 logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, console_handler]
)

# Redirect print to logging / 重定向 print 到 logging
def print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    logging.info(message)

# Initialize DeepSeek client / 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# Trading configuration - Binance Plus Enhanced Edition (AI Dynamic Position Management)
# 交易参数配置 - 币安专用 Plus 增强版（AI动态仓位管理）
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',  # Trading pair - BNB Binance Coin / 交易对 - BNB币安币
    'leverage': 3,  # Leverage multiplier - Fixed 3x leverage / 杠杆倍数 - 固定3倍杠杆
    'timeframe': '15m',  # Use 15-minute K-lines / 使用15分钟K线
    'test_mode': False,  # Live mode - Real trading / 实盘模式 - 真实交易
    'data_points': 96,  # 24-hour data (96 x 15-minute K-lines) / 24小时数据（96根15分钟K线）
    'analysis_periods': {
        'short_term': 20,  # Short-term moving average / 短期均线
        'medium_term': 50,  # Medium-term moving average / 中期均线
        'long_term': 96  # Long-term trend / 长期趋势
    },
    # AI position management configuration / AI仓位管理配置
    'position_management': {
        'mode': 'ai_controlled',  # AI fully controls position / AI完全控制仓位
        'max_position_percent': 80,  # AI max uses 80% available funds / AI最多使用80%可用资金
        'min_position_percent': 5,   # AI min uses 5% available funds / AI最少使用5%可用资金
        'force_reserve_percent': 20,  # Force reserve 20% buffer funds / 强制预留20%缓冲资金
        'allow_zero': True  # Allow AI to return 0 (no trading) / 允许AI返回0（不交易）
    }
}

# Initialize Binance exchange / 初始化币安交易所
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET'),
})

# Global variables to store historical data / 全局变量存储历史数据
price_history = []
signal_history = []
position = None


def setup_exchange():
    """
    Setup exchange parameters
    设置交易所参数
    """
    try:
        # 设置杠杆
        exchange.set_leverage(TRADE_CONFIG['leverage'], TRADE_CONFIG['symbol'])
        print(f"设置杠杆倍数: {TRADE_CONFIG['leverage']}x")

        # 获取余额
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        print(f"当前USDT余额: {usdt_balance:.2f}")

        return True
    except Exception as e:
        print(f"交易所设置失败: {e}")
        return False


def calculate_technical_indicators(df):
    """
    Calculate technical indicators - From first strategy
    计算技术指标 - 来自第一个策略
    """
    try:
        # 移动平均线
        df['sma_5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()

        # 指数移动平均线
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # 相对强弱指数 (RSI)
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

        # 成交量均线
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']

        # 支撑阻力位
        df['resistance'] = df['high'].rolling(20).max()
        df['support'] = df['low'].rolling(20).min()

        # 填充NaN值
        df = df.bfill().ffill()

        return df
    except Exception as e:
        print(f"技术指标计算失败: {e}")
        return df


def get_support_resistance_levels(df, lookback=20):
    """计算支撑阻力位"""
    try:
        recent_high = df['high'].tail(lookback).max()
        recent_low = df['low'].tail(lookback).min()
        current_price = df['close'].iloc[-1]

        resistance_level = recent_high
        support_level = recent_low

        # 动态支撑阻力（基于布林带）
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]

        return {
            'static_resistance': resistance_level,
            'static_support': support_level,
            'dynamic_resistance': bb_upper,
            'dynamic_support': bb_lower,
            'price_vs_resistance': ((resistance_level - current_price) / current_price) * 100,
            'price_vs_support': ((current_price - support_level) / support_level) * 100
        }
    except Exception as e:
        print(f"支撑阻力计算失败: {e}")
        return {}


def get_market_trend(df):
    """获取价格与关键指标的位置关系（纯数值，无主观判断）"""
    try:
        current_price = df['close'].iloc[-1]
        
        # 价格与均线的位置关系（百分比差值）
        sma_20_diff = ((current_price - df['sma_20'].iloc[-1]) / df['sma_20'].iloc[-1]) * 100
        sma_50_diff = ((current_price - df['sma_50'].iloc[-1]) / df['sma_50'].iloc[-1]) * 100
        
        # MACD与信号线的差值
        macd_diff = df['macd'].iloc[-1] - df['macd_signal'].iloc[-1]
        
        # 价格动量（最近5根K线的平均涨跌幅）
        recent_changes = df['close'].pct_change().tail(5).mean() * 100
        
        return {
            'price_vs_sma20': sma_20_diff,      # 价格相对SMA20的百分比
            'price_vs_sma50': sma_50_diff,      # 价格相对SMA50的百分比
            'macd_vs_signal': macd_diff,        # MACD与信号线的差值
            'rsi_level': df['rsi'].iloc[-1],    # RSI数值
            'recent_momentum': recent_changes   # 近期动量
        }
    except Exception as e:
        print(f"趋势数据获取失败: {e}")
        return {}


def get_btc_ohlcv_enhanced():
    """增强版：获取BTC K线数据并计算技术指标"""
    try:
        # 获取K线数据
        ohlcv = exchange.fetch_ohlcv(TRADE_CONFIG['symbol'], TRADE_CONFIG['timeframe'],
                                     limit=TRADE_CONFIG['data_points'])

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # 计算技术指标
        df = calculate_technical_indicators(df)

        current_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # 获取技术分析数据
        trend_analysis = get_market_trend(df)
        levels_analysis = get_support_resistance_levels(df)

        return {
            'price': current_data['close'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'high': current_data['high'],
            'low': current_data['low'],
            'volume': current_data['volume'],
            'timeframe': TRADE_CONFIG['timeframe'],
            'price_change': ((current_data['close'] - previous_data['close']) / previous_data['close']) * 100,
            'kline_data': df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(10).to_dict('records'),
            'technical_data': {
                'sma_5': current_data.get('sma_5', 0),
                'sma_20': current_data.get('sma_20', 0),
                'sma_50': current_data.get('sma_50', 0),
                'rsi': current_data.get('rsi', 0),
                'macd': current_data.get('macd', 0),
                'macd_signal': current_data.get('macd_signal', 0),
                'macd_histogram': current_data.get('macd_histogram', 0),
                'bb_upper': current_data.get('bb_upper', 0),
                'bb_lower': current_data.get('bb_lower', 0),
                'bb_position': current_data.get('bb_position', 0),
                'volume_ratio': current_data.get('volume_ratio', 0)
            },
            'trend_analysis': trend_analysis,
            'levels_analysis': levels_analysis,
            'full_data': df
        }
    except Exception as e:
        print(f"获取增强K线数据失败: {e}")
        return None


def generate_technical_analysis_text(price_data):
    """生成技术分析文本"""
    if 'technical_data' not in price_data:
        return "技术指标数据不可用"

    tech = price_data['technical_data']
    trend = price_data.get('trend_analysis', {})
    levels = price_data.get('levels_analysis', {})

    # 检查数据有效性
    def safe_float(value, default=0):
        return float(value) if value and pd.notna(value) else default

    analysis_text = f"""
    【技术指标分析】
    📈 移动平均线:
    - 5周期: {safe_float(tech['sma_5']):.2f} | 价格相对: {(price_data['price'] - safe_float(tech['sma_5'])) / safe_float(tech['sma_5']) * 100:+.2f}%
    - 20周期: {safe_float(tech['sma_20']):.2f} | 价格相对: {(price_data['price'] - safe_float(tech['sma_20'])) / safe_float(tech['sma_20']) * 100:+.2f}%
    - 50周期: {safe_float(tech['sma_50']):.2f} | 价格相对: {(price_data['price'] - safe_float(tech['sma_50'])) / safe_float(tech['sma_50']) * 100:+.2f}%

    🎯 价格与指标位置关系:
    - 价格相对SMA20: {trend.get('price_vs_sma20', 0):+.2f}%
    - 价格相对SMA50: {trend.get('price_vs_sma50', 0):+.2f}%
    - MACD相对信号线: {trend.get('macd_vs_signal', 0):+.6f}
    - 近期动量: {trend.get('recent_momentum', 0):+.2f}%

    📊 动量指标:
    - RSI: {safe_float(tech['rsi']):.2f} ({'超买' if safe_float(tech['rsi']) > 70 else '超卖' if safe_float(tech['rsi']) < 30 else '中性'})
    - MACD: {safe_float(tech['macd']):.4f}
    - 信号线: {safe_float(tech['macd_signal']):.4f}

    🎚️ 布林带位置: {safe_float(tech['bb_position']):.2%} ({'上部' if safe_float(tech['bb_position']) > 0.7 else '下部' if safe_float(tech['bb_position']) < 0.3 else '中部'})

    💰 关键水平:
    - 静态阻力: {safe_float(levels.get('static_resistance', 0)):.2f}
    - 静态支撑: {safe_float(levels.get('static_support', 0)):.2f}
    """
    return analysis_text


def get_account_status():
    """获取完整的账户状态信息（用于AI决策）"""
    try:
        balance = exchange.fetch_balance()
        
        # 获取USDT相关信息
        total_balance = balance['USDT']['total']  # 总权益
        free_balance = balance['USDT']['free']    # 可用余额
        used_balance = balance['USDT']['used']    # 已用保证金
        
        # 计算保证金占用率
        margin_ratio = (used_balance / total_balance * 100) if total_balance > 0 else 0
        
        # 获取当前持仓
        current_position = get_current_position()
        
        # 计算持仓价值和盈亏
        position_value = 0
        unrealized_pnl = 0
        pnl_percent = 0
        
        if current_position:
            position_value = abs(current_position['size']) * current_position['entry_price']
            unrealized_pnl = current_position['unrealized_pnl']
            if current_position['entry_price'] > 0:
                pnl_percent = (unrealized_pnl / (position_value / TRADE_CONFIG['leverage'])) * 100
        
        return {
            'total_balance': total_balance,
            'free_balance': free_balance,
            'used_margin': used_balance,
            'margin_ratio': margin_ratio,
            'position_value': position_value,
            'unrealized_pnl': unrealized_pnl,
            'pnl_percent': pnl_percent,
            'has_position': current_position is not None
        }
    except Exception as e:
        print(f"获取账户状态失败: {e}")
        return {
            'total_balance': 0,
            'free_balance': 0,
            'used_margin': 0,
            'margin_ratio': 0,
            'position_value': 0,
            'unrealized_pnl': 0,
            'pnl_percent': 0,
            'has_position': False
        }


def get_current_position():
    """获取当前持仓情况"""
    try:
        positions = exchange.fetch_positions([TRADE_CONFIG['symbol']])

        # 标准化配置的交易对符号用于比较（币安合约格式）
        config_symbol = TRADE_CONFIG['symbol']
        config_symbol_normalized = config_symbol + ':USDT'  # 如：DOGE/USDT:USDT

        for pos in positions:
            # 比较标准化的符号（支持两种格式）
            if pos['symbol'] == config_symbol_normalized or pos['symbol'] == config_symbol:
                # 获取持仓数量
                position_amt = 0
                if 'positionAmt' in pos.get('info', {}):
                    position_amt = float(pos['info']['positionAmt'])
                elif 'contracts' in pos:
                    # 使用 contracts 字段，根据 side 确定方向
                    contracts = float(pos['contracts'])
                    if pos.get('side') == 'short':
                        position_amt = -contracts
                    else:
                        position_amt = contracts

                if position_amt != 0:  # 有持仓
                    side = 'long' if position_amt > 0 else 'short'
                    return {
                        'side': side,
                        'size': abs(position_amt),
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                        'position_amt': position_amt,
                        'symbol': pos['symbol']
                    }

        return None

    except Exception as e:
        print(f"获取持仓失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def safe_json_parse(json_str):
    """安全解析JSON，处理格式不规范的情况"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # 修复常见的JSON格式问题
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败，原始内容: {json_str}")
            print(f"错误详情: {e}")
            return None


def create_fallback_signal(price_data):
    """创建备用交易信号"""
    return {
        "signal": "HOLD",
        "reason": "因技术分析暂时不可用，采取保守策略",
        "stop_loss": price_data['price'] * 0.98,  # -2%
        "take_profit": price_data['price'] * 1.02,  # +2%
        "confidence": "LOW",
        "position_percent": 0,  # HOLD信号不交易
        "is_fallback": True
    }


def analyze_with_deepseek(price_data):
    """使用DeepSeek分析市场并生成交易信号（增强版）"""

    # 生成技术分析文本
    technical_analysis = generate_technical_analysis_text(price_data)

    # 构建K线数据文本
    kline_text = f"【最近5根{TRADE_CONFIG['timeframe']}K线数据】\n"
    for i, kline in enumerate(price_data['kline_data'][-5:]):
        trend = "阳线" if kline['close'] > kline['open'] else "阴线"
        change = ((kline['close'] - kline['open']) / kline['open']) * 100
        kline_text += f"K线{i + 1}: {trend} 开盘:{kline['open']:.2f} 收盘:{kline['close']:.2f} 涨跌:{change:+.2f}%\n"

    # 添加上次交易信号
    signal_text = ""
    if signal_history:
        last_signal = signal_history[-1]
        signal_text = f"\n【上次交易信号】\n信号: {last_signal.get('signal', 'N/A')}\n信心: {last_signal.get('confidence', 'N/A')}"

    # 获取账户状态信息
    account_status = get_account_status()
    
    # 构建账户信息文本
    account_text = f"""
    【账户信息】
    - 总权益: {account_status['total_balance']:.2f} USDT
    - 可用余额: {account_status['free_balance']:.2f} USDT
    - 已用保证金: {account_status['used_margin']:.2f} USDT
    - 保证金占用率: {account_status['margin_ratio']:.1f}%
    - 当前杠杆: {TRADE_CONFIG['leverage']}x
    """
    
    # 添加持仓详情
    current_pos = get_current_position()
    if current_pos:
        position_text = f"""
    【当前持仓】
    - 持仓方向: {current_pos['side']}仓
    - 持仓数量: {current_pos['size']:.2f}
    - 持仓价值: {account_status['position_value']:.2f} USDT
    - 未实现盈亏: {account_status['unrealized_pnl']:+.2f} USDT ({account_status['pnl_percent']:+.2f}%)
        """
    else:
        position_text = "\n    【当前持仓】无持仓"

    prompt = f"""
    你是一个专业的加密货币交易分析师和资金管理专家。请基于以下{TRADE_CONFIG['symbol']} {TRADE_CONFIG['timeframe']}周期数据进行分析：

    {kline_text}

    {technical_analysis}

    {signal_text}

    【当前行情】
    - 当前价格: ${price_data['price']:,.2f}
    - 时间: {price_data['timestamp']}
    - 本K线最高: ${price_data['high']:,.2f}
    - 本K线最低: ${price_data['low']:,.2f}
    - 本K线成交量: {price_data['volume']:.2f}
    - 价格变化: {price_data['price_change']:+.2f}%

    {account_text}
    {position_text}

    【分析要求】
    1. 基于{TRADE_CONFIG['timeframe']}K线趋势和技术指标给出交易信号: BUY(买入) / SELL(卖出) / HOLD(观望)
    2. 简要分析理由（考虑趋势连续性、支撑阻力、成交量等因素）
    3. 基于技术分析建议合理的止损价位
    4. 基于技术分析建议合理的止盈价位
    5. 评估信号信心程度
    6. **仓位管理：根据信号强度、市场波动、当前持仓情况，决定使用可用余额的百分比作为保证金（0-100）**
       
       杠杆机制说明：
       - 当前杠杆为{TRADE_CONFIG['leverage']}x
       - 你返回的百分比 = 使用多少可用余额作为保证金
       - 实际控制的仓位价值 = 保证金 × {TRADE_CONFIG['leverage']}倍
       
       计算示例：
       - 可用余额100 USDT，你返回50%
       - 系统将使用 50 USDT 作为保证金
       - 实际开仓价值为 50 × {TRADE_CONFIG['leverage']} = {50 * TRADE_CONFIG['leverage']} USDT 的仓位
       
       备注：
       - HOLD信号时，position_percent应为0
       - 系统风控自动限制最大80%，并预留20%缓冲
       - 交易所最小交易量0.01个，请根据当前价格确保仓位足够

    【重要格式要求】
    - 必须返回纯JSON格式，不要有任何额外文本
    - 所有属性名必须使用双引号
    - 不要使用单引号
    - 不要添加注释
    - 确保JSON格式完全正确

    请用以下JSON格式回复：
    {{
        "signal": "BUY|SELL|HOLD",
        "reason": "分析理由",
        "stop_loss": 具体价格,
        "take_profit": 具体价格,
        "confidence": "HIGH|MEDIUM|LOW",
        "position_percent": 0到100的整数
    }}
    """

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": f"您是一位专业的交易员，专注于{TRADE_CONFIG['timeframe']}周期趋势分析。请结合K线形态和技术指标做出判断，并严格遵循JSON格式要求。"},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.1
        )

        # 安全解析JSON
        result = response.choices[0].message.content
        print(f"DeepSeek原始回复: {result}")

        # 提取JSON部分
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            signal_data = safe_json_parse(json_str)

            if signal_data is None:
                signal_data = create_fallback_signal(price_data)
        else:
            signal_data = create_fallback_signal(price_data)

        # 验证必需字段
        required_fields = ['signal', 'reason', 'stop_loss', 'take_profit', 'confidence', 'position_percent']
        if not all(field in signal_data for field in required_fields):
            signal_data = create_fallback_signal(price_data)
        
        # 确保position_percent是数值且在合理范围内
        try:
            signal_data['position_percent'] = int(signal_data.get('position_percent', 0))
            signal_data['position_percent'] = max(0, min(100, signal_data['position_percent']))
        except (ValueError, TypeError):
            print("⚠️ position_percent格式错误，设为0")
            signal_data['position_percent'] = 0

        # 保存信号到历史记录
        signal_data['timestamp'] = price_data['timestamp']
        signal_history.append(signal_data)
        if len(signal_history) > 30:
            signal_history.pop(0)

        # 信号统计
        signal_count = len([s for s in signal_history if s.get('signal') == signal_data['signal']])
        total_signals = len(signal_history)
        print(f"信号统计: {signal_data['signal']} (最近{total_signals}次中出现{signal_count}次)")

        # 信号连续性检查
        if len(signal_history) >= 3:
            last_three = [s['signal'] for s in signal_history[-3:]]
            if len(set(last_three)) == 1:
                print(f"⚠️ 注意：连续3次{signal_data['signal']}信号")

        return signal_data

    except Exception as e:
        print(f"DeepSeek分析失败: {e}")
        return create_fallback_signal(price_data)


def calculate_position_size(signal_data, account_status, current_price):
    """
    根据AI返回的百分比和风控规则计算实际交易数量
    
    参数:
        signal_data: AI返回的信号数据（包含position_percent）
        account_status: 账户状态信息
        current_price: 当前价格
    
    返回:
        dict: {
            'amount': 交易数量,
            'margin_needed': 需要的保证金,
            'position_value': 仓位价值,
            'final_percent': 实际使用的百分比
        }
    """
    try:
        # 获取AI建议的百分比
        ai_percent = signal_data.get('position_percent', 0)
        
        # 如果是HOLD信号或百分比为0，不交易
        if signal_data['signal'] == 'HOLD' or ai_percent == 0:
            return {
                'amount': 0,
                'margin_needed': 0,
                'position_value': 0,
                'final_percent': 0
            }
        
        # 获取可用余额
        free_balance = account_status['free_balance']
        
        if free_balance <= 0:
            print("⚠️ 可用余额不足，无法开仓")
            return {
                'amount': 0,
                'margin_needed': 0,
                'position_value': 0,
                'final_percent': 0
            }
        
        # 应用风控限制
        config = TRADE_CONFIG['position_management']
        max_percent = config['max_position_percent']
        min_percent = config['min_position_percent']
        
        # 限制在最大最小范围内
        final_percent = max(min_percent, min(ai_percent, max_percent))
        
        # 计算保证金金额
        margin_needed = free_balance * (final_percent / 100)
        
        # 计算仓位价值（考虑杠杆）
        position_value = margin_needed * TRADE_CONFIG['leverage']
        
        # 计算交易数量
        raw_amount = position_value / current_price
        
        # ===== 容错处理 =====
        # 1. 精度处理：BNB保留3位小数
        amount = round(raw_amount, 3)
        
        # 2. 最小数量检查
        min_safe_amount = 0.01  # BNB最小0.01个
        if amount < min_safe_amount:
            print(f"⚠️ 计算数量{amount}太小（<{min_safe_amount}），无法下单")
            return {
                'amount': 0,
                'margin_needed': 0,
                'position_value': 0,
                'final_percent': 0
            }
        
        # 3. 合理性验证（防止计算错误）
        expected_value = amount * current_price
        value_diff_percent = abs(expected_value - position_value) / position_value * 100
        if value_diff_percent > 5:  # 误差不应超过5%
            print(f"❌ 数量计算异常：期望{position_value:.2f}U，实际{expected_value:.2f}U（误差{value_diff_percent:.1f}%）")
            return {
                'amount': 0,
                'margin_needed': 0,
                'position_value': 0,
                'final_percent': 0
            }
        
        # 如果AI的百分比被风控限制了，记录日志
        if final_percent != ai_percent:
            print(f"⚠️ AI建议 {ai_percent}%，风控调整为 {final_percent}%")
        
        print(f"💰 仓位计算: AI建议{ai_percent}% → 实际{final_percent}% → 保证金{margin_needed:.2f}U → 仓位{position_value:.2f}U → 数量{amount:.3f}")
        
        return {
            'amount': amount,
            'margin_needed': margin_needed,
            'position_value': position_value,
            'final_percent': final_percent
        }
        
    except Exception as e:
        print(f"仓位计算失败: {e}")
        return {
            'amount': 0,
            'margin_needed': 0,
            'position_value': 0,
            'final_percent': 0
        }


def execute_trade(signal_data, price_data):
    """执行交易 - AI动态仓位管理版本"""
    global position

    current_position = get_current_position()

    print(f"\n{'='*60}")
    print(f"📊 AI交易决策")
    print(f"{'='*60}")
    print(f"交易信号: {signal_data['signal']}")
    print(f"信心程度: {signal_data['confidence']}")
    print(f"AI建议仓位: {signal_data.get('position_percent', 0)}%")
    print(f"理由: {signal_data['reason']}")
    print(f"止损: ${signal_data['stop_loss']:,.2f}")
    print(f"止盈: ${signal_data['take_profit']:,.2f}")
    print(f"当前持仓: {current_position}")

    # HOLD信号或0仓位，不交易
    if signal_data['signal'] == 'HOLD' or signal_data.get('position_percent', 0) == 0:
        print("💤 AI决定观望，不执行交易")
        return

    if TRADE_CONFIG['test_mode']:
        print("测试模式 - 仅模拟交易")
        return

    try:
        # 获取账户状态
        account_status = get_account_status()
        
        # 计算动态仓位
        position_calc = calculate_position_size(signal_data, account_status, price_data['price'])
        
        if position_calc['amount'] == 0:
            print("⚠️ 计算出的交易数量为0，跳过交易")
            return
        
        trade_amount = position_calc['amount']
        
        # 执行交易逻辑
        if signal_data['signal'] == 'BUY':
            if current_position and current_position['side'] == 'short':
                # 先平空仓
                print(f"📉 平空仓: {current_position['size']:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_buy_order(
                    TRADE_CONFIG['symbol'],
                    current_position['size']
                )
                time.sleep(1)
                # 再开多仓
                print(f"📈 开多仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_buy_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )
            elif not current_position:
                # 直接开多仓
                print(f"📈 开多仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_buy_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )
            elif current_position['side'] == 'long':
                # 加多仓
                print(f"📈 加多仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_buy_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )

        elif signal_data['signal'] == 'SELL':
            if current_position and current_position['side'] == 'long':
                # 先平多仓
                print(f"📈 平多仓: {current_position['size']:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_sell_order(
                    TRADE_CONFIG['symbol'],
                    current_position['size']
                )
                time.sleep(1)
                # 再开空仓
                print(f"📉 开空仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_sell_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )
            elif not current_position:
                # 直接开空仓
                print(f"📉 开空仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_sell_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )
            elif current_position['side'] == 'short':
                # 加空仓
                print(f"📉 加空仓: {trade_amount:.4f} {TRADE_CONFIG['symbol']}")
                exchange.create_market_sell_order(
                    TRADE_CONFIG['symbol'],
                    trade_amount
                )

        print("✅ 订单执行成功")
        time.sleep(2)
        
        # 更新持仓信息
        position = get_current_position()
        new_account = get_account_status()
        print(f"\n更新后持仓: {position}")
        print(f"保证金占用: {new_account['margin_ratio']:.1f}%")
        print(f"可用余额: {new_account['free_balance']:.2f} USDT")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"❌ 订单执行失败: {e}")
        import traceback
        traceback.print_exc()


def analyze_with_deepseek_with_retry(price_data, max_retries=2):
    """带重试的DeepSeek分析"""
    for attempt in range(max_retries):
        try:
            signal_data = analyze_with_deepseek(price_data)
            if signal_data and not signal_data.get('is_fallback', False):
                return signal_data

            print(f"第{attempt + 1}次尝试失败，进行重试...")
            time.sleep(1)

        except Exception as e:
            print(f"第{attempt + 1}次尝试异常: {e}")
            if attempt == max_retries - 1:
                return create_fallback_signal(price_data)
            time.sleep(1)

    return create_fallback_signal(price_data)


def trading_bot():
    """主交易机器人函数"""
    print("\n" + "=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 获取增强版K线数据
    price_data = get_btc_ohlcv_enhanced()
    if not price_data:
        return

    print(f"{TRADE_CONFIG['symbol']} 当前价格: ${price_data['price']:,.2f}")
    print(f"数据周期: {TRADE_CONFIG['timeframe']}")
    print(f"价格变化: {price_data['price_change']:+.2f}%")

    # 2. 使用DeepSeek分析（带重试）
    signal_data = analyze_with_deepseek_with_retry(price_data)

    if signal_data.get('is_fallback', False):
        print("⚠️ 使用备用交易信号")

    # 3. 执行交易
    execute_trade(signal_data, price_data)


def main():
    """主函数"""
    print(f"{TRADE_CONFIG['symbol']} 币安自动交易机器人启动成功！")
    print("融合技术指标策略 Plus 增强版")

    if TRADE_CONFIG['test_mode']:
        print("当前为模拟模式，不会真实下单")
    else:
        print("🚨 实盘交易模式，请谨慎操作！")

    print(f"交易周期: {TRADE_CONFIG['timeframe']}")
    print("已启用完整技术指标分析和持仓跟踪功能")

    # 设置交易所
    if not setup_exchange():
        print("交易所初始化失败，程序退出")
        return

    # 根据时间周期设置执行频率
    if TRADE_CONFIG['timeframe'] == '1h':
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")
    elif TRADE_CONFIG['timeframe'] == '15m':
        schedule.every(15).minutes.do(trading_bot)
        print("执行频率: 每15分钟一次")
    else:
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")

    # 立即执行一次
    trading_bot()

    # 循环执行
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()

