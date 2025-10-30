#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Statistics Module - Track trading history and performance
交易统计模块 - 跟踪交易历史和性能

Simplified version for single coin trading (BNB)
单币种交易的简化版本（BNB）

Author: AI Trading Bot
License: MIT
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional


class TradingStatistics:
    """交易统计类 - 管理单币种交易历史和性能指标"""
    
    def __init__(self, stats_file='trading_stats.json'):
        self.stats_file = stats_file
        self.start_time = None
        self.total_trades = 0
        self.win_trades = 0
        self.lose_trades = 0
        self.total_pnl = 0.0
        self.current_position = None
        self.trade_history = []  # 所有交易历史
        
        self.load()
    
    def load(self):
        """从文件加载统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.start_time = datetime.fromisoformat(data.get('start_time', datetime.now().isoformat()))
                    self.trade_history = data.get('trade_history', [])
                    self.total_trades = data.get('total_trades', 0)
                    self.win_trades = data.get('win_trades', 0)
                    self.lose_trades = data.get('lose_trades', 0)
                    self.total_pnl = data.get('total_pnl', 0.0)
                    self.current_position = data.get('current_position', None)
                    
                print(f"✅ 加载交易统计数据成功: {len(self.trade_history)}笔历史交易")
            except Exception as e:
                print(f"⚠️ 加载统计数据失败: {e}，将创建新的统计文件")
                self._initialize_new()
        else:
            self._initialize_new()
    
    def _initialize_new(self):
        """初始化新的统计数据"""
        self.start_time = datetime.now()
        self.trade_history = []
        self.total_trades = 0
        self.win_trades = 0
        self.lose_trades = 0
        self.total_pnl = 0.0
        self.current_position = None
        self.save()
        print(f"✅ 初始化新的交易统计数据，启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def save(self):
        """保存统计数据到文件"""
        try:
            data = {
                'start_time': self.start_time.isoformat(),
                'trade_history': self.trade_history[-200:],  # 保留最近200笔
                'total_trades': self.total_trades,
                'win_trades': self.win_trades,
                'lose_trades': self.lose_trades,
                'total_pnl': self.total_pnl,
                'current_position': self.current_position,
                'last_update': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存统计数据失败: {e}")
    
    def record_position_entry(self, side: str, entry_price: float, amount: float, signal_data: Dict = None):
        """记录开仓信息
        
        Args:
            side: 'BUY' or 'SELL'
            entry_price: 入场价格
            amount: 数量
            signal_data: AI信号数据（包含reason, confidence等）
        """
        self.current_position = {
            'entry_time': datetime.now().isoformat(),
            'side': side,
            'entry_price': entry_price,
            'amount': amount,
            'signal_data': signal_data or {}
        }
        self.save()
        print(f"📝 记录开仓: {side} @ ${entry_price:.2f} x {amount:.4f}")
    
    def record_position_exit(self, exit_price: float, amount: float, signal_data: Dict = None):
        """记录平仓信息并计算盈亏
        
        Args:
            exit_price: 出场价格
            amount: 数量
            signal_data: AI信号数据（包含reason, confidence等）
        """
        if not self.current_position:
            print("⚠️ 没有持仓记录，无法记录平仓")
            return
        
        entry_price = self.current_position['entry_price']
        side = self.current_position['side']
        
        # 计算盈亏
        if side == 'BUY':
            pnl = (exit_price - entry_price) * amount
        else:  # SELL
            pnl = (entry_price - exit_price) * amount
        
        pnl_percent = (pnl / (entry_price * amount)) * 100
        
        # 记录交易
        trade_record = {
            'entry_time': self.current_position['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': amount,
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2),
            'entry_signal': self.current_position.get('signal_data', {}),
            'exit_signal': signal_data or {}
        }
        
        self.trade_history.append(trade_record)
        self.total_trades += 1
        self.total_pnl += pnl
        
        if pnl > 0:
            self.win_trades += 1
            result = "✅ 盈利"
        else:
            self.lose_trades += 1
            result = "❌ 亏损"
        
        print(f"📝 记录平仓: {side} @ ${exit_price:.2f} | 盈亏: {pnl:+.2f} USDT ({pnl_percent:+.2f}%) {result}")
        
        # 清除持仓
        self.current_position = None
        self.save()
    
    def get_runtime_minutes(self) -> int:
        """获取运行时长（分钟）"""
        if not self.start_time:
            return 0
        elapsed = datetime.now() - self.start_time
        return int(elapsed.total_seconds() / 60)
    
    def get_win_rate(self) -> float:
        """获取胜率"""
        if self.total_trades == 0:
            return 0.0
        return (self.win_trades / self.total_trades) * 100
    
    def generate_stats_text(self) -> str:
        """生成统计信息文本（用于日志显示）"""
        runtime_minutes = self.get_runtime_minutes()
        runtime_hours = runtime_minutes / 60
        win_rate = self.get_win_rate()
        
        text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【交易统计】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
运行时长: {runtime_hours:.1f}小时 ({runtime_minutes}分钟)
总交易: {self.total_trades}笔
盈利交易: {self.win_trades}笔
亏损交易: {self.lose_trades}笔
胜率: {win_rate:.1f}%
总盈亏: {self.total_pnl:+.2f} USDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return text
    
    def generate_stats_text_for_ai(self) -> str:
        """生成给AI看的统计信息（简洁版）"""
        runtime_minutes = self.get_runtime_minutes()
        runtime_hours = runtime_minutes / 60
        win_rate = self.get_win_rate()
        
        text = f"""【历史表现】
- 运行时长: {runtime_hours:.1f}小时
- 总交易: {self.total_trades}笔 | 胜率: {win_rate:.1f}% ({self.win_trades}胜/{self.lose_trades}负)
- 总盈亏: {self.total_pnl:+.2f} USDT"""
        
        # 添加最近3笔交易
        if self.trade_history:
            text += "\n\n【最近3笔交易】"
            for trade in self.trade_history[-3:]:
                side = trade['side']
                pnl = trade['pnl']
                pnl_percent = trade['pnl_percent']
                entry_reason = trade.get('entry_signal', {}).get('reason', 'N/A')
                text += f"\n- {side}: {pnl:+.2f} USDT ({pnl_percent:+.2f}%) | 理由: {entry_reason}"
        
        return text

