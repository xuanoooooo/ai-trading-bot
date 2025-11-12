#!/usr/bin/env python3
"""测试止损记录功能"""

from portfolio_statistics import PortfolioStatistics
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 测试止损触发记录功能")
print("=" * 60)
print()

# 初始化统计模块
stats = PortfolioStatistics('portfolio_stats_test.json')

# 模拟记录一个止损触发
print("1️⃣ 模拟记录 BNB 空头止损触发...")
entry_time = datetime.now() - timedelta(minutes=5)
trigger_time = datetime.now()

stats.record_stop_loss_triggered(
    coin='BNB',
    side='short',
    entry_price=1117.65,
    stop_price=1120.0,
    amount=0.08,
    trigger_time=trigger_time,
    pnl=-1.88,
    entry_time=entry_time
)

print()
print("2️⃣ 再模拟一个 SOL 多头止损触发...")
entry_time2 = datetime.now() - timedelta(minutes=3)
trigger_time2 = datetime.now()

stats.record_stop_loss_triggered(
    coin='SOL',
    side='long',
    entry_price=195.08,
    stop_price=195.0,
    amount=0.3,
    trigger_time=trigger_time2,
    pnl=-0.02,
    entry_time=entry_time2
)

print()
print("=" * 60)
print("3️⃣ 查询最近30分钟的止损记录...")
print("=" * 60)
print()

recent = stats.get_recent_stop_losses(minutes=30)
print(f"找到 {len(recent)} 条止损记录：")
print()

for sl in recent:
    trigger_time_str = datetime.fromisoformat(sl['timestamp']).strftime('%H:%M:%S')
    print(f"- {sl['coin']} {sl['side'].upper()}仓")
    print(f"  开仓价: ${sl['entry_price']:.2f} → 止损价: ${sl['stop_price']:.2f}")
    print(f"  亏损: {sl['pnl']:.2f} USDC")
    print(f"  触发时间: {trigger_time_str} (开仓后{sl['duration_minutes']}分钟)")
    print()

print("=" * 60)
print("4️⃣ 测试过期清理（模拟8天前的记录）...")
print("=" * 60)
print()

old_time = datetime.now() - timedelta(days=8)
stats.record_stop_loss_triggered(
    coin='ETH',
    side='long',
    entry_price=4000.0,
    stop_price=3950.0,
    amount=0.01,
    trigger_time=old_time,
    pnl=-0.50,
    entry_time=old_time - timedelta(minutes=10)
)

print(f"保存前总记录数: {len(stats.stop_loss_history)}")
stats.save()  # 保存时会自动过滤7天外的记录

# 重新加载
stats2 = PortfolioStatistics('portfolio_stats_test.json')
print(f"重新加载后记录数: {len(stats2.stop_loss_history)}")
print("(8天前的ETH记录应该被过滤掉)")

print()
print("=" * 60)
print("✅ 测试完成！")
print("=" * 60)
print()
print("📝 测试文件：portfolio_stats_test.json (可以删除)")


