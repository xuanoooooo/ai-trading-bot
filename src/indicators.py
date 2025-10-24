#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technical Indicators Calculation Module
技术指标计算模块

Provides various technical analysis indicator calculation functions.
提供各种技术分析指标的计算功能。

Author: AI Trading Bot
License: MIT
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    计算简单移动平均线
    """
    return data.rolling(window=period, min_periods=1).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    计算指数移动平均线
    """
    return data.ewm(span=period).mean()


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """
    Calculate MACD indicator
    计算MACD指标
    """
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """计算相对强弱指数(RSI)"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
    """计算布林带"""
    middle = calculate_sma(data, period)
    std = data.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    position = (data - lower) / (upper - lower)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower,
        'position': position
    }


def calculate_volume_indicators(volume: pd.Series, period: int = 20) -> Dict[str, pd.Series]:
    """计算成交量指标"""
    volume_ma = calculate_sma(volume, period)
    volume_ratio = volume / volume_ma
    
    return {
        'volume_ma': volume_ma,
        'volume_ratio': volume_ratio
    }


def calculate_support_resistance(high: pd.Series, low: pd.Series, period: int = 20) -> Dict[str, float]:
    """计算支撑阻力位"""
    resistance = high.rolling(window=period).max()
    support = low.rolling(window=period).min()
    
    return {
        'resistance': resistance.iloc[-1] if not resistance.empty else 0,
        'support': support.iloc[-1] if not support.empty else 0
    }


def calculate_momentum(data: pd.Series, period: int = 5) -> float:
    """计算价格动量"""
    if len(data) < period:
        return 0
    return data.pct_change().tail(period).mean() * 100


def get_price_position_analysis(price: float, sma_20: float, sma_50: float) -> Dict[str, float]:
    """获取价格与均线的位置关系"""
    return {
        'price_vs_sma20': ((price - sma_20) / sma_20) * 100 if sma_20 > 0 else 0,
        'price_vs_sma50': ((price - sma_50) / sma_50) * 100 if sma_50 > 0 else 0
    }


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算所有技术指标"""
    try:
        # 移动平均线
        df['sma_5'] = calculate_sma(df['close'], 5)
        df['sma_20'] = calculate_sma(df['close'], 20)
        df['sma_50'] = calculate_sma(df['close'], 50)
        
        # 指数移动平均线
        df['ema_12'] = calculate_ema(df['close'], 12)
        df['ema_26'] = calculate_ema(df['close'], 26)
        
        # MACD
        macd_data = calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # RSI
        df['rsi'] = calculate_rsi(df['close'])
        
        # 布林带
        bb_data = calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        df['bb_position'] = bb_data['position']
        
        # 成交量指标
        volume_data = calculate_volume_indicators(df['volume'])
        df['volume_ma'] = volume_data['volume_ma']
        df['volume_ratio'] = volume_data['volume_ratio']
        
        # 支撑阻力
        df['resistance'] = df['high'].rolling(20).max()
        df['support'] = df['low'].rolling(20).min()
        
        # 填充NaN值
        df = df.bfill().ffill()
        
        return df
        
    except Exception as e:
        print(f"技术指标计算失败: {e}")
        return df


def get_technical_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """获取技术指标摘要"""
    if df.empty:
        return {}
    
    current = df.iloc[-1]
    
    return {
        'price': current['close'],
        'sma_5': current.get('sma_5', 0),
        'sma_20': current.get('sma_20', 0),
        'sma_50': current.get('sma_50', 0),
        'rsi': current.get('rsi', 0),
        'macd': current.get('macd', 0),
        'macd_signal': current.get('macd_signal', 0),
        'bb_upper': current.get('bb_upper', 0),
        'bb_lower': current.get('bb_lower', 0),
        'bb_position': current.get('bb_position', 0),
        'volume_ratio': current.get('volume_ratio', 0),
        'resistance': current.get('resistance', 0),
        'support': current.get('support', 0)
    }
