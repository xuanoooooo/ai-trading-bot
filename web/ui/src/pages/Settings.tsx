import React, { useEffect, useState } from 'react';

interface CoinConfig {
  symbol: string;
  binance_symbol: string;
  precision: number;
  price_precision: number;
  min_order_value: number;
}

interface PortfolioRules {
  leverage: number;
  min_cash_reserve_percent: number;
  check_interval_minutes: number;
}

interface Config {
  coins: CoinConfig[];
  portfolio_rules: PortfolioRules;
}

const Settings: React.FC = () => {
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Prompts state
  const [promptFiles, setPromptFiles] = useState<string[]>([]);
  const [selectedPromptFile, setSelectedPromptFile] = useState<string>('');
  const [promptContent, setPromptContent] = useState<string>('');
  const [newPromptName, setNewPromptName] = useState<string>('');
  const [isCreatingNewPrompt, setIsCreatingNewPrompt] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [configRes, promptsRes] = await Promise.all([
          fetch('/api/config'),
          fetch('/api/prompts/list')
        ]);

        if (!configRes.ok) throw new Error(`Config error: ${configRes.status}`);
        if (!promptsRes.ok) throw new Error(`Prompts error: ${promptsRes.status}`);

        const configData: Config = await configRes.json();
        const promptsData = await promptsRes.json();

        setConfig(configData);
        setPromptFiles(promptsData.files || []);
        
        // Select default.txt if available, otherwise first file
        if (promptsData.files && promptsData.files.includes('default.txt')) {
            setSelectedPromptFile('default.txt');
        } else if (promptsData.files && promptsData.files.length > 0) {
            setSelectedPromptFile(promptsData.files[0]);
        }

      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Fetch prompt content when selection changes
  useEffect(() => {
    if (!selectedPromptFile) return;
    
    const fetchContent = async () => {
        try {
            const res = await fetch(`/api/prompts/content?file=${selectedPromptFile}`);
            if (!res.ok) throw new Error('Failed to load prompt content');
            const data = await res.json();
            setPromptContent(data.content);
        } catch (err: any) {
            setError(err.message);
        }
    };
    fetchContent();
  }, [selectedPromptFile]);


  const handlePortfolioRulesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (config) {
      setConfig({
        ...config,
        portfolio_rules: {
          ...config.portfolio_rules,
          [e.target.name]: parseFloat(e.target.value),
        },
      });
    }
  };

  const handleCoinChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (config) {
      const newCoins = [...config.coins];
      newCoins[index] = {
        ...newCoins[index],
        [e.target.name]:
          e.target.name === 'symbol' || e.target.name === 'binance_symbol'
            ? e.target.value
            : parseFloat(e.target.value),
      };
      setConfig({ ...config, coins: newCoins });
    }
  };

  const handleAddCoin = () => {
    if (config) {
      setConfig({
        ...config,
        coins: [
          ...config.coins,
          {
            symbol: '',
            binance_symbol: '',
            precision: 0,
            price_precision: 0,
            min_order_value: 0,
          },
        ],
      });
    }
  };

  const handleRemoveCoin = (index: number) => {
    if (config) {
      const newCoins = config.coins.filter((_, i) => i !== index);
      setConfig({ ...config, coins: newCoins });
    }
  };

  const handleSubmitConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    if (!config) return;

    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const result = await response.json();
      setMessage(result.message || '配置已成功更新！');
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Prompt Handlers
  const handleSavePrompt = async () => {
    setMessage(null);
    try {
        const filename = isCreatingNewPrompt ? newPromptName : selectedPromptFile;
        if (!filename) return;

        const response = await fetch('/api/prompts/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, content: promptContent }),
        });

        if (!response.ok) throw new Error('Failed to save prompt');
        
        const result = await response.json();
        setMessage(result.message);
        
        if (isCreatingNewPrompt) {
            setPromptFiles([...promptFiles, filename.endsWith('.txt') ? filename : `${filename}.txt`]);
            setSelectedPromptFile(filename.endsWith('.txt') ? filename : `${filename}.txt`);
            setIsCreatingNewPrompt(false);
            setNewPromptName('');
        }

    } catch (err: any) {
        setError(err.message);
    }
  };

  const handleActivatePrompt = async () => {
    setMessage(null);
    try {
        const response = await fetch('/api/prompts/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: selectedPromptFile }),
        });

        if (!response.ok) throw new Error('Failed to activate prompt');
        
        const result = await response.json();
        setMessage(result.message);
    } catch (err: any) {
        setError(err.message);
    }
  };


  if (loading) return <div className="p-4 text-center">正在加载配置...</div>;
  if (error) return <div className="p-4 text-center text-red-500">错误: {error}</div>;
  if (!config) return <div className="p-4 text-center">暂无配置数据。</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">系统设置</h1>
      {message && (
        <div className="bg-green-100 text-green-800 p-3 rounded-md mb-4 dark:bg-green-800 dark:text-green-100">
          {message}
        </div>
      )}
      
      {/* Config Form */}
      <form onSubmit={handleSubmitConfig} className="space-y-8 mb-12">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">投资风控规则</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="leverage" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                杠杆倍数 (Leverage)
              </label>
              <input
                type="number"
                id="leverage"
                name="leverage"
                value={config.portfolio_rules.leverage}
                onChange={handlePortfolioRulesChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
            </div>
            <div>
              <label htmlFor="min_cash_reserve_percent" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                最低现金保留比例 (%)
              </label>
              <input
                type="number"
                id="min_cash_reserve_percent"
                name="min_cash_reserve_percent"
                value={config.portfolio_rules.min_cash_reserve_percent}
                onChange={handlePortfolioRulesChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
            </div>
            <div>
              <label htmlFor="check_interval_minutes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                检查间隔 (分钟)
              </label>
              <input
                type="number"
                id="check_interval_minutes"
                name="check_interval_minutes"
                value={config.portfolio_rules.check_interval_minutes}
                onChange={handlePortfolioRulesChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">交易币种配置</h2>
          <div className="space-y-4">
            {config.coins.map((coin, index) => (
              <div key={index} className="border p-4 rounded-md dark:border-gray-700 relative">
                <h3 className="text-lg font-medium mb-2">币种: {coin.symbol || `新币种 ${index + 1}`}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">代币符号</label>
                    <input type="text" name="symbol" value={coin.symbol} onChange={(e) => handleCoinChange(index, e)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">币安交易对</label>
                    <input type="text" name="binance_symbol" value={coin.binance_symbol} onChange={(e) => handleCoinChange(index, e)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">数量精度 (小数点后几位)</label>
                    <input type="number" name="precision" value={coin.precision} onChange={(e) => handleCoinChange(index, e)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">价格精度 (小数点后几位)</label>
                    <input type="number" name="price_precision" value={coin.price_precision} onChange={(e) => handleCoinChange(index, e)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">最小下单金额</label>
                    <input type="number" name="min_order_value" value={coin.min_order_value} onChange={(e) => handleCoinChange(index, e)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100" />
                  </div>
                </div>
                <button type="button" onClick={() => handleRemoveCoin(index)} className="absolute top-2 right-2 p-1 rounded-full bg-red-500 text-white hover:bg-red-600">&times;</button>
              </div>
            ))}
            <button type="button" onClick={handleAddCoin} className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">添加币种</button>
          </div>
        </div>

        <button type="submit" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">保存配置修改</button>
      </form>

      {/* Prompts Management Section */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">AI 提示词 (Prompts) 管理</h2>
        <div className="mb-4 flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">选择提示词文件</label>
                {isCreatingNewPrompt ? (
                    <div className="flex gap-2">
                        <input 
                            type="text" 
                            placeholder="输入新文件名 (e.g. strategy_v2)" 
                            value={newPromptName}
                            onChange={(e) => setNewPromptName(e.target.value)}
                            className="flex-1 rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                        />
                        <button 
                            onClick={() => setIsCreatingNewPrompt(false)}
                            className="px-3 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                        >
                            取消
                        </button>
                    </div>
                ) : (
                    <select 
                        value={selectedPromptFile} 
                        onChange={(e) => setSelectedPromptFile(e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                    >
                        {promptFiles.map(file => (
                            <option key={file} value={file}>{file}</option>
                        ))}
                    </select>
                )}
            </div>
            {!isCreatingNewPrompt && (
                <button 
                    onClick={() => { setIsCreatingNewPrompt(true); setPromptContent(''); }}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                    新建提示词
                </button>
            )}
        </div>

        <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">提示词内容</label>
            <textarea
                value={promptContent}
                onChange={(e) => setPromptContent(e.target.value)}
                rows={15}
                className="block w-full rounded-md border-gray-300 shadow-sm font-mono text-sm dark:bg-gray-900 dark:border-gray-600 dark:text-gray-100"
            />
        </div>

        <div className="flex gap-4">
            <button 
                onClick={handleSavePrompt}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
                保存提示词
            </button>
            {!isCreatingNewPrompt && (
                <button 
                    onClick={handleActivatePrompt}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    title="将此文件内容覆盖到 default.txt，使其立即生效"
                >
                    载入此提示词 (激活)
                </button>
            )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
