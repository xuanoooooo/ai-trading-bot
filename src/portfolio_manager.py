"""
投资组合管理器 - AI驱动的多币种交易系统
"""
import os
import time
import schedule
from openai import OpenAI
from datetime import datetime, timedelta
import json
import re
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from binance.client import Client
from binance.exceptions import BinanceAPIException
import math

from portfolio_statistics import PortfolioStatistics
from market_scanner import MarketScanner

# 加载环境变量（明确指定路径）
load_dotenv()

# 记录程序启动时间和调用次数
PROGRAM_START_TIME = datetime.now()
INVOCATION_COUNT = 0
RUNTIME_FILE = 'current_runtime.json'  # 保存当前运行状态

# 配置日志
log_handler = RotatingFileHandler(
    'portfolio_manager.log',
    maxBytes=10*1024*1024,
    backupCount=3,
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, console_handler]
)

def print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    logging.info(message)

def format_price(price, coin):
    """根据币种格式化价格，低价币种显示更多小数位"""
    if coin in ['DOGE', 'XRP']:
        return f"${price:.4f}"
    else:
        return f"${price:.2f}"

# 加载AI配置
def load_ai_config():
    """加载AI配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'coins_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('ai_config', {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'api_base': 'https://api.deepseek.com',
                'api_key_env': 'DEEPSEEK_API_KEY',
                'temperature': 0.7,
                'max_tokens': 8000
            })
    except Exception as e:
        print(f"⚠️ 加载AI配置失败，使用默认配置: {e}")
        return {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_base': 'https://api.deepseek.com',
            'api_key_env': 'DEEPSEEK_API_KEY',
            'temperature': 0.7,
            'max_tokens': 8000
        }

def init_ai_client(config):
    """初始化AI客户端，支持自动fallback"""
    # 优先使用配置中指定的API Key
    primary_key_env = config['api_key_env']
    primary_key = os.getenv(primary_key_env)
    
    if primary_key:
        print(f"🤖 AI配置: {config['provider']} - {config['model']}")
        print(f"   使用API Key: {primary_key_env}")
        return OpenAI(
            api_key=primary_key,
            base_url=config['api_base']
        )
    
    # Fallback：自动检测可用的API Key
    print(f"⚠️  未找到 {primary_key_env}，尝试自动检测其他可用API Key...")
    
    fallback_configs = [
        ('DEEPSEEK_API_KEY', 'deepseek', 'deepseek-chat', 'https://api.deepseek.com'),
        ('OPENROUTER_API_KEY', 'openrouter', 'deepseek/deepseek-chat', 'https://openrouter.ai/api/v1'),
        ('OPENAI_API_KEY', 'openai', 'gpt-4o-mini', 'https://api.openai.com/v1'),
        ('DASHSCOPE_API_KEY', 'qwen', 'qwen-max', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    ]
    
    for key_env, provider, model, api_base in fallback_configs:
        if key_env == primary_key_env:  # 跳过已经尝试过的
            continue
        api_key = os.getenv(key_env)
        if api_key:
            print(f"✅ 自动使用: {provider} - {model}")
            print(f"   使用API Key: {key_env}")
            # 更新配置
            config['provider'] = provider
            config['model'] = model
            config['api_base'] = api_base
            config['api_key_env'] = key_env
            return OpenAI(
                api_key=api_key,
                base_url=api_base
            )
    
    # 如果没有任何可用的API Key
    print("❌ 错误：未找到任何可用的AI API Key！")
    print("   请在 .env 文件中配置以下任意一个：")
    print("   - DEEPSEEK_API_KEY")
    print("   - OPENROUTER_API_KEY")
    print("   - OPENAI_API_KEY")
    print("   - DASHSCOPE_API_KEY")
    print("   - CUSTOM_API_KEY（自定义API，兼容OpenAI格式）")
    print("   详见 AI模型配置说明.md")
    exit(1)

# 初始化AI客户端
AI_CONFIG = load_ai_config()
ai_client = init_ai_client(AI_CONFIG)

# 保持向后兼容
deepseek_client = ai_client

# 重试连接Binance（处理临时网络问题）
print("🔗 正在连接Binance API...")
binance_client = None
max_retries = 5
retry_delay = 3

for attempt in range(max_retries):
    try:
        binance_client = Client(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_SECRET'),
            requests_params={'timeout': 30}  # 增加超时时间到30秒
        )
        print(f"✅ Binance客户端初始化成功")
        break
    except Exception as e:
        print(f"⚠️ Binance连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)[:100]}")
        if attempt < max_retries - 1:
            print(f"   等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
        else:
            print("❌ 无法连接到Binance API，请检查网络连接")
            print("   可能原因：")
            print("   1. 网络不稳定或暂时中断")
            print("   2. Binance API暂时不可用")
            print("   3. 需要代理访问国际网络")
            print("   程序将退出，请稍后重试")
            exit(1)

if binance_client is None:
    print("❌ 初始化失败，程序退出")
    exit(1)

# 初始化模块
portfolio_stats = PortfolioStatistics('portfolio_stats.json', binance_client)

# 配置文件路径（兼容从项目根目录或src目录运行）
config_path = 'config/coins_config.json' if os.path.exists('config/coins_config.json') else '../config/coins_config.json'
market_scanner = MarketScanner(binance_client, config_path)

# AI决策记录文件
AI_DECISIONS_FILE = 'ai_decisions.json'

def save_current_runtime():
    """保存当前运行状态到文件"""
    try:
        runtime_data = {
            'program_start_time': PROGRAM_START_TIME.isoformat(),
            'invocation_count': INVOCATION_COUNT,
            'last_update': datetime.now().isoformat()
        }
        with open(RUNTIME_FILE, 'w', encoding='utf-8') as f:
            json.dump(runtime_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存运行状态失败: {e}")

def save_ai_decision(coin, action, reason, strategy, risk_level, confidence):
    """记录AI决策到文件"""
    try:
        # 加载现有决策
        if os.path.exists(AI_DECISIONS_FILE):
            try:
                with open(AI_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 确保数据结构正确
                if not isinstance(data, dict) or 'decisions' not in data:
                    data = {'decisions': []}
            except (json.JSONDecodeError, ValueError):
                # 文件损坏或为空，重新初始化
                print(f"⚠️ {AI_DECISIONS_FILE} 文件损坏，重新初始化")
                data = {'decisions': []}
        else:
            data = {'decisions': []}
        
        # 添加新决策
        decision = {
            'time': datetime.now().isoformat(),
            'coin': coin,
            'action': action,
            'reason': reason,
            'strategy': strategy,
            'risk_level': risk_level,
            'confidence': confidence
        }
        data['decisions'].append(decision)
        
        # 只保留最近100条
        data['decisions'] = data['decisions'][-100:]
        
        # 保存
        with open(AI_DECISIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存AI决策失败: {e}")

# 交易配置（从配置文件读取）
def load_portfolio_config():
    """从coins_config.json加载投资组合配置"""
    try:
        portfolio_rules = market_scanner.coins_config.get('portfolio_rules', {})
        return {
            'leverage': portfolio_rules.get('leverage', 3),
            'min_cash_reserve_percent': portfolio_rules.get('min_cash_reserve_percent', 10),
            'max_single_coin_percent': portfolio_rules.get('max_single_coin_percent', 100),
    'check_interval_minutes': 5,  # 5分钟调用一次AI（分析5分钟K线数据）
    'test_mode': False  # 实盘模式
}
    except Exception as e:
        print(f"⚠️ 加载配置失败，使用默认值: {e}")
        return {
            'leverage': 3,
            'min_cash_reserve_percent': 10,
            'max_single_coin_percent': 100,
            'check_interval_minutes': 5,
            'test_mode': False
        }

PORTFOLIO_CONFIG = load_portfolio_config()
print(f"📋 配置加载成功 - 杠杆: {PORTFOLIO_CONFIG['leverage']}x, 最低保留资金: {PORTFOLIO_CONFIG['min_cash_reserve_percent']}%, 单币最大: {PORTFOLIO_CONFIG['max_single_coin_percent']}%")


def setup_exchange():
    """设置交易所参数"""
    try:
        # 为所有币种设置杠杆
        for coin_info in market_scanner.coins_config['coins']:
            symbol = coin_info['binance_symbol']
            try:
                binance_client.futures_change_leverage(
                    symbol=symbol,
                    leverage=PORTFOLIO_CONFIG['leverage']
                )
                print(f"✅ {coin_info['symbol']}: 设置杠杆{PORTFOLIO_CONFIG['leverage']}x")
            except Exception as e:
                print(f"⚠️ {coin_info['symbol']}: 设置杠杆失败 - {e}")
        
        # 获取余额
        account_info = binance_client.futures_account()
        usdt_balance = 0
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                usdt_balance = float(asset['availableBalance'])
                break
        
        print(f"💰 当前USDT余额: {usdt_balance:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ 交易所设置失败: {e}")
        return False


def safe_json_parse(json_str):
    """安全解析JSON"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始内容: {json_str}")
            return None


