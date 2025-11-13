// AI交易机器人前端逻辑
// 每5秒自动刷新数据

const API_BASE = '';
let pnlChart = null;
let lastTradeCount = 0; // 记录上次的交易数量

// 格式化时间
function formatTime(isoString) {
    if (!isoString) return '--';
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化数字
function formatNumber(num, decimals = null) {
    if (num === undefined || num === null) return '--';
    
    // 如果没有指定小数位，自动检测
    if (decimals === null) {
        // 小于1的数字（如DOGE 0.19），保留5位小数
        if (Math.abs(num) < 1) {
            decimals = 5;
        }
        // 小于10的数字（如XRP 2.6），保留4位小数  
        else if (Math.abs(num) < 10) {
            decimals = 4;
        }
        // 其他情况保留2位小数
        else {
            decimals = 2;
        }
    }
    
    return Number(num).toFixed(decimals);
}

// 格式化盈亏
function formatPnl(pnl) {
    if (pnl === undefined || pnl === null) return '--';
    const formatted = formatNumber(pnl, 2);
    return pnl >= 0 ? `+${formatted}` : formatted;
}

// 更新最后更新时间
function updateLastUpdate() {
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('zh-CN');
}

// 获取并显示运行状态
async function fetchRuntime() {
    try {
        const response = await fetch(`${API_BASE}/api/runtime`);
        const data = await response.json();
        
        // 运行状态卡片（4个信息）
        document.getElementById('currentStartTime').textContent = data.current_start_time || '未运行';
        document.getElementById('currentRuntime').textContent = data.current_runtime || '--';
        document.getElementById('totalRuntime').textContent = data.total_runtime || '--';
        document.getElementById('currentTime').textContent = data.current_time || '--';
    } catch (error) {
        console.error('获取运行状态失败:', error);
    }
}

// 获取并显示统计数据
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        document.getElementById('totalTrades').textContent = data.total_trades || 0;
        document.getElementById('winRate').textContent = `${data.win_rate || 0}%`;
        
        const pnlElement = document.getElementById('totalPnl');
        const pnl = data.total_pnl || 0;
        pnlElement.textContent = `${formatPnl(pnl)} USDT`;
        pnlElement.className = `stat-value pnl ${pnl >= 0 ? 'positive' : 'negative'}`;
        
        updateLastUpdate();
    } catch (error) {
        console.error('获取统计数据失败:', error);
    }
}

// 获取并显示账户信息
async function fetchAccount() {
    try {
        const response = await fetch(`${API_BASE}/api/account`);
        if (response.ok) {
            const data = await response.json();

            document.getElementById('totalBalance').textContent = `${formatNumber(data.total_balance)} USDT`;
            document.getElementById('freeBalance').textContent = `${formatNumber(data.free_balance)} USDT`;
        }
    } catch (error) {
        console.error('获取账户信息失败:', error);
        document.getElementById('totalBalance').textContent = '--';
        document.getElementById('freeBalance').textContent = '--';
    }
}

// 获取并显示夏普比率
async function fetchSharpeRatio() {
    try {
        const response = await fetch(`${API_BASE}/api/sharpe_ratio`);
        if (response.ok) {
            const data = await response.json();

            document.getElementById('sharpeRatio').textContent = data.sharpe_ratio.toFixed(2);
            document.getElementById('riskLevel').textContent = data.risk_level;
            document.getElementById('maxPositions').textContent = data.max_positions;
            document.getElementById('confidenceThreshold').textContent = `${data.confidence_threshold}%`;

            // 根据风险等级设置颜色
            const riskElement = document.getElementById('riskLevel');
            if (data.risk_level === '积极') {
                riskElement.style.color = '#4caf50'; // 绿色
            } else if (data.risk_level === '冷静') {
                riskElement.style.color = '#f44336'; // 红色
            } else {
                riskElement.style.color = '#ffc107'; // 黄色（正常）
            }

            // 如果有备注，显示样本不足提示
            if (data.note) {
                document.getElementById('sharpeNote').textContent = `(${data.note})`;
                document.getElementById('sharpeNote').style.display = 'inline';
            } else {
                document.getElementById('sharpeNote').style.display = 'none';
            }
        }
    } catch (error) {
        console.error('获取夏普比率失败:', error);
        document.getElementById('sharpeRatio').textContent = '--';
        document.getElementById('riskLevel').textContent = '--';
        document.getElementById('maxPositions').textContent = '--';
        document.getElementById('confidenceThreshold').textContent = '--';
    }
}

