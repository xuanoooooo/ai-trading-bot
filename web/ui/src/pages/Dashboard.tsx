import React, { useEffect, useState } from 'react';

interface Position {
  symbol: string;
  amount: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
}

interface PortfolioStats {
  total_balance?: number; // This is now Total Equity (Real-time)
  total_pnl?: number;     // Historical Realized PnL
  total_unrealized_pnl?: number; // Real-time Unrealized PnL
  total_trades?: number;
  win_trades?: number;
  daily_pnl?: number;
}

interface AIDecision {
  timestamp: string;
  symbol: string;
  action: string;
  reason: string;
  confidence?: number;
}

const Dashboard: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [decisions, setDecisions] = useState<AIDecision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [positionsResponse, statsResponse, decisionsResponse] = await Promise.all([
          fetch('/api/positions'),
          fetch('/api/stats'),
          fetch('/api/ai_decisions'),
        ]);

        if (!positionsResponse.ok) throw new Error(`Positions API error! status: ${positionsResponse.status}`);
        if (!statsResponse.ok) throw new Error(`Stats API error! status: ${statsResponse.status}`);
        if (!decisionsResponse.ok) throw new Error(`Decisions API error! status: ${decisionsResponse.status}`);

        const positionsData = await positionsResponse.json();
        const statsData = await statsResponse.json();
        const decisionsData = await decisionsResponse.json();

        console.log('Positions Data:', positionsData);
        console.log('Stats Data:', statsData);
        console.log('Decisions Data:', decisionsData);

        setPositions(Array.isArray(positionsData.positions) ? positionsData.positions : []);
        setStats(statsData);

        let decisionsList: AIDecision[] = [];
        if (Array.isArray(decisionsData)) {
            decisionsList = decisionsData;
        } else if (decisionsData && Array.isArray(decisionsData.decisions)) {
            decisionsList = decisionsData.decisions;
        }

        // Map data fields if necessary and sort by time desc
        const formattedDecisions = decisionsList.map((d: any) => ({
            ...d,
            timestamp: d.timestamp || d.time, // Handle both 'timestamp' and 'time'
        })).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

        setDecisions(formattedDecisions);
      } catch (err: any) {
        console.error('Dashboard Error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <div className="p-4 text-center">加载数据中...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">错误: {error}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">交易概览</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">总资产权益</h2>
          <p className="text-3xl text-green-600 dark:text-green-400">
            {stats?.total_balance !== undefined ? `$${stats.total_balance.toFixed(2)}` : 'N/A'}
          </p>
          <p className="text-sm text-gray-500 mt-1">包含未实现盈亏</p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">当前浮动盈亏</h2>
          <p className={`text-3xl ${stats && (stats.total_unrealized_pnl || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {stats?.total_unrealized_pnl !== undefined ? `$${stats.total_unrealized_pnl.toFixed(2)}` : 'N/A'}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">历史总盈亏</h2>
          <p className={`text-3xl ${stats && (stats.total_pnl || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {stats?.total_pnl !== undefined ? `$${stats.total_pnl.toFixed(2)}` : 'N/A'}
          </p>
          <p className="text-sm text-gray-500 mt-1">已平仓收益</p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">历史胜率</h2>
          <p className="text-3xl text-blue-600 dark:text-blue-400">
            {stats && stats.total_trades && stats.total_trades > 0 
                ? `${((stats.win_trades || 0) / stats.total_trades * 100).toFixed(2)}%` 
                : 'N/A'}
          </p>
          <p className="text-sm text-gray-500 mt-1">总交易: {stats?.total_trades || 0} 笔</p>
        </div>
      </div>

      <h2 className="text-2xl font-bold mb-4">当前持仓</h2>
      {positions.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400 mb-8">暂无持仓。</p>
      ) : (
        <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow-md mb-8">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  币种
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  数量
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  入场价
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  当前价
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  未实现盈亏
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {positions.map((position) => (
                <tr key={position.symbol}>
                  <td className="px-6 py-4 whitespace-nowrap">{position.symbol}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{position.amount}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{position.entryPrice.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{position.currentPrice.toFixed(2)}</td>
                  <td className={`px-6 py-4 whitespace-nowrap ${position.pnl >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {position.pnl.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 className="text-2xl font-bold mb-4">AI 决策日志</h2>
      {decisions.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400">暂无 AI 决策记录。</p>
      ) : (
        <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  时间
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  币种
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  决策
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  理由
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {decisions.map((decision, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {new Date(decision.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                    {decision.symbol}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${
                    ['BUY', 'OPEN_LONG', 'LONG'].includes(decision.action) ? 'text-green-600 dark:text-green-400' : 
                    ['SELL', 'OPEN_SHORT', 'SHORT', 'CLOSE'].includes(decision.action) ? 'text-red-600 dark:text-red-400' : 
                    'text-gray-600 dark:text-gray-400'
                  }`}>
                    {decision.action === 'BUY' || decision.action === 'OPEN_LONG' ? '开多' : 
                     decision.action === 'OPEN_SHORT' ? '开空' :
                     decision.action === 'SELL' || decision.action === 'CLOSE' ? '平仓' : 
                     decision.action === 'HOLD' ? '持有' : 
                     decision.action === 'WAIT' ? '观望' : decision.action}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-md whitespace-normal">
                    {decision.reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Dashboard;