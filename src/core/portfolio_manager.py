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

# 配置项目根目录
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量（明确指定路径）
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# 记录程序启动时间和调用次数
PROGRAM_START_TIME = datetime.now()
INVOCATION_COUNT = 0

# 使用绝对路径定义文件（按项目结构存储在data目录）
RUNTIME_FILE = os.path.join(PROJECT_ROOT, 'data', 'current_runtime.json')
PORTFOLIO_STATS_FILE = os.path.join(PROJECT_ROOT, 'data', 'portfolio_stats.json')
AI_DECISIONS_FILE = os.path.join(PROJECT_ROOT, 'data', 'ai_decisions.json')

# 配置日志
log_handler = RotatingFileHandler(
    os.path.join(PROJECT_ROOT, 'portfolio_manager.log'),
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

# 初始化客户端
deepseek_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL')
)

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

# 初始化模块（使用全局定义的路径常量）
portfolio_stats = PortfolioStatistics(PORTFOLIO_STATS_FILE, binance_client)

# 配置文件路径
config_path = os.path.join(PROJECT_ROOT, 'config', 'coins_config.json')
market_scanner = MarketScanner(binance_client, config_path)

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
            'check_interval_minutes': portfolio_rules.get('check_interval_minutes', 5),  # 从配置文件读取
            'test_mode': False  # 实盘模式
        }
    except Exception as e:
        print(f"⚠️ 加载配置失败，使用默认值: {e}")
        return {
            'leverage': 3,
            'min_cash_reserve_percent': 10,
            'check_interval_minutes': 5,
            'test_mode': False
        }

PORTFOLIO_CONFIG = load_portfolio_config()
print(f"📋 配置加载成功 - 杠杆: {PORTFOLIO_CONFIG['leverage']}x, 最低保留资金: {PORTFOLIO_CONFIG['min_cash_reserve_percent']}%")


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






def _build_kline_text(klines, title, count):
    if not klines:
        return f"【{title}】: 无数据"

    text = f"【{title}】最近 {count} 根:"
    for i, kline in enumerate(klines[-count:], 1):
        # 适配字典格式（market_scanner返回的格式）
        if isinstance(kline, dict):
            open_p = kline['open']
            high_p = kline['high']
            low_p = kline['low']
            close_p = kline['close']
            volume = kline['volume']
        else:
            # 兼容原始列表格式（币安API原始格式）
            open_p, high_p, low_p, close_p, volume = kline[1:6]

        change = ((close_p - open_p) / open_p * 100) if open_p > 0 else 0
        body = "🟢" if close_p > open_p else "🔴" if close_p < open_p else "➖"
        text += f"\n  K{i}: {body} O:{open_p} H:{high_p} L:{low_p} C:{close_p} ({change:+.2f}%) V:{volume}"
    return text

def _build_indicator_text(data, timeframe, indicators):
    text = ""
    for name, key in indicators:
        value = data.get(key)
        if value is not None:
            if isinstance(value, dict): # 处理布林带等复合指标
                value_str = f"Upper:{value.get('upper', 0):.2f}, Middle:{value.get('middle', 0):.2f}, Lower:{value.get('lower', 0):.2f}"
            else:
                value_str = f"{value:.4f}"
            text += f"- {name}: {value_str}\n"
    return text

