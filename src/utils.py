#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions Module
工具函数模块

Provides common utility functions and helper features.
提供通用的工具函数和辅助功能。

Author: AI Trading Bot
License: MIT
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def setup_logging(log_file: str = "trading_bot.log", level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration
    设置日志配置
    """
    from logging.handlers import RotatingFileHandler
    
    # 创建logger
    logger = logging.getLogger('trading_bot')
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 文件处理器（自动轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config(config_file: str = "config/trading_config.json") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {config_file} 不存在")
        return {}
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return {}


def save_config(config: Dict[str, Any], config_file: str = "config/trading_config.json") -> bool:
    """保存配置文件"""
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False


def load_env_vars() -> Dict[str, str]:
    """加载环境变量"""
    load_dotenv()
    return {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY', ''),
        'BINANCE_API_KEY': os.getenv('BINANCE_API_KEY', ''),
        'BINANCE_SECRET': os.getenv('BINANCE_SECRET', ''),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'MAX_RETRIES': os.getenv('MAX_RETRIES', '3'),
        'REQUEST_TIMEOUT': os.getenv('REQUEST_TIMEOUT', '30')
    }


def validate_api_keys(env_vars: Dict[str, str]) -> bool:
    """验证API密钥"""
    required_keys = ['DEEPSEEK_API_KEY', 'BINANCE_API_KEY', 'BINANCE_SECRET']
    
    for key in required_keys:
        if not env_vars.get(key):
            print(f"❌ 缺少必需的API密钥: {key}")
            return False
    
    print("✅ 所有必需的API密钥都已配置")
    return True


def format_currency(amount: float, currency: str = "USDT") -> str:
    """格式化货币显示"""
    if currency == "USDT":
        return f"{amount:,.2f} {currency}"
    else:
        return f"{amount:.8f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """格式化百分比显示"""
    return f"{value:+.{decimals}f}%"


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """计算百分比变化"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100


def truncate_float(value: float, decimals: int) -> float:
    """截断浮点数到指定小数位"""
    multiplier = 10 ** decimals
    return int(value * multiplier) / multiplier


def is_valid_symbol(symbol: str) -> bool:
    """验证交易对格式"""
    if not symbol or '/' not in symbol:
        return False
    
    parts = symbol.split('/')
    if len(parts) != 2:
        return False
    
    base, quote = parts
    return len(base) > 0 and len(quote) > 0


def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_backup_filename(original_file: str) -> str:
    """创建备份文件名"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_file)
    return f"{name}_backup_{timestamp}{ext}"


def ensure_directory(directory: str) -> bool:
    """确保目录存在"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败 {directory}: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def clean_old_logs(log_directory: str, max_files: int = 10) -> None:
    """清理旧日志文件"""
    try:
        if not os.path.exists(log_directory):
            return
        
        log_files = []
        for file in os.listdir(log_directory):
            if file.endswith('.log'):
                file_path = os.path.join(log_directory, file)
                log_files.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序，保留最新的文件
        log_files.sort(key=lambda x: x[1], reverse=True)
        
        # 删除超出限制的旧文件
        for file_path, _ in log_files[max_files:]:
            try:
                os.remove(file_path)
                print(f"已删除旧日志文件: {file_path}")
            except OSError:
                pass
                
    except Exception as e:
        print(f"清理日志文件失败: {e}")


def validate_trading_config(config: Dict[str, Any]) -> bool:
    """验证交易配置"""
    required_fields = ['symbol', 'leverage', 'timeframe']
    
    for field in required_fields:
        if field not in config:
            print(f"❌ 缺少必需的配置字段: {field}")
            return False
    
    # 验证杠杆倍数
    leverage = config.get('leverage', 0)
    if not isinstance(leverage, (int, float)) or leverage <= 0:
        print("❌ 杠杆倍数必须大于0")
        return False
    
    # 验证交易对格式
    symbol = config.get('symbol', '')
    if not is_valid_symbol(symbol):
        print("❌ 交易对格式无效")
        return False
    
    print("✅ 交易配置验证通过")
    return True