// 获取并显示持仓
async function fetchPositions() {
    try {
        const response = await fetch(`${API_BASE}/api/positions`);
        const data = await response.json();
        
        const container = document.getElementById('positionsList');
        
        // 更新总浮盈浮亏
        if (data.total_unrealized_pnl !== undefined) {
            const unrealizedPnlElement = document.getElementById('totalUnrealizedPnl');
            const unrealizedPnl = data.total_unrealized_pnl || 0;
            unrealizedPnlElement.textContent = `${formatPnl(unrealizedPnl)} USDT`;
            unrealizedPnlElement.className = `stat-value pnl ${unrealizedPnl >= 0 ? 'positive' : 'negative'}`;
        }
        
        if (!data.positions || data.positions.length === 0) {
            container.innerHTML = '<div class="no-data">当前无持仓</div>';
            return;
        }
        
        let html = '';
        data.positions.forEach(pos => {
            const pnlClass = pos.pnl >= 0 ? 'positive' : 'negative';
            const roeClass = pos.roe >= 0 ? 'positive' : 'negative';

            // 格式化持仓时长
            let durationText = '--';
            if (pos.duration_minutes !== undefined && pos.duration_minutes >= 0) {
                const hours = Math.floor(pos.duration_minutes / 60);
                const minutes = pos.duration_minutes % 60;
                if (hours > 0) {
                    durationText = `${hours}小时${minutes}分钟`;
                } else {
                    durationText = `${minutes}分钟`;
                }
            }

            html += `
                <div class="position-item">
                    <div class="position-header">
                        <span class="position-coin">${pos.coin}</span>
                        <span class="position-side ${pos.side}">${pos.side.toUpperCase()}</span>
                    </div>
                    <div class="position-details">
                        <div>开仓价: $${formatNumber(pos.entry_price)}</div>
                        <div>数量: ${pos.amount}</div>
                        ${pos.leverage ? `<div>杠杆: ${pos.leverage}x</div>` : ''}
                        <div>当前价: $${formatNumber(pos.current_price)}</div>
                        <div>开仓时间: ${formatTime(pos.entry_time)}</div>
                        <div>持仓时长: ${durationText}</div>
                        ${pos.stop_loss > 0 ? `<div style="color: #f44336;">止损: $${formatNumber(pos.stop_loss)} ${pos.stop_order_id > 0 ? '✅' : ''}</div>` : ''}
                        ${pos.take_profit > 0 ? `<div style="color: #4caf50;">止盈: $${formatNumber(pos.take_profit)}</div>` : ''}
                    </div>
                    <div class="position-pnl ${pnlClass}">
                        浮盈浮亏: ${formatPnl(pos.pnl)} USDT
                    </div>
                    <div class="position-roe ${roeClass}">
                        保证金回报(ROE): ${formatPnl(pos.roe)}%
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('获取持仓失败:', error);
        document.getElementById('positionsList').innerHTML = '<div class="no-data">加载失败</div>';
    }
}

// 获取并显示AI决策
async function fetchAIDecisions() {
    try {
        const response = await fetch(`${API_BASE}/api/ai_decisions`);
        const data = await response.json();
        
        const container = document.getElementById('decisionsList');
        
        if (!data.decisions || data.decisions.length === 0) {
            container.innerHTML = '<div class="no-data">暂无AI决策记录</div>';
            return;
        }
        
        let html = '';
        data.decisions.forEach(decision => {
            html += `
                <div class="decision-item">
                    <div class="decision-header">
                        <span class="decision-action ${decision.action}">${decision.coin} - ${decision.action}</span>
                        <span class="decision-time">${formatTime(decision.time)}</span>
                    </div>
                    <div class="decision-reason">${decision.reason || '无理由说明'}</div>
                    <div class="decision-meta">
                        <span>策略: ${decision.strategy || '--'}</span>
                        <span>风险: ${decision.risk_level || '--'}</span>
                        <span>信心: ${decision.confidence || '--'}</span>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('获取AI决策失败:', error);
        document.getElementById('decisionsList').innerHTML = '<div class="no-data">加载失败</div>';
    }
}

// 获取并显示交易历史
async function fetchTrades() {
    try {
        const response = await fetch(`${API_BASE}/api/trades`);
        const data = await response.json();
        
        const container = document.getElementById('tradesTable');
        
        if (!data.trades || data.trades.length === 0) {
            container.innerHTML = '<div class="no-data">暂无交易历史</div>';
            return;
        }
        
        // 交易历史表格只显示最近15笔
        const recentTrades = data.trades.slice(0, 15);
        
        let html = `
            <div class="trade-item trade-header">
                <div>币种</div>
                <div>方向</div>
                <div>开仓价</div>
                <div>平仓价</div>
                <div>数量</div>
                <div>盈亏</div>
                <div>持续(分钟)</div>
            </div>
        `;
        
        recentTrades.forEach(trade => {
            const pnlClass = trade.pnl >= 0 ? 'positive' : 'negative';
            html += `
                <div class="trade-item">
                    <div class="trade-coin">${trade.coin}</div>
                    <div class="trade-side ${trade.side}">${trade.side.toUpperCase()}</div>
                    <div>$${formatNumber(trade.entry_price)}</div>
                    <div>$${formatNumber(trade.exit_price)}</div>
                    <div>${trade.amount}</div>
                    <div class="trade-pnl ${pnlClass}">${formatPnl(trade.pnl)} USDT</div>
                    <div>${trade.duration_minutes || '--'}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // 只在交易数量变化时更新盈亏曲线，避免频繁闪烁
        if (data.trades.length !== lastTradeCount) {
            lastTradeCount = data.trades.length;
            updatePnlChart(data.trades);
        }
    } catch (error) {
        console.error('获取交易历史失败:', error);
        document.getElementById('tradesTable').innerHTML = '<div class="no-data">加载失败</div>';
    }
}

// 获取并显示实时价格
async function fetchPrices() {
    try {
        const response = await fetch(`${API_BASE}/api/prices`);
        if (!response.ok) {
            throw new Error('无法获取价格');
        }
        
        const data = await response.json();
        const container = document.querySelector('.ticker-content');
        
        if (!data.prices || Object.keys(data.prices).length === 0) {
            container.innerHTML = '<span class="ticker-loading">价格数据不可用</span>';
            return;
        }
        
        let html = '';
        Object.values(data.prices).forEach(coin => {
            html += `
                <div class="ticker-item">
                    <span class="ticker-symbol">${coin.symbol}</span>
                    <span class="ticker-price">$${formatNumber(coin.price)}</span>
                </div>
            `;
        });
        
        // 固定显示，不复制
        container.innerHTML = html;
    } catch (error) {
        console.error('获取价格失败:', error);
        document.querySelector('.ticker-content').innerHTML = '<span class="ticker-loading">价格数据不可用</span>';
    }
}

// 更新盈亏曲线图
function updatePnlChart(trades) {
    const ctx = document.getElementById('pnlChart');
    if (!ctx) {
        console.error('找不到pnlChart canvas元素');
        return;
    }
    
    try {
        console.log(`开始更新盈亏曲线，交易数量: ${trades.length}`);
        
        // 交易数据是倒序的（最新在前），需要反转为正序（最早在前）
        const sortedTrades = [...trades].reverse();
        
        // 计算累计盈亏
        let cumulativePnl = 0;
        const chartData = [];
        
        // 添加起点 (累计盈亏从0开始)
        chartData.push({ y: 0 });
        
        sortedTrades.forEach(trade => {
            cumulativePnl += trade.pnl || 0;
            chartData.push({ y: cumulativePnl });
        });
        
        console.log(`图表数据点数量: ${chartData.length}`);
    
        // 销毁旧图表
        if (pnlChart) {
            pnlChart.destroy();
        }
        
        // 创建新图表
        const labels = ['起点', ...sortedTrades.map((trade, index) => {
            const date = new Date(trade.exit_time);
            return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
        })];
        
        const pnlValues = chartData.map(d => d.y);
        
        pnlChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '累计盈亏 (USDT)',
                    data: pnlValues,
                    borderColor: '#00ff41',
                    backgroundColor: 'rgba(0, 255, 65, 0.2)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#00ff41',
                    pointBorderColor: '#0a1929',
                    pointBorderWidth: 2,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0 // 禁用动画，避免闪烁
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#00ff41',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#00ff41',
                        bodyColor: '#fff',
                        borderColor: '#00ff41',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '交易时间',
                            color: '#00ff41',
                            font: {
                                size: 12
                            }
                        },
                        ticks: {
                            color: '#00ff41',
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 255, 65, 0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '累计盈亏 (USDT)',
                            color: '#00ff41',
                            font: {
                                size: 12
                            }
                        },
                        ticks: {
                            color: '#00ff41',
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 255, 65, 0.1)'
                        }
                    }
                }
            }
        });
        
        console.log('✅ 盈亏曲线创建成功');
    } catch (error) {
        console.error('❌ 更新盈亏曲线失败:', error);
        console.error('错误详情:', error.message);
        console.error('错误堆栈:', error.stack);
        // 图表失败不影响交易历史显示
    }
}

// 刷新所有数据
async function refreshAll() {
    await Promise.all([
        fetchRuntime(),
        fetchStats(),
        fetchAccount(),
        fetchSharpeRatio(),
        fetchPositions(),
        fetchAIDecisions(),
        fetchTrades(),
        fetchPrices()
    ]);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AI交易机器人监控系统已启动');
    
    // 立即加载一次数据
    refreshAll();
    
    // 每10秒刷新一次
    setInterval(refreshAll, 10000);
    
    // 每10秒刷新一次价格
    setInterval(fetchPrices, 10000);
});