def analyze_portfolio_with_ai(market_data, portfolio_positions, btc_data, account_info):
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
        if values is None:
            return "⚠️ 数据不可用"
        if not values or len(values) == 0:
            return "无数据"
        formatted = [f"{v:.{decimals}f}" for v in values]
        return " → ".join(formatted)
    
    # 构建BTC市场参考（加入时间序列）
    if btc_data:
        # 计算ATR百分比
        btc_price = btc_data['price']
        btc_atr_15m_pct = (btc_data['atr_15m'] / btc_price * 100) if btc_price > 0 and btc_data.get('atr_15m') else 0
        btc_atr_1h_pct = (btc_data['atr_1h'] / btc_price * 100) if btc_price > 0 and btc_data.get('atr_1h') else 0

        # 处理资金费率和持仓量可能为None的情况
        funding_rate = btc_data.get('funding_rate')
        if funding_rate is not None:
            funding_text = f"{funding_rate:.6f} {'(多头付费)' if funding_rate > 0 else '(空头付费)' if funding_rate < 0 else '(中性)'}"
        else:
            funding_text = "⚠️ 数据不可用"

        open_interest = btc_data.get('open_interest')
        if open_interest is not None:
            open_interest_text = f"{open_interest:,.0f} BTC"
        else:
            open_interest_text = "⚠️ 数据不可用"

        btc_text = f"""
    【BTC大盘】
    - 价格: ${btc_data['price']:,.2f} | 15m: {btc_data['change_15m']:+.2f}%
    - 资金费率: {funding_text}
    - 持仓量: {open_interest_text}

    15分钟周期:
    - RSI: {btc_data['rsi_15m']:.1f} | 序列: [{format_series(btc_data.get('rsi_series_15m', []), 1)}]
    - MACD: {btc_data['macd_15m']:.2f} | 序列: [{format_series(btc_data.get('macd_series_15m', []), 2)}]
    - ATR（15分钟）: ${btc_data['atr_15m']:.2f} ({btc_atr_15m_pct:.2f}%) | 序列: [{format_series(btc_data.get('atr_series_15m', []), 2)}]

    1小时周期:
    - RSI: {btc_data['rsi_1h']:.1f} | 序列: [{format_series(btc_data.get('rsi_series_1h', []), 1)}]
    - MACD: {btc_data['macd_1h']:.2f} | 序列: [{format_series(btc_data.get('macd_series_1h', []), 2)}]
    - ATR（1小时）: ${btc_data['atr_1h']:.2f} ({btc_atr_1h_pct:.2f}%) | 序列: [{format_series(btc_data.get('atr_series_1h', []), 2)}]
    - SMA20: ${btc_data['sma_20_1h']:.0f} | SMA50: ${btc_data['sma_50_1h']:.0f}

    4小时周期（轻量级）:
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
    
    # 构建各币种行情（多周期技术指标）
    market_text = "\n【各币种市场分析】"
    for coin, data in market_data.items():
        # 格式化价格
        price_display = format_price(data['price'], coin)

        # 资金费率
        funding_rate = data.get('funding_rate')
        if funding_rate is not None:
            funding_text = f"{funding_rate:.6f} {'(多头付费)' if funding_rate > 0 else '(空头付费)' if funding_rate < 0 else '(中性)'}"
        else:
            funding_text = "⚠️ 数据不可用"

        # 持仓量
        open_interest = data.get('open_interest')
        if open_interest is not None:
            open_interest_text = f"{open_interest:,.0f}"
        else:
            open_interest_text = "⚠️ 数据不可用"

        # 构建各周期文本
        kline_5m_text = _build_kline_text(data.get('kline_5m'), "5分钟K线 (执行层)", 13)
        kline_15m_text = _build_kline_text(data.get('kline_15m'), "15分钟K线 (战术层)", 16)
        kline_1h_text = _build_kline_text(data.get('kline_1h'), "1小时K线 (策略层)", 10)
        kline_4h_text = _build_kline_text(data.get('kline_4h'), "4小时K线 (战略层)", 6)

        indicators_15m_text = _build_indicator_text(data, '15m', [
            ('EMA(20)', 'ema_20_15m'), ('EMA(50)', 'ema_50_15m'),
            ('RSI(14)', 'rsi_14_15m'), ('MACD', 'macd_15m')
        ])

        indicators_1h_text = _build_indicator_text(data, '1h', [
            ('EMA(20)', 'ema_20_1h'), ('EMA(50)', 'ema_50_1h'),
            ('ATR(14)', 'atr_14_1h'), ('BBands(20,2)', 'bbands_1h')
        ])

        indicators_4h_text = _build_indicator_text(data, '4h', [
            ('EMA(20)', 'ema_20_4h'), ('EMA(50)', 'ema_50_4h'),
            ('ATR(14)', 'atr_14_4h')
        ])

        market_text += f"""

    {coin}/USDT:
    - 价格: {price_display} | 24h: {data.get('change_24h', 0):+.2f}%
    - 资金费率: {funding_text} | 持仓量: {open_interest_text}
    - 最小开仓: {data.get('min_order_value', 0)} USDT

    --- 5分钟周期 (执行层) ---
    {kline_5m_text}
    - ATR(14): {data.get('atr_14_5m', 0):.4f}

    --- 15分钟周期 (战术层) ---
    {kline_15m_text}
    {indicators_15m_text}

    --- 1小时周期 (策略层) ---
    {kline_1h_text}
    {indicators_1h_text}

    --- 4小时周期 (战略层) ---
    {kline_4h_text}
    {indicators_4h_text}
    """
    
    # 获取统计信息
    stats_text = portfolio_stats.generate_stats_text_for_ai()
    
    # 读取最近的AI决策历史（排除WAIT观望决策，避免浪费Token）
    last_decisions_text = ""
    try:
        if os.path.exists(AI_DECISIONS_FILE):
            with open(AI_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                decisions_data = json.load(f)
                all_decisions = decisions_data.get('decisions', [])
                # 过滤掉WAIT决策，只保留实际操作
                recent_decisions = [d for d in all_decisions if d.get('action') != 'WAIT'][-3:]
                
                if recent_decisions:
                    last_decisions_text = "\n【最近AI决策记录】（最近实际操作）"
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

    # 加载外部提示词（策略和理念）
    external_prompt = ""
    try:
        prompt_file = os.path.join(PROJECT_ROOT, 'prompts', 'default.txt')
        with open(prompt_file, 'r', encoding='utf-8') as f:
            external_prompt = f.read()
    except FileNotFoundError:
        print("⚠️ 外部提示词文件不存在，使用默认配置")
        external_prompt = ""
    except Exception as e:
        print(f"⚠️ 读取外部提示词失败: {e}")
        external_prompt = ""

    # 动态生成币种最小限制说明（从配置文件读取）
    coin_limits = []
    for coin_info in market_scanner.coins_config['coins']:
        coin_limits.append(f"{coin_info['symbol']} {coin_info['min_order_value']}")
    coin_limits_text = " | ".join(coin_limits)

    # 构建 User Message（仅包含变化的数据）
    user_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 系统运行状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 程序启动: {PROGRAM_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}
⏰ 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
⏱️  已运行: {runtime_text} | 第 {INVOCATION_COUNT} 次调用
📊 数据顺序: 所有时间序列从旧到新（最旧 → 最新）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 当前资金状况
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 账户总资产: {account_info['total_balance']:.2f} USDT
- 已用保证金: {account_info['used_margin']:.2f} USDT
- 剩余可用余额: {account_info['free_balance']:.2f} USDT
- 保证金使用率: {account_info['margin_ratio']:.2f}%
- 当前杠杆: {PORTFOLIO_CONFIG['leverage']}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 市场数据
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{btc_text}

{portfolio_text}

{stats_text}

{last_decisions_text}

{market_text}
"""

    try:
        # 构建 System Message（身份 + 策略 + 格式规则，不变的内容）
        system_message = f"""您是专业的加密货币投资组合经理(Portfolio Manager)。

{external_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 返回格式要求（JSON）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
格式示例：
{{{{
  "decisions": [
    {{{{
      "coin": "ETH",
      "action": "OPEN_LONG | OPEN_SHORT | CLOSE | ADD | HOLD",
      "reason": "K线形态 | 技术指标说明",
      "position_value": 100,
      "stop_loss": 3200.5,
      "take_profit": 3500.0
    }}}}
  ],
  "strategy": "整体策略说明",
  "risk_level": "LOW | MEDIUM | HIGH",
  "confidence": "LOW | MEDIUM | HIGH"
}}}}

⚠️ 语言要求（重要）：
- 所有文本字段（reason、strategy）必须使用简体中文
- 保持简洁专业，每个 reason 不超过 80 字
- 避免冗长描述和重复内容

⚠️ 字段说明：
- action: 操作类型（OPEN_LONG/OPEN_SHORT/CLOSE/ADD/HOLD）
- reason: 必须包含K线形态+技术指标，简洁明了
- position_value: 持仓价值（USDT），HOLD/CLOSE时填0
- stop_loss/take_profit: 必填具体价格（CLOSE时可填0）
- decisions为空数组时表示观望

💡 移动止损机制（重要）：
当您想要移动止损时，只需在HOLD操作中填入新的stop_loss价格即可。
示例：
{{{{
  "coin": "BTC",
  "action": "HOLD",
  "stop_loss": 45000,
  "take_profit": 50000,
  "reason": "已盈利5%，上移止损至45000保护利润"
}}}}
系统会自动：
1. 取消旧的止损订单
2. 创建新的止损订单
您无需做任何额外操作，只需提供新价格。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 硬性规则（系统限制，必须遵守）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 资金保护（重要）：
   - 必须保留至少 10% 的账户总资产作为手续费和风险缓冲
   - 最大可用保证金 = 账户总资产 × 90% - 已用保证金
   - 示例：总资产 100 USDT，已用 50 USDT → 最多还能用 40 USDT (100×0.9-50)
   - 这是为了确保有足够资金支付手续费和应对突发波动

2. 杠杆固定：当前使用 {PORTFOLIO_CONFIG['leverage']}x 杠杆，由系统管理，无需考虑调整

3. 最小开仓金额（position_value，杠杆后的金额）：
   - 🔒 全局限制：任何币种不得低于 13 USDT（硬编码，不可突破）
   - 币种限制：{coin_limits_text}
   - 实际生效：取两者中的较大值

4. 止损必填：所有开仓（OPEN_LONG/OPEN_SHORT）和持仓（HOLD）必须提供止损价格

请基于用户消息中的数据和上述策略进行分析，严格按JSON格式返回决策。"""

        response = deepseek_client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat'),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            stream=False,
            temperature=0.3,
            timeout=120  # 120秒超时，避免长时间等待
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
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            print(f"⚠️ AI调用超时（120秒），本次跳过决策（HOLD）")
            return {'decisions': [], 'strategy': 'AI服务超时，保持观望', 'risk_level': 'HIGH', 'confidence': 'LOW'}
        else:
            print(f"❌ AI分析失败: {e}")
            return {'decisions': [], 'strategy': 'AI服务异常，保持观望', 'risk_level': 'HIGH', 'confidence': 'LOW'}