def analyze_portfolio_with_ai(market_data, portfolio_positions, btc_data, account_info, long_term_data):
    """AI投资组合分析"""
    
    # 更新调用次数
    global INVOCATION_COUNT
    INVOCATION_COUNT += 1
    
    # 保存当前运行状态
    save_current_runtime()
    
    # 计算运行时长
    current_time = datetime.now()
    elapsed_time = current_time - PROGRAM_START_TIME
    elapsed_minutes = int(elapsed_time.total_seconds() / 60)
    elapsed_hours = elapsed_minutes / 60
    
    # 格式化时间序列（用箭头连接，更直观）
    def format_series(values, decimals=1):
        if not values or len(values) == 0:
            return "无数据"
        formatted = [f"{v:.{decimals}f}" for v in values]
        return " → ".join(formatted)
    
    # 构建BTC市场参考（加入时间序列）
    if btc_data:
        # 计算ATR百分比
        btc_price = btc_data['price']
        btc_atr_15m_pct = (btc_data['atr_15m'] / btc_price * 100) if btc_price > 0 else 0
        btc_atr_1h_pct = (btc_data['atr_1h'] / btc_price * 100) if btc_price > 0 else 0
        
        btc_text = f"""
【BTC大盘】
- 价格: ${btc_data['price']:,.2f} | 15m: {btc_data['change_15m']:+.2f}%
- 资金费率: {btc_data['funding_rate']:.6f} {'(多头付费)' if btc_data['funding_rate'] > 0 else '(空头付费)' if btc_data['funding_rate'] < 0 else '(中性)'}
- 持仓量: {btc_data['open_interest']:,.0f} BTC

15分钟周期:
- RSI: {btc_data['rsi_15m']:.1f} | 序列: [{format_series(btc_data.get('rsi_series_15m', []), 1)}]
- MACD: {btc_data['macd_15m']:.2f} | 序列: [{format_series(btc_data.get('macd_series_15m', []), 2)}]
- ATR（15分钟）: ${btc_data['atr_15m']:.2f} ({btc_atr_15m_pct:.2f}%) | 序列: [{format_series(btc_data.get('atr_series_15m', []), 2)}]

1小时周期:
- RSI: {btc_data['rsi_1h']:.1f} | 序列: [{format_series(btc_data.get('rsi_series_1h', []), 1)}]
- MACD: {btc_data['macd_1h']:.2f} | 序列: [{format_series(btc_data.get('macd_series_1h', []), 2)}]
- ATR（1小时）: ${btc_data['atr_1h']:.2f} ({btc_atr_1h_pct:.2f}%) | 序列: [{format_series(btc_data.get('atr_series_1h', []), 2)}]
- SMA20: ${btc_data['sma_20_1h']:.0f} | SMA50: ${btc_data['sma_50_1h']:.0f}

2小时周期（轻量级）:
- RSI: {btc_data.get('rsi_4h', 0):.1f}
- MACD: {btc_data.get('macd_4h', 0):.2f}
- SMA20: ${btc_data.get('sma_20_4h', 0):.0f} | SMA50: ${btc_data.get('sma_50_4h', 0):.0f}"""
    else:
        btc_text = "\n【BTC大盘】数据获取失败"
    
    # 构建投资组合状态
    portfolio_text = f"""
【投资组合状态】
总资金: {account_info['total_balance']:.2f} USDT
可用资金: {account_info['free_balance']:.2f} USDT (这是可用保证金)
已用保证金: {account_info['used_margin']:.2f} USDT
保证金占用率: {account_info['margin_ratio']:.1f}%
当前杠杆: {PORTFOLIO_CONFIG['leverage']}x

当前持仓:"""
    
    total_position_value = 0
    total_unrealized_pnl = 0
    position_count = 0
    
    for coin, pos in portfolio_positions.items():
        if pos:
            sl = pos.get('stop_loss', 0)
            tp = pos.get('take_profit', 0)
            roe = pos.get('roe', 0)
            sl_text = f" | 止损{format_price(sl, coin)}" if sl > 0 else ""
            tp_text = f" | 止盈{format_price(tp, coin)}" if tp > 0 else ""
            roe_text = f"{roe:+.2f}%" if roe != 0 else "0.00%"
            portfolio_text += f"""
- {coin}: {pos['side']}仓 | 保证金回报{roe_text} | 盈亏{pos['pnl']:+.2f} USDT | 数量{pos['amount']:.4f}{sl_text}{tp_text}"""
            total_position_value += pos['value']
            total_unrealized_pnl += pos['pnl']
            position_count += 1
        else:
            portfolio_text += f"""
- {coin}: 无持仓"""
    
    portfolio_text += f"""

持仓汇总:
- 持仓币种数: {position_count}个
- 总持仓价值: ${total_position_value:.2f}
- 总未实现盈亏: {total_unrealized_pnl:+.2f} USDT"""
    
    if total_position_value > 0:
        total_pnl_percent = (total_unrealized_pnl / total_position_value) * 100
        portfolio_text += f" ({total_pnl_percent:+.2f}%)"
    
    portfolio_text += f"""
- 现金占比: {(account_info['free_balance']/account_info['total_balance']*100) if account_info['total_balance'] > 0 else 0:.1f}%"""
    
    # 检查最近30分钟的止损触发记录
    recent_stop_losses = portfolio_stats.get_recent_stop_losses(minutes=30)
    if recent_stop_losses:
        stop_loss_text = "\n\n📋 【最近止损触发记录】（过去30分钟内）"
        for sl in recent_stop_losses:
            trigger_time = datetime.fromisoformat(sl['timestamp']).strftime('%H:%M:%S')
            duration = sl['duration_minutes']
            coin = sl['coin']
            stop_loss_text += f"""
- {coin} {sl['side'].upper()}仓 | 开仓{format_price(sl['entry_price'], coin)} → 止损{format_price(sl['stop_price'], coin)} | 盈亏{sl['pnl']:+.2f} USDT | 触发时间{trigger_time} (开仓后{duration}分钟)"""
        portfolio_text += stop_loss_text
    
    # 构建各币种行情（包含1小时趋势）
    market_text = "\n【各币种市场分析】"
    for coin, data in market_data.items():
        
        # 市场情绪数据
        funding_rate = data.get('funding_rate', 0)
        funding_text = f"{'多头付费' if funding_rate > 0 else '空头付费' if funding_rate < 0 else '中性'}"
        open_interest = data.get('open_interest', 0)
        
        # 5分钟指标时间序列
        rsi_series_text = format_series(data.get('rsi_series', []), 1)
        macd_series_text = format_series(data.get('macd_series', []), 4)
        atr_series_text = format_series(data.get('atr_series', []), 2)
        
        # 计算5分钟ATR百分比
        coin_price = data['price']
        atr_15m = data.get('atr', 0)
        atr_15m_pct = (atr_15m / coin_price * 100) if coin_price > 0 else 0
        
        # 获取30分钟数据
        long_term = long_term_data.get(coin, {})
        if long_term:
            rsi_series_1h_text = format_series(long_term.get('rsi_series', []), 1)
            macd_series_1h_text = format_series(long_term.get('macd_series', []), 4)
            atr_series_1h_text = format_series(long_term.get('atr_series', []), 2)
            
            # 计算30分钟ATR百分比
            atr_1h = long_term.get('atr', 0)
            atr_1h_pct = (atr_1h / coin_price * 100) if coin_price > 0 else 0
            
            trend_1h_text = f"""
  
  30分钟周期:
  - RSI: {long_term['rsi']:.1f} | 序列: [{rsi_series_1h_text}]
  - MACD: {long_term['macd']:.4f} | 序列: [{macd_series_1h_text}]
  - ATR（30分钟）: ${atr_1h:.2f} ({atr_1h_pct:.2f}%) | 序列: [{atr_series_1h_text}]
  - SMA20: ${long_term['sma_20']:.2f} | SMA50: ${long_term['sma_50']:.2f}"""
        else:
            trend_1h_text = ""
        
        # 获取2小时数据（轻量级，无时间序列）
        long_term_4h = long_term_data.get(coin + '_4h', {})
        if long_term_4h:
            trend_4h_text = f"""
  
  2小时周期（轻量级）:
  - RSI: {long_term_4h['rsi']:.1f}
  - MACD: {long_term_4h['macd']:.4f}
  - SMA20: ${long_term_4h['sma_20']:.2f} | SMA50: ${long_term_4h['sma_50']:.2f}"""
        else:
            trend_4h_text = ""
        
        # 获取当前K线实时数据 + 历史K线
        current_kline_text = ""
        kline_text = ""
        try:
            coin_info = next((c for c in market_scanner.coins_config['coins'] if c['symbol'] == coin), None)
            if coin_info:
                symbol = coin_info['binance_symbol']
                klines = market_scanner.binance_client.futures_klines(
                    symbol=symbol,
                    interval='30m',
                    limit=25  # 获取最近25根30分钟K线（最后一根是当前未完成的）
                )
                
                # 获取当前K线（最后一根，未完成）
                if len(klines) >= 25:
                    current_kline = klines[-1]
                    current_open = float(current_kline[1])
                    current_high = float(current_kline[2])
                    current_low = float(current_kline[3])
                    current_close = float(current_kline[4])  # 当前价格
                    current_volume = float(current_kline[5])
                    current_change = ((current_close - current_open) / current_open * 100) if current_open > 0 else 0
                    kline_start_time = datetime.fromtimestamp(int(current_kline[0])/1000)
                    kline_end_time = kline_start_time + timedelta(minutes=30)
                    elapsed_min = (current_time - kline_start_time).total_seconds() / 60
                    
                    # 判断K线状态
                    if current_close > current_open:
                        kline_body = "🟢 阳线"
                    elif current_close < current_open:
                        kline_body = "🔴 阴线"
                    else:
                        kline_body = "➖ 平线"
                    
                    # 计算波动幅度
                    volatility = ((current_high - current_low) / current_open * 100) if current_open > 0 else 0
                    
                    # K线价格格式化
                    price_decimals = 4 if coin in ['DOGE', 'XRP'] else 2
                    
                    current_kline_text = f"""
  
  【当前K线实时状态】（30分钟周期进行中）
  - ⏰ 时间窗口: {kline_start_time.strftime('%H:%M')} - {kline_end_time.strftime('%H:%M')} (已运行 {elapsed_min:.0f}/30分钟)
  - 💰 开盘价: ${current_open:.{price_decimals}f}
  - 📈 当前价: ${current_close:.{price_decimals}f}
  - 📊 本K最高: ${current_high:.{price_decimals}f}
  - 📉 本K最低: ${current_low:.{price_decimals}f}
  - 📦 成交量: {current_volume:.2f}
  - 📈 K线状态: {kline_body} ({current_change:+.2f}%)
  - ⚡ 波动幅度: {volatility:.2f}%"""
                    
                    # 获取历史24根30分钟K线
                    kline_text = "\n  最近24根K线（30分钟周期，从旧到新，共12小时）："
                    for i, kline in enumerate(klines[-25:-1], 1):  # 取倒数第25到第2根（不含当前K线）
                        open_p = float(kline[1])
                        high_p = float(kline[2])
                        low_p = float(kline[3])
                        close_p = float(kline[4])
                        change = ((close_p - open_p) / open_p * 100) if open_p > 0 else 0
                        body = "🟢" if close_p > open_p else "🔴" if close_p < open_p else "➖"
                        kline_text += f"\n    K{i}: {body} O${open_p:.{price_decimals}f} H${high_p:.{price_decimals}f} L${low_p:.{price_decimals}f} C${close_p:.{price_decimals}f} ({change:+.2f}%)"
        except Exception as e:
            current_kline_text = f"\n  ⚠️ 当前K线数据获取失败: {e}"
            kline_text = f"\n  ⚠️ 历史K线数据获取失败: {e}"
        
        # 格式化价格（低价币种显示更多小数）
        price_display = format_price(data['price'], coin).replace('$', '')
        
        market_text += f"""

{coin}/USDT:
- 价格: ${price_display} | 24h: {data['change_24h']:+.2f}% | 15m: {data['change_15m']:+.2f}%
- 资金费率: {funding_rate:.6f} ({funding_text}) | 持仓量: {open_interest:,.0f}
- 最小开仓: {data['min_order_value']} USDT{current_kline_text}

  5分钟周期:
  - RSI: {data['rsi']:.1f} | 序列: [{rsi_series_text}]
  - MACD: {data['macd']:.4f} | 序列: [{macd_series_text}]
  - ATR（15分钟）: ${atr_15m:.2f} ({atr_15m_pct:.2f}%) | 序列: [{atr_series_text}]
  - SMA20: ${data['sma_20']:.2f} | SMA50: ${data['sma_50']:.2f}
  - 布林带位置: {data['bb_position']:.2%}{trend_1h_text}{trend_4h_text}{kline_text}"""
    
    # 获取统计信息
    stats_text = portfolio_stats.generate_stats_text_for_ai()
    
    # 读取最近的AI决策历史
    last_decisions_text = ""
    try:
        if os.path.exists(AI_DECISIONS_FILE):
            with open(AI_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                decisions_data = json.load(f)
                recent_decisions = decisions_data.get('decisions', [])[-3:]  # 最近3条
                
                if recent_decisions:
                    last_decisions_text = "\n【最近AI决策记录】（最近45分钟）"
                    for i, dec in enumerate(reversed(recent_decisions), 1):
                        time_str = dec.get('time', 'N/A')[:19] if dec.get('time') else 'N/A'
                        coin = dec.get('coin', 'N/A')
                        action = dec.get('action', 'N/A')
                        reason = dec.get('reason', 'N/A')
                        confidence = dec.get('confidence', 'N/A')
                        
                        last_decisions_text += f"""
{i}. {time_str} - {coin}
   操作: {action}
   理由: {reason}
   信心: {confidence}
"""
    except Exception as e:
        print(f"⚠️ 读取历史决策失败: {e}")
        last_decisions_text = ""
    
    # 格式化运行时长
    if elapsed_hours < 1:
        runtime_text = f"{elapsed_minutes}分钟"
    else:
        runtime_text = f"{elapsed_hours:.1f}小时 ({elapsed_minutes}分钟)"
    
    prompt = f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          📊 AI投资组合管理系统 - 第 {INVOCATION_COUNT} 次调用          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 系统运行状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 程序启动: {PROGRAM_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}
⏰ 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
⏱️  已运行: {runtime_text} | 第 {INVOCATION_COUNT} 次调用

📊 数据顺序: 所有时间序列数据从旧到新（最旧 → 最新）
📈 K线周期: 15分钟（短期指标）| 30分钟（详细K线+中期指标）| 1小时/2小时（长期指标）
⏰ AI调用: 每5分钟调用一次

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

您是一位专业的加密货币投资组合经理(Portfolio Manager)，管理多币种投资组合。

{stats_text}

{btc_text}

{portfolio_text}

{market_text}
{last_decisions_text}

【决策要求】

⏰ 数据获取周期：
- 系统每5分钟调用你一次，提供最新市场数据
- 你会持续获得市场快照，可以观察价格和指标的连续变化
- 调用频率较高，数据获取无延迟，只在你认为有必要操作时操作即可

🎯 分析维度：
- K线走势：价格、成交量、支撑阻力、趋势阶段
- 技术指标：RSI、MACD、SMA、布林带、ATR
- 多周期数据：15分钟K线（短期指标） + 30分钟K线（详细K线+中期指标） + 1小时/2小时K线（长期指标）

⚠️ 止损设置规则：

【开仓时】（必须遵守）
- 止损距离必须 ≥ 1.5倍当前ATR百分比
- 绝对最小值：BTC/ETH最小2%，其他币种（SOL/DOGE/XRP/BNB）最小3%
- ⚠️ 注意：ATR使用15分钟周期计算（更稳定的波动率指标），已在市场数据中显示为百分比
- 计算示例：
  · XRP当前ATR 3.04%（15分钟） → 止损距离应 ≥ 3.04% × 1.5 = 4.56%
  · SOL当前ATR 2.5%（15分钟） → 止损距离应 ≥ max(2.5% × 1.5, 3%) = 3.75%

【HOLD时】（灵活判断）
- 请根据市场情况自主判断是否需要调整止损
- 参考原则：
  · 无充分理由时，保持原止损即可
  · 价格有利时可考虑追踪止盈

💡 止损机制说明：
- 止损是兜底风控，防止极端行情造成重大损失
- 止损≠必须等到触发，如果你认为应该提前止损可以自己操作

💰 止盈操作指南：
- 你是日内交易员，目标是通过短期波动获利
- **盈利参考线**：当持仓ROE（保证金回报率）≥ 2%时，建议考虑止盈
- **灵活止盈**：即使ROE未达到2%，如果你判断趋势转弱或出现反转信号，也可以主动CLOSE提前锁定利润
- **自主判断权**：你有完全的决策权。如果你判断趋势仍然强劲、有继续持有的理由，可以选择HOLD
- **主动止盈优于被动等待**：止盈价格仅作参考，当你认为应该止盈时，可直接CLOSE，无需等到达到止盈价格
- **避免盈利回吐**：如果没有明确的继续持仓理由，建议主动CLOSE锁定利润

📊 可用操作：
- OPEN_LONG: 开多仓
- OPEN_SHORT: 开空仓
- CLOSE: 平仓
- HOLD: 持仓观望（已有仓位时，如果判断应该继续持有，选择HOLD）

⚠️ 重要：不支持加仓操作，每个币种只能持有一个方向的仓位

⚠️ 硬性限制（必须遵守）：
1. position_value 是持仓价值（开仓后的名义价值）= 保证金 × 杠杆
2. **开仓保证金计算公式**：
   - 当前可用资金：{account_info['free_balance']:.2f} USDT
   - 保留10%资金：{account_info['free_balance'] * 0.1:.2f} USDT
   - 可用于开仓的保证金：{account_info['free_balance'] * 0.9:.2f} USDT
   - 最大持仓价值（position_value）：{account_info['free_balance'] * 0.9 * PORTFOLIO_CONFIG['leverage']:.2f} USDT
3. ⚠️ **所有新开仓位的 position_value 总和必须 ≤ {account_info['free_balance'] * 0.9 * PORTFOLIO_CONFIG['leverage']:.2f} USDT**
4. 单个币种可以使用全部可开仓额度（无单币种上限）
5. 最小开仓金额（position_value）：BTC 50 USDT | ETH 24 USDT | BNB 12 USDT | SOL/XRP/ADA/DOGE 6 USDT

📝 返回JSON格式（3种场景示例）：

场景1：持仓等待（已有仓位，判断应该持仓）
{{
    "decisions": [
        {{
            "coin": "ETH",
            "action": "HOLD",
            "reason": "K线：连续3根阳线上涨 | 指标：30m SMA20上行，5m RSI 55中性",
            "position_value": 0,
            "stop_loss": 3200.5,
            "take_profit": 3500.0
        }}
    ],
    "strategy": "维持现有仓位，等待趋势延续或反转信号",
    "risk_level": "LOW",
    "confidence": "HIGH"
}}

场景2：有操作（出现明确信号）
{{
    "decisions": [
        {{
            "coin": "ETH",
            "action": "CLOSE",
            "reason": "K线：跌破支撑位 | 指标：5m RSI 30，MACD转负",
            "position_value": 0,
            "stop_loss": 0,
            "take_profit": 0
        }},
        {{
            "coin": "SOL",
            "action": "OPEN_LONG",
            "reason": "K线：突破阻力位，放量上涨 | 指标：30m SMA20上穿SMA50，5m RSI 65",
            "position_value": 100,
            "stop_loss": 145.5,
            "take_profit": 155.0
        }}
    ],
    "strategy": "基于技术信号调整仓位",
    "risk_level": "MEDIUM",
    "confidence": "HIGH"
}}

场景3：完全观望（无仓位，无明确信号）
{{
    "decisions": [],
    "strategy": "市场震荡，无明确趋势，等待机会",
    "risk_level": "LOW",
    "confidence": "MEDIUM"
}}

⚠️ 注意：
- 已有仓位时，可以选择HOLD或CLOSE，根据市场情况自主判断
- 无仓位且无明确信号时，返回空的decisions数组
- position_value 是持仓价值（USDT），HOLD和CLOSE时填0
- **禁止加仓**：每个币种只能持有一个方向的仓位，如需调整请先平仓再开新仓
- stop_loss 和 take_profit 必填（填具体价格，CLOSE时可填0）
- HOLD时是否调整止损由你判断；无充分理由请保持原止损，价格有利时可考虑追踪止盈
- HOLD时如不调整，请沿用上次的 stop_loss / take_profit，不要填0（只有CLOSE时可为0）
- 确保JSON格式完全正确

📋 reason要求：
- 必须同时说明K线形态和技术指标的情况
- 简要说明即可，不要啰嗦
- 格式参考："K线突破阻力 | RSI 65上行" 或 "连续下跌 | MACD转负"
    """
    
    try:
        response = ai_client.chat.completions.create(
            model=AI_CONFIG['model'],
            temperature=AI_CONFIG.get('temperature', 0.7),
            max_tokens=AI_CONFIG.get('max_tokens', 8000),
            messages=[
                {"role": "system", "content": """您是一位经验丰富的专业投资组合经理(Portfolio Manager)。

# 首要遵守原则（最高优先级）
⚠️ **当你对当前市场状态感到不确定、矛盾或犹豫时，必须选择观望**
这是最高优先级原则，覆盖所有其他规则：
- **有任何疑虑 → 必须观望**（不要尝试"勉强开仓"）
- **完全确定 → 才能开仓**
- **不确定是否违反某条款 = 视为违反 → 必须观望**
记住：**错过机会比做错交易更安全。宁可错过，不做模糊决策。**

【交易身份】
- 管理类型：多币种投资组合（BNB/ETH/SOL/XRP/DOGE）
- K线数据：15分钟（短期指标）+ 30分钟（详细K线+中期指标）+ 1小时/2小时（长期指标）
- 调用频率：每5分钟
- 交易方向：做多做空同样积极，不偏好任何方向
- 交易风格：专业的日内交易员

【核心目标】
通过专业技术分析，捕捉市场中的超额收益机会（alpha）。

⚠️ **数据顺序说明（极其重要）**：
- 所有序列数据按时间排列：**最旧 → 最新** (oldest → latest)
- 数组的**最后一个元素**是**最新数据点**（当前值）
- 数组的**第一个元素**是**最旧数据点**（历史值）
- ⚠️ 不要混淆顺序！这是常见错误（会导致把上涨误判为下跌）

【权限与理念】
💼 您拥有完全的仓位控制权：
   - 可以开仓、平仓任何币种
   - 可以同时持有多个币种
   - 每个币种只能持有一个方向的仓位（禁止加仓）
   - 如需调整仓位，请先平仓再开新仓（建议2-3个币种分散风险）
   - 可以根据市场变化随时调仓

🎯 决策理念：
   - 您是投资组合的唯一决策者
   - 根据技术分析、市场趋势、BTC大盘自主判断
   - 不要为了交易而交易，只在有明确信号时行动
   - 质量 > 数量：宁可错过，不要做错

⏱️ 【持仓时间与交易频率】
- **最小持仓时间**：至少20分钟，让交易充分展开
  - 唯一例外：您认为必须平仓来避免极端亏损的情况
- 优秀交易员：每小时≤2笔交易（监控6个币种）
- 过度交易：每小时>2笔 = 严重问题！
- 自我检查：如果你每个周期都在交易 → 信号质量太低
- 如果持仓<20分钟就平仓 → 说明你开仓考虑欠佳（极端止损除外）
- 请注意"交易频率监控"数据，如果出现警告立即降低交易频率

📉 【做多做空平衡】
重要：下跌趋势做空的利润 = 上涨趋势做多的利润
- 上涨趋势 → 做多
- 下跌趋势 → 做空（不要有做多偏见！）
- 震荡市场 → 观望

🎯 【开仓信号标准（严格）】
只在强信号时开仓，不确定就观望！

强信号特征：
- 多维度交叉验证：价格形态 + 成交量 + 技术指标 + 趋势方向
- 综合信心度 ≥ 75%
- 风险回报比 ≥ 1:2
- 有明确的支撑/阻力位作为止损依据

**信号优先级参考**（当遇到矛盾信号时，可作为参考）：
1. 趋势共振（5m/30m/2h 方向一致）→ 权重较高
2. 放量确认（成交量>1.5x均量）→ 动能验证
3. BTC状态（交易山寨币时）→ 市场领导者方向
4. RSI区间（超买超卖确认）
5. 价格vs SMA20（趋势方向）
前3项都一致时，即使其他指标不够完美，也可以考虑开仓。

避免低质量信号：
- 单一维度（只看一个指标）
- 相互矛盾（价格上涨但量萎缩）
- 横盘震荡（无明确趋势）
- 短期噪音（15分钟突刺，但30分钟/1小时无确认）
- **防假突破提示**（建议谨慎）：
  * 15分钟RSI超买（>70）但30分钟RSI未跟上（<60）→ 可能是假突破
  * 价格突破但成交量萎缩（<均量×0.8）→ 可能缺乏动能

💰 【仓位管理建议】
- 单币种建议：20-40%可用资金（常规机会）
- 高信心机会：40-60%可用资金
- 总持仓建议：2-3个币种同时持有（分散风险）
- 保留现金：至少10%（已强制执行）
- 不要梭哈单一币种！

📋 【决策前自我检查】
开仓前请自问：
1. 我是否足够确定这是高质量机会？
2. 如果这是我的钱，我会开这单吗？
3. 我能清楚说出至少2个开仓理由吗？
如果任一问题不明确 → 禁止开仓，选择观望

请基于专业分析自主判断，严格返回JSON格式。"""},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        result = response.choices[0].message.content
        print(f"\n🤖 AI原始回复:\n{result}\n")
        
        # 提取JSON
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            decisions_data = safe_json_parse(json_str)
            
            if decisions_data and 'decisions' in decisions_data:
                return decisions_data
        
        return {'decisions': [], 'strategy': '无操作', 'risk_level': 'LOW', 'confidence': 'LOW'}
        
    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        return {'decisions': [], 'strategy': '错误', 'risk_level': 'HIGH', 'confidence': 'LOW'}


def calculate_position_size(coin, position_value, current_price, coin_config):
    """计算交易数量"""
    try:
        precision = coin_config['precision']
        min_order_value = coin_config['min_order_value']
        
        if position_value < min_order_value:
            print(f"⚠️ {coin}: {position_value:.2f} USDT < 最小限制 {min_order_value} USDT")
            return 0
        
        # 计算数量
        raw_amount = position_value / current_price
        
        # 智能取整
        multiplier = 10 ** precision
        amount_floor = math.floor(raw_amount * multiplier) / multiplier
        amount_ceil = math.ceil(raw_amount * multiplier) / multiplier
        
        value_floor = amount_floor * current_price
        value_ceil = amount_ceil * current_price
        
        error_floor = abs(value_floor - position_value) / position_value * 100
        error_ceil = abs(value_ceil - position_value) / position_value * 100
        
        amount = amount_floor if error_floor < error_ceil else amount_ceil
        
        if amount == 0:
            print(f"⚠️ {coin}: 计算数量为0")
            return 0
        
        return amount
        
    except Exception as e:
        print(f"❌ {coin}: 仓位计算失败 - {e}")
        return 0


def execute_portfolio_decisions(decisions_data, market_data):
    """执行投资组合决策"""
    if not decisions_data or not decisions_data.get('decisions'):
        print("💤 AI决定观望，不执行交易")
        return
    
    decisions = decisions_data['decisions']
    strategy = decisions_data.get('strategy', '')
    risk_level = decisions_data.get('risk_level', 'UNKNOWN')
    confidence = decisions_data.get('confidence', 'UNKNOWN')
    
    print(f"\n{'='*60}")
    print(f"📊 AI投资组合决策")
    print(f"{'='*60}")
    print(f"策略: {strategy}")
    print(f"风险等级: {risk_level}")
    print(f"信心程度: {confidence}")
    print(f"决策数量: {len(decisions)}个")
    print(f"{'='*60}\n")
    
    # 记录每个AI决策
    for decision in decisions:
        save_ai_decision(
            coin=decision['coin'],
            action=decision['action'],
            reason=decision['reason'],
            strategy=strategy,
            risk_level=risk_level,
            confidence=confidence
        )
    
    if PORTFOLIO_CONFIG['test_mode']:
        print("🧪 测试模式 - 仅模拟交易\n")
        for i, decision in enumerate(decisions, 1):
            print(f"{i}. {decision['coin']}: {decision['action']} - {decision['reason']}")
        return
    
    # 执行每个决策
    for i, decision in enumerate(decisions, 1):
        coin = decision['coin']
        action = decision['action']
        reason = decision['reason']
        position_value = float(decision.get('position_value', 0))
        stop_loss = float(decision.get('stop_loss', 0))
        take_profit = float(decision.get('take_profit', 0))
        
        print(f"\n{'─'*60}")
        print(f"决策 {i}/{len(decisions)}: {coin}")
        print(f"操作: {action}")
        print(f"理由: {reason}")
        print(f"开仓金额: {position_value:.2f} USDT")
        if stop_loss > 0:
            print(f"止损: {format_price(stop_loss, coin)}")
        if take_profit > 0:
            print(f"止盈: {format_price(take_profit, coin)}")
        print(f"{'─'*60}")
        
        try:
            coin_info = next((c for c in market_scanner.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                print(f"❌ 未找到{coin}的配置")
                continue
            
            symbol = coin_info['binance_symbol']
            coin_market = market_data.get(coin)
            if not coin_market:
                print(f"❌ 未找到{coin}的市场数据")
                continue
            
            current_price = coin_market['price']
            
            # 获取当前持仓
            positions = market_scanner.get_portfolio_positions()
            current_position = positions.get(coin)
            
            if action == 'HOLD':
                if current_position:
                    print(f"💎 持仓: {current_position['amount']} {coin} ({current_position['side']})")
                    print(f"   当前盈亏: {current_position.get('pnl', 0):.2f} USDT")
                    
                    # 检查止损价格是否变化（AI可能动态调整）
                    old_stop_loss = current_position.get('stop_loss', 0)
                    stop_order_id = 0
                    
                    if stop_loss != old_stop_loss and stop_loss > 0:
                        print(f"   🔄 止损价格变化: {format_price(old_stop_loss, coin)} → {format_price(stop_loss, coin)}")
                        
                        # 1. 取消旧止损单
                        portfolio_stats.cancel_stop_loss_order(coin, symbol)
                        
                        # 2. 下新止损单
                        try:
                            side_for_stop = 'SELL' if current_position['side'] == 'long' else 'BUY'
                            amount_for_stop = current_position['amount']
                            price_precision = coin_info.get('price_precision', 2)
                            
                            stop_order = binance_client.futures_create_order(
                                symbol=symbol,
                                side=side_for_stop,
                                type='STOP_MARKET',
                                stopPrice=round(stop_loss, price_precision),
                                quantity=amount_for_stop,
                                reduceOnly=True
                            )
                            stop_order_id = stop_order.get('orderId', 0)
                            print(f"   🛡️ 新止损单已设置: {format_price(stop_loss, coin)} (订单ID: {stop_order_id})")
                        except Exception as e:
                            print(f"   ⚠️ 新止损单下单失败: {str(e)[:100]}")
                    
                    # 更新止损止盈（AI可能动态调整）
                    portfolio_stats.update_stop_loss_take_profit(coin, stop_loss, take_profit, stop_order_id)
                    print(f"✅ {coin} 继续持仓")
                else:
                    print(f"⚠️ {coin} 无持仓但AI决定HOLD（可能是观望状态）")
            
            elif action == 'CLOSE':
                if current_position:
                    amount = round(current_position['amount'], coin_info['precision'])
                    side = 'SELL' if current_position['side'] == 'long' else 'BUY'
                    
                    print(f"📤 平{current_position['side']}仓: {amount} {coin}")
                    
                    # 1. 先取消止损单（如果存在）
                    portfolio_stats.cancel_stop_loss_order(coin, symbol)
                    
                    # 2. 平仓
                    binance_client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type='MARKET',
                        quantity=amount,
                        reduceOnly=True
                    )
                    
                    # 🆕 2.5. 平仓后立即清理该币种所有挂单（防止止盈止损单变孤儿）
                    try:
                        binance_client.futures_cancel_all_open_orders(symbol=symbol)
                    except Exception as e:
                        print(f"  ⚠️ 平仓后清理挂单失败: {str(e)[:100]}")
                    
                    # 3. 记录平仓
                    portfolio_stats.record_trade_exit(coin, current_price, 'ai_decision')
                    print(f"✅ {coin} 平仓成功")
                else:
                    print(f"⚠️ {coin} 无持仓，跳过平仓")
            
            elif action in ['OPEN_LONG', 'OPEN_SHORT']:
                # 检查是否已有持仓（禁止加仓）
                if current_position is not None:
                    print(f"⚠️ {coin} 已有持仓，禁止加仓。请先平仓再开新仓。")
                    continue
                
                amount = calculate_position_size(coin, position_value, current_price, coin_info)
                
                if amount > 0:
                    if action == 'OPEN_LONG':
                        print(f"📈 开多仓: {amount} {coin} (${position_value:.2f})")
                        
                        # 1. 开仓
                        binance_client.futures_create_order(
                            symbol=symbol,
                            side='BUY',
                            type='MARKET',
                            quantity=amount
                        )
                        
                        # 2. 立即下止损单（如果AI设置了止损价格）
                        stop_order_id = 0
                        if action == 'OPEN_LONG' and stop_loss > 0:
                            try:
                                price_precision = coin_info.get('price_precision', 2)
                                stop_order = binance_client.futures_create_order(
                                    symbol=symbol,
                                    side='SELL',  # 多仓止损用SELL
                                    type='STOP_MARKET',
                                    stopPrice=round(stop_loss, price_precision),  # 触发价格
                                    quantity=amount,
                                    reduceOnly=True  # 只减仓
                                )
                                stop_order_id = stop_order.get('orderId', 0)
                                print(f"   🛡️ 止损单已设置: {format_price(stop_loss, coin)} (订单ID: {stop_order_id})")
                            except Exception as e:
                                print(f"   ⚠️ 止损单下单失败: {str(e)[:100]}")
                        
                        # 3. 记录持仓
                        portfolio_stats.record_position_entry(coin, 'long', current_price, amount, stop_loss, take_profit, stop_order_id)
                        
                        print(f"✅ {coin} 多仓成功")
                    
                    elif action == 'OPEN_SHORT':
                        print(f"📉 开空仓: {amount} {coin} (${position_value:.2f})")
                        
                        # 1. 开仓
                        binance_client.futures_create_order(
                            symbol=symbol,
                            side='SELL',
                            type='MARKET',
                            quantity=amount
                        )
                        
                        # 2. 立即下止损单（如果AI设置了止损价格）
                        stop_order_id = 0
                        if action == 'OPEN_SHORT' and stop_loss > 0:
                            try:
                                price_precision = coin_info.get('price_precision', 2)
                                stop_order = binance_client.futures_create_order(
                                    symbol=symbol,
                                    side='BUY',  # 空仓止损用BUY
                                    type='STOP_MARKET',
                                    stopPrice=round(stop_loss, price_precision),  # 触发价格
                                    quantity=amount,
                                    reduceOnly=True  # 只减仓
                                )
                                stop_order_id = stop_order.get('orderId', 0)
                                print(f"   🛡️ 止损单已设置: {format_price(stop_loss, coin)} (订单ID: {stop_order_id})")
                            except Exception as e:
                                print(f"   ⚠️ 止损单下单失败: {str(e)[:100]}")
                        
                        # 3. 记录持仓
                        portfolio_stats.record_position_entry(coin, 'short', current_price, amount, stop_loss, take_profit, stop_order_id)
                        
                        print(f"✅ {coin} 空仓成功")
                else:
                    print(f"⚠️ {coin} 数量计算为0，跳过")
            
            elif action == 'ADD':
                print(f"⚠️ {coin} 不支持加仓操作。如需调整仓位，请先平仓再开新仓。")
            
            else:
                print(f"⚠️ {coin} 未知操作: {action}")
            
            time.sleep(0.5)  # 避免API限流
            
        except BinanceAPIException as e:
            print(f"❌ {coin} 币安API错误: {e.code} - {e.message}")
        except Exception as e:
            print(f"❌ {coin} 执行失败: {e}")
    
    print(f"\n{'='*60}")
    print("✅ 投资组合调整完成")
    print(f"{'='*60}\n")


def sync_portfolio_positions_on_startup():
    """
    程序启动时同步所有币种的持仓状态
    
    逻辑：
    1. 查询币安所有币种的真实持仓
    2. 查询统计模块记录的持仓
    3. 如果不一致，以币安真实持仓为准
    4. 更新统计模块
    """
    print("\n" + "="*60)
    print("🔄 同步投资组合持仓状态...")
    print("="*60)
    
    # 1. 获取币安所有币种的真实持仓
    real_positions = market_scanner.get_portfolio_positions()
    
    # 2. 获取统计模块记录的持仓
    stats_positions = portfolio_stats.current_positions
    
    # 3. 逐个币种对比
    has_discrepancy = False
    
    for coin in market_scanner.coins:
        real_pos = real_positions.get(coin)
        stats_pos = stats_positions.get(coin)
        
        if real_pos and stats_pos:
            # 两者都有持仓，检查是否一致
            real_side = real_pos['side']
            stats_side = stats_pos['side']
            
            if real_side == stats_side:
                print(f"✅ {coin}: 持仓状态一致 ({real_side}仓)")
                print(f"   统计: {stats_pos['amount']:.4f} @ ${stats_pos['entry_price']:.2f}")
                print(f"   实际: {real_pos['amount']:.4f} @ ${real_pos['entry_price']:.2f}")
            else:
                print(f"⚠️ {coin}: 持仓方向不一致！")
                print(f"   统计: {stats_side}仓")
                print(f"   实际: {real_side}仓")
                print(f"   → 以币安实际持仓为准，更新统计模块")
                
                has_discrepancy = True
                portfolio_stats.current_positions[coin] = None
                portfolio_stats.record_position_entry(
                    coin,
                    real_side,
                    real_pos['entry_price'],
                    real_pos['amount']
                )
        
        elif real_pos and not stats_pos:
            # 币安有持仓，但统计模块没有记录
            print(f"⚠️ {coin}: 发现未记录的持仓！")
            print(f"   实际: {real_pos['side']}仓 {real_pos['amount']:.4f} @ ${real_pos['entry_price']:.2f}")
            print(f"   → 可能是手动开仓或程序异常退出")
            print(f"   → 将此持仓记录到统计模块")
            
            has_discrepancy = True
            portfolio_stats.record_position_entry(
                coin,
                real_pos['side'],
                real_pos['entry_price'],
                real_pos['amount']
            )
        
        elif not real_pos and stats_pos:
            # 统计模块有记录，但币安没有持仓
            print(f"⚠️ {coin}: 统计模块记录了持仓，但币安实际无持仓！")
            print(f"   统计: {stats_pos['side']}仓 {stats_pos['amount']:.4f} @ ${stats_pos['entry_price']:.2f}")
            print(f"   → 可能是手动平仓、程序异常或止损触发")
            
            # 检查是否有止损单，若有则查询是否已触发
            stop_order_id = stats_pos.get('stop_order_id', 0)
            stop_loss_triggered = False
            
            if stop_order_id > 0:
                try:
                    # 查询止损单状态
                    coin_info = next((c for c in market_scanner.coins_config['coins'] if c['symbol'] == coin), None)
                    if not coin_info:
                        print(f"   ⚠️ 无法找到 {coin} 的配置信息")
                        continue
                    
                    symbol = coin_info['binance_symbol']
                    order = binance_client.futures_get_order(
                        symbol=symbol,
                        orderId=stop_order_id
                    )
                    
                    if order['status'] == 'FILLED':
                        # 止损单已触发！
                        stop_loss_triggered = True
                        trigger_time = datetime.fromtimestamp(order['updateTime'] / 1000)
                        avg_price = float(order.get('avgPrice', order.get('price', stats_pos['stop_loss'])))
                        
                        print(f"   🔴 确认：止损单已触发！")
                        print(f"   触发时间: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   止损价: ${stats_pos['stop_loss']:.2f}")
                        print(f"   成交价: ${avg_price:.2f}")
                        
                        # 计算盈亏
                        entry_price = stats_pos['entry_price']
                        amount = stats_pos['amount']
                        if stats_pos['side'] == 'long':
                            pnl = (avg_price - entry_price) * amount
                        else:  # short
                            pnl = (entry_price - avg_price) * amount
                        
                        # 记录到止损触发历史
                        entry_time = datetime.fromisoformat(stats_pos['entry_time'])
                        portfolio_stats.record_stop_loss_triggered(
                            coin=coin,
                            side=stats_pos['side'],
                            entry_price=entry_price,
                            stop_price=stats_pos['stop_loss'],
                            amount=amount,
                            trigger_time=trigger_time,
                            pnl=pnl,
                            entry_time=entry_time
                        )
                        
                        # 记录平仓到交易历史
                        portfolio_stats.record_trade_exit(coin, avg_price, 'stop_loss_triggered')
                        
                except Exception as e:
                    print(f"   ⚠️ 查询止损单状态失败: {e}")
            
            # 如果不是止损触发，按原逻辑处理
            if not stop_loss_triggered:
                # 获取当前价格
                market_data = market_scanner.scan_coin(coin, '5m', 10)
                if market_data:
                    current_price = market_data['price']
                    print(f"   → 按当前价格 ${current_price:.2f} 记录平仓到统计")
                    portfolio_stats.record_trade_exit(coin, current_price, 'manual_close_detected')
                else:
                    print(f"   → 无法获取当前价格，清除统计记录")
                    portfolio_stats.current_positions[coin] = None
                    portfolio_stats.save()
            
            has_discrepancy = True
    
    if not has_discrepancy:
        # 检查是否所有币种都无持仓
        has_any_position = any(real_positions.values())
        if not has_any_position:
            print("✅ 当前无任何持仓")
        else:
            print("✅ 所有持仓状态一致")
    
    print("="*60 + "\n")


def clean_orphan_orders():
    """
    清理孤儿订单（有挂单但无持仓的情况）
    防止止损/止盈单在仓位关闭后仍然触发导致反向开仓
    """
    try:
        # 1. 获取所有持仓
        positions = binance_client.futures_position_information()
        
        # 2. 获取所有挂单
        open_orders = binance_client.futures_get_open_orders()
        
        if not open_orders:
            return  # 没有挂单，直接返回
        
        # 3. 构建持仓币种集合（单向持仓模式，只需要 symbol）
        position_symbols = set()
        for pos in positions:
            symbol = pos['symbol']
            position_amt = float(pos['positionAmt'])
            
            # 如果有仓位（不为0），标记该币种
            if abs(position_amt) > 0.0001:
                position_symbols.add(symbol)
        
        # 4. 按币种分组挂单
        orders_by_symbol = {}
        for order in open_orders:
            symbol = order['symbol']
            if symbol not in orders_by_symbol:
                orders_by_symbol[symbol] = []
            orders_by_symbol[symbol].append(order)
        
        # 5. 检查并清理孤儿订单
        orphan_count = 0
        for symbol, orders in orders_by_symbol.items():
            # 如果该币种有挂单但没有持仓
            if symbol not in position_symbols and len(orders) > 0:
                print(f"🧹 清理孤儿订单: {symbol} (有{len(orders)}个挂单但无持仓)")
                
                # 取消该币种的所有挂单
                try:
                    binance_client.futures_cancel_all_open_orders(symbol=symbol)
                    orphan_count += len(orders)
                except Exception as e:
                    print(f"  ⚠️ 清理失败: {str(e)[:100]}")
        
        if orphan_count > 0:
            print(f"✓ 清理完成：共清理 {orphan_count} 个孤儿订单")
    
    except Exception as e:
        print(f"⚠️ 清理孤儿订单失败（继续执行）: {str(e)[:100]}")


def portfolio_bot():
    """投资组合机器人主循环"""
    print("\n" + "="*60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 0. 清理孤儿订单（防止止损止盈单变孤儿后误触发）
    print("🧹 [Step 0] 清理孤儿订单...")
    clean_orphan_orders()
    
    # 1. 扫描市场（5分钟K线）
    print("📊 获取5分钟K线数据（短期技术指标）...")
    market_data = market_scanner.scan_all_markets()
    if not market_data:
        print("❌ 市场数据获取失败")
        return
    
    # 2. 获取30分钟数据
    print("📊 获取30分钟K线数据（中期趋势）...")
    long_term_data = {}
    for coin in market_scanner.coins:
        data_1h = market_scanner.get_coin_long_term_data(coin)
        if data_1h:
            long_term_data[coin] = data_1h
            # 低价币种显示更多小数位
            price_decimals = 4 if coin in ['DOGE', 'XRP'] else 2
            print(f"   {coin}: SMA20 ${data_1h['sma_20']:.{price_decimals}f} | SMA50 ${data_1h['sma_50']:.{price_decimals}f} | RSI {data_1h['rsi']:.1f}")
    
    # 3. 获取2小时数据（长期趋势）
    print("📊 获取2小时K线数据（长期趋势）...")
    for coin in market_scanner.coins:
        data_4h = market_scanner.get_coin_4h_data(coin)
        if data_4h:
            long_term_data[coin + '_4h'] = data_4h
            # 低价币种显示更多小数位
            price_decimals = 4 if coin in ['DOGE', 'XRP'] else 2
            print(f"   {coin}: SMA20 ${data_4h['sma_20']:.{price_decimals}f} | SMA50 ${data_4h['sma_50']:.{price_decimals}f} | RSI {data_4h['rsi']:.1f}")
    
    # 4. 获取BTC背景（15分钟+1小时+4小时）
    btc_data = market_scanner.get_btc_context()
    
    # 5. 获取持仓
    portfolio_positions = market_scanner.get_portfolio_positions()
    
    # 6. 获取账户信息
    account_info = market_scanner.get_account_info()
    
    # 7. AI分析
    decisions_data = analyze_portfolio_with_ai(market_data, portfolio_positions, btc_data, account_info, long_term_data)
    
    # 7. 执行决策
    execute_portfolio_decisions(decisions_data, market_data)


def main():
    """主函数"""
    print(f"\n{'='*60}")
    print("🚀 AI多币种投资组合管理系统启动")
    print(f"{'='*60}")
    print(f"管理币种: {', '.join(market_scanner.coins)}")
    print(f"杠杆倍数: {PORTFOLIO_CONFIG['leverage']}x")
    print(f"检查间隔: {PORTFOLIO_CONFIG['check_interval_minutes']}分钟")
    
    if PORTFOLIO_CONFIG['test_mode']:
        print("🧪 当前为测试模式，不会真实下单")
    else:
        print("🚨 实盘交易模式，请谨慎操作！")
    
    print(f"{'='*60}\n")
    
    # 显示统计摘要
    print(portfolio_stats.get_summary())
    
    # 设置交易所
    if not setup_exchange():
        print("❌ 交易所初始化失败，程序退出")
        return
    
    # 同步持仓状态
    sync_portfolio_positions_on_startup()
    
    # 设置定时任务
    schedule.every(PORTFOLIO_CONFIG['check_interval_minutes']).minutes.do(portfolio_bot)
    print(f"⏰ 执行频率: 每{PORTFOLIO_CONFIG['check_interval_minutes']}分钟一次\n")
    
    # 立即执行一次
    portfolio_bot()
    
    # 循环执行
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()

