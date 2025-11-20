#!/bin/bash

# 清理AI历史记录脚本 - 让AI从零开始
# 用途：删除所有历史决策、交易统计、运行时状态，重置系统

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  AI历史记录清理工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  此操作将删除以下文件："
echo "   - data/ai_decisions.json       (AI决策历史)"
echo "   - data/portfolio_stats.json    (持仓和交易统计)"
echo "   - data/current_runtime.json    (运行时状态)"
echo "   - portfolio_manager.log       (程序日志)"
echo ""
echo "📦 删除前会自动备份到 backups/ 目录"
echo ""

# 确认操作
read -p "是否继续？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 操作已取消"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  停止所有运行中的程序"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 停止交易程序
if pgrep -f "portfolio_manager.py" > /dev/null; then
    echo "🛑 停止交易程序..."
    pkill -f portfolio_manager.py
    sleep 2
    echo "✅ 交易程序已停止"
else
    echo "ℹ️  交易程序未运行"
fi

# 停止看板
if pgrep -f "web_app.py" > /dev/null; then
    echo "🛑 停止可视化看板..."
    pkill -f web_app.py
    sleep 1
    echo "✅ 看板已停止"
else
    echo "ℹ️  看板未运行"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  备份现有记录"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 创建备份目录
BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📁 备份目录: $BACKUP_DIR"

# 备份文件列表
FILES_TO_BACKUP=(
    "data/ai_decisions.json"
    "data/portfolio_stats.json"
    "data/current_runtime.json"
    "portfolio_manager.log"
)

BACKUP_COUNT=0
for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        # 确保备份目录有对应结构
        if [[ "$file" == data/* ]]; then
            mkdir -p "$BACKUP_DIR/data"
            cp "$file" "$BACKUP_DIR/$file"
        else
            cp "$file" "$BACKUP_DIR/"
        fi
        echo "   ✅ 已备份: $file"
        ((BACKUP_COUNT++))
    fi
done

if [ $BACKUP_COUNT -eq 0 ]; then
    echo "   ℹ️  没有文件需要备份（全新系统）"
    rmdir "$BACKUP_DIR"
    rmdir "backups" 2>/dev/null
else
    echo ""
    echo "📦 已备份 $BACKUP_COUNT 个文件到: $BACKUP_DIR"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  删除历史记录文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DELETE_COUNT=0
for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "   🗑️  已删除: $file"
        ((DELETE_COUNT++))
    fi
done

if [ $DELETE_COUNT -eq 0 ]; then
    echo "   ℹ️  没有文件需要删除"
else
    echo ""
    echo "✅ 已删除 $DELETE_COUNT 个历史记录文件"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  检查币安账户持仓"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  重要提醒："
echo "   请确认币安账户没有未平仓的持仓！"
echo "   如果有持仓，请先手动平仓或使用程序平仓。"
echo ""
echo "💡 启动程序后，系统会自动同步币安持仓状态"
echo ""

read -p "确认币安账户已清空？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚠️  请先清空币安持仓，然后重新运行此脚本"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 清理完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 操作摘要："
echo "   - 已停止所有运行程序"
if [ $BACKUP_COUNT -gt 0 ]; then
    echo "   - 已备份 $BACKUP_COUNT 个文件到: $BACKUP_DIR"
fi
echo "   - 已删除 $DELETE_COUNT 个历史记录文件"
echo "   - 系统已重置，AI将从零开始"
echo ""
echo "🚀 下一步："
echo "   启动程序: ./start_portfolio.sh"
echo "   查看日志: tmux attach -t portfolio"
echo ""
echo "💾 备份位置: $BACKUP_DIR"
echo "   如需恢复数据，可从备份目录复制文件"
echo ""

# 询问是否立即启动
read -p "是否立即启动交易程序？[y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 正在启动交易程序..."
    ./start_portfolio.sh
    echo ""
    echo "✅ 程序已启动！"
    echo "📊 查看运行状态: tmux attach -t portfolio"
    echo "📈 启动可视化看板: cd web && ./start_web.sh"
else
    echo ""
    echo "ℹ️  稍后可手动启动: ./scripts/start_portfolio.sh"
fi

echo ""
