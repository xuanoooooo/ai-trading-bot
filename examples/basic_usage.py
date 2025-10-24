#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Usage Example
基础使用示例

Demonstrates how to use the basic features of the AI trading bot.
演示如何使用AI交易机器人的基本功能。

Author: AI Trading Bot
License: MIT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_env_vars, validate_api_keys, setup_logging
from src.indicators import calculate_all_indicators, get_technical_summary
import pandas as pd
import ccxt
from datetime import datetime, timedelta


def example_1_basic_setup():
    """
    Example 1: Basic setup and configuration verification
    示例1: 基本设置和配置验证
    """
    print("=" * 60)
    print("示例1: 基本设置和配置验证")
    print("=" * 60)
    
    # 加载环境变量
    env_vars = load_env_vars()
    print("环境变量加载完成")
    
    # 验证API密钥
    if validate_api_keys(env_vars):
        print("✅ API密钥配置正确")
    else:
        print("❌ API密钥配置有误")
        return False
    
    # 设置日志
    logger = setup_logging("example.log", "INFO")
    logger.info("示例程序启动")
    
    return True


def example_2_exchange_connection():
    """示例2: 交易所连接测试"""
    print("=" * 60)
    print("示例2: 交易所连接测试")
    print("=" * 60)
    
    try:
        # 创建交易所实例
        exchange = ccxt.binance({
            'options': {'defaultType': 'future'},
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET'),
        })
        
        # 测试连接
        print("测试币安API连接...")
        balance = exchange.fetch_balance()
        print(f"✅ 连接成功")
        print(f"USDT余额: {balance['USDT']['free']:.2f}")
        
        # 获取市场信息
        markets = exchange.load_markets()
        print(f"可用交易对数量: {len(markets)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def example_3_technical_indicators():
    """示例3: 技术指标计算"""
    print("=" * 60)
    print("示例3: 技术指标计算")
    print("=" * 60)
    
    try:
        # 创建示例数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='15T')
        prices = [100 + i * 0.1 + (i % 10 - 5) * 0.5 for i in range(100)]
        volumes = [1000 + i * 10 + (i % 7 - 3) * 100 for i in range(100)]
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + 0.5 for p in prices],
            'low': [p - 0.5 for p in prices],
            'close': prices,
            'volume': volumes
        })
        
        # 计算技术指标
        df = calculate_all_indicators(df)
        
        # 获取技术指标摘要
        summary = get_technical_summary(df)
        
        print("技术指标计算结果:")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 技术指标计算失败: {e}")
        return False


def example_4_market_data():
    """示例4: 获取市场数据"""
    print("=" * 60)
    print("示例4: 获取市场数据")
    print("=" * 60)
    
    try:
        # 创建交易所实例
        exchange = ccxt.binance({
            'options': {'defaultType': 'future'},
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET'),
        })
        
        # 获取K线数据
        symbol = 'BNB/USDT'
        timeframe = '15m'
        limit = 96
        
        print(f"获取 {symbol} {timeframe} K线数据...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # 转换为DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        print(f"✅ 获取到 {len(df)} 根K线数据")
        print(f"时间范围: {df['timestamp'].iloc[0]} 到 {df['timestamp'].iloc[-1]}")
        print(f"最新价格: ${df['close'].iloc[-1]:.2f}")
        
        # 计算技术指标
        df = calculate_all_indicators(df)
        
        # 显示最新指标
        latest = df.iloc[-1]
        print("\n最新技术指标:")
        print(f"  SMA20: {latest['sma_20']:.2f}")
        print(f"  RSI: {latest['rsi']:.2f}")
        print(f"  MACD: {latest['macd']:.4f}")
        print(f"  布林带位置: {latest['bb_position']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取市场数据失败: {e}")
        return False


def example_5_risk_management():
    """示例5: 风险管理演示"""
    print("=" * 60)
    print("示例5: 风险管理演示")
    print("=" * 60)
    
    # 模拟账户状态
    account_status = {
        'total_balance': 1000.0,
        'free_balance': 800.0,
        'used_margin': 200.0,
        'margin_ratio': 20.0,
        'position_value': 600.0,
        'unrealized_pnl': 50.0,
        'pnl_percent': 8.33,
        'has_position': True
    }
    
    print("模拟账户状态:")
    for key, value in account_status.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # 风险参数
    risk_params = {
        'max_position_percent': 80,
        'min_position_percent': 5,
        'force_reserve_percent': 20,
        'leverage': 3
    }
    
    print(f"\n风险参数:")
    for key, value in risk_params.items():
        print(f"  {key}: {value}")
    
    # 模拟AI决策
    ai_decisions = [
        {'signal': 'BUY', 'position_percent': 50, 'confidence': 'HIGH'},
        {'signal': 'SELL', 'position_percent': 30, 'confidence': 'MEDIUM'},
        {'signal': 'HOLD', 'position_percent': 0, 'confidence': 'LOW'}
    ]
    
    print(f"\nAI决策示例:")
    for i, decision in enumerate(ai_decisions, 1):
        print(f"  决策{i}: {decision}")
        
        # 计算实际仓位
        if decision['position_percent'] > 0:
            margin_needed = account_status['free_balance'] * (decision['position_percent'] / 100)
            position_value = margin_needed * risk_params['leverage']
            print(f"    保证金: {margin_needed:.2f} USDT")
            print(f"    仓位价值: {position_value:.2f} USDT")
        
        print()
    
    return True


def main():
    """主函数"""
    print("🚀 AI交易机器人基础使用示例")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv('BINANCE_API_KEY') or not os.getenv('BINANCE_SECRET'):
        print("❌ 请先配置API密钥")
        print("1. 复制 config/env.example 为 .env")
        print("2. 编辑 .env 文件，填入您的API密钥")
        return
    
    examples = [
        ("基本设置", example_1_basic_setup),
        ("交易所连接", example_2_exchange_connection),
        ("技术指标", example_3_technical_indicators),
        ("市场数据", example_4_market_data),
        ("风险管理", example_5_risk_management)
    ]
    
    success_count = 0
    total_count = len(examples)
    
    for name, func in examples:
        try:
            if func():
                success_count += 1
                print(f"✅ {name} 示例完成")
            else:
                print(f"❌ {name} 示例失败")
        except Exception as e:
            print(f"❌ {name} 示例异常: {e}")
        
        print()
    
    print("=" * 60)
    print(f"示例完成: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 所有示例运行成功！")
        print("\n下一步:")
        print("1. 查看完整文档: docs/")
        print("2. 启动交易机器人: ./scripts/start_trading.sh")
        print("3. 监控运行状态: ./scripts/start_trading.sh status")
    else:
        print("⚠️ 部分示例失败，请检查配置")
        print("\n故障排除:")
        print("1. 检查API密钥配置")
        print("2. 检查网络连接")
        print("3. 查看详细文档")


if __name__ == "__main__":
    main()