def calculate_position_size(coin, position_value, current_price, coin_config):
    """计算交易数量"""
    try:
        # 全局最小金额硬编码（安全底线）
        GLOBAL_MIN_ORDER_VALUE = 13  # USDT

        if position_value < GLOBAL_MIN_ORDER_VALUE:
            print(f"⚠️ {coin}: {position_value:.2f} USDT < 全局最小限制 {GLOBAL_MIN_ORDER_VALUE} USDT（硬编码）")
            return 0

        precision = coin_config['precision']
        min_order_value = coin_config['min_order_value']

        if position_value < min_order_value:
            print(f"⚠️ {coin}: {position_value:.2f} USDT < 币种最小限制 {min_order_value} USDT")
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
    strategy = decisions_data.get('strategy', '')
    risk_level = decisions_data.get('risk_level', 'UNKNOWN')
    confidence = decisions_data.get('confidence', 'UNKNOWN')
    
    if not decisions_data or not decisions_data.get('decisions'):
        print("💤 AI决定观望，不执行交易")
        # 记录观望决策到看板（但不传递给下一次AI）
        save_ai_decision(
            coin='ALL',
            action='WAIT',
            reason=strategy if strategy else '市场观望',
            strategy=strategy,
            risk_level=risk_level,
            confidence=confidence
        )
        return
    
    decisions = decisions_data['decisions']
    
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

                        # 使用"先建后删"策略，确保始终有止损保护
                        new_stop_order = None
                        try:
                            # 1. 先下新止损单
                            side_for_stop = 'SELL' if current_position['side'] == 'long' else 'BUY'
                            amount_for_stop = current_position['amount']
                            price_precision = coin_info.get('price_precision', 2)

                            new_stop_order = binance_client.futures_create_order(
                                symbol=symbol,
                                side=side_for_stop,
                                type='STOP_MARKET',
                                stopPrice=round(stop_loss, price_precision),
                                closePosition=True,  # 使用closePosition而不是quantity
                                workingType='MARK_PRICE'
                            )
                            stop_order_id = new_stop_order.get('orderId', 0)
                            print(f"   ✅ 新止损单已下: {format_price(stop_loss, coin)} (订单ID: {stop_order_id})")

                            # 2. 新止损单成功后，再取消旧止损单
                            portfolio_stats.cancel_stop_loss_order(coin, symbol)
                            print(f"   ✅ 旧止损单已取消")

                        except Exception as e:
                            print(f"   ❌ 调整止损失败: {str(e)[:100]}")
                            # 如果新止损单已创建但后续步骤失败，尝试回滚
                            if new_stop_order and 'orderId' in new_stop_order:
                                try:
                                    binance_client.futures_cancel_order(symbol=symbol, orderId=new_stop_order['orderId'])
                                    print(f"   ↩️ 已回滚新止损单")
                                except:
                                    print(f"   ⚠️ 回滚失败，可能同时存在两个止损单，请手动检查")
                            # 保持旧止损单不变
                            stop_order_id = current_position.get('stop_order_id', 0)

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
                    
                    # 3. 记录平仓
                    portfolio_stats.record_trade_exit(coin, current_price, 'ai_decision')
                    print(f"✅ {coin} 平仓成功")
                else:
                    print(f"⚠️ {coin} 无持仓，跳过平仓")
            
            elif action in ['OPEN_LONG', 'OPEN_SHORT', 'ADD']:
                amount = calculate_position_size(coin, position_value, current_price, coin_info)
                
                if amount > 0:
                    if action == 'OPEN_LONG' or (action == 'ADD' and current_position and current_position['side'] == 'long'):
                        print(f"📈 {'开' if action == 'OPEN_LONG' else '加'}多仓: {amount} {coin} (${position_value:.2f})")
                        
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
                        if action == 'OPEN_LONG':
                            portfolio_stats.record_position_entry(coin, 'long', current_price, amount, stop_loss, take_profit, stop_order_id)
                        
                        print(f"✅ {coin} 多仓成功")
                    
                    elif action == 'OPEN_SHORT' or (action == 'ADD' and current_position and current_position['side'] == 'short'):
                        print(f"📉 {'开' if action == 'OPEN_SHORT' else '加'}空仓: {amount} {coin} (${position_value:.2f})")
                        
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
                        if action == 'OPEN_SHORT':
                            portfolio_stats.record_position_entry(coin, 'short', current_price, amount, stop_loss, take_profit, stop_order_id)
                        
                        print(f"✅ {coin} 空仓成功")
                else:
                    print(f"⚠️ {coin} 数量计算为0，跳过")
            
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
                if market_data and 'price' in market_data:
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


def portfolio_bot():
    """投资组合机器人主循环"""
    print("\n" + "="*60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. 扫描市场（获取所有周期数据）
    print("📊 扫描所有市场，获取多周期数据...")
    market_data = market_scanner.scan_all_markets()
    if not market_data:
        print("❌ 市场数据获取失败")
        return
    
    # 2. 获取BTC背景
    btc_data = market_scanner.get_btc_context()
    
    # 3. 获取持仓
    portfolio_positions = market_scanner.get_portfolio_positions()
    
    # 4. 获取账户信息
    account_info = market_scanner.get_account_info()
    
    # 5. AI分析 (移除 long_term_data)
    decisions_data = analyze_portfolio_with_ai(market_data, portfolio_positions, btc_data, account_info)
    
    # 6. 执行决策
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

