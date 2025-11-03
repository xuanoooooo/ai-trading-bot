"""
AI交易机器人可视化Web服务
- 只读取数据，不执行交易
- 独立运行，不影响交易程序
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# 添加父目录到路径，以便导入src模块
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# 配置文件路径与执行模式
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config', 'coins_config.json')
CONFIG_DATA = {}
PORTFOLIO_RULES = {}
EXECUTION_MODE = 'live'
COIN_SYMBOL_MAP = {}
SYMBOL_TO_COIN = {}

def _load_config():
    global CONFIG_DATA, PORTFOLIO_RULES, EXECUTION_MODE, COIN_SYMBOL_MAP, SYMBOL_TO_COIN
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            CONFIG_DATA = json.load(f)
            PORTFOLIO_RULES = CONFIG_DATA.get('portfolio_rules', {}) or {}
            EXECUTION_MODE = PORTFOLIO_RULES.get('execution_mode', 'live').lower()
            COIN_SYMBOL_MAP = {}
            SYMBOL_TO_COIN = {}
            for coin_cfg in CONFIG_DATA.get('coins', []):
                coin = coin_cfg.get('symbol')
                symbol = coin_cfg.get('binance_symbol')
                if coin and symbol:
                    COIN_SYMBOL_MAP[coin] = symbol
                    SYMBOL_TO_COIN[symbol] = coin
                    if symbol.endswith('USDT'):
                        SYMBOL_TO_COIN.setdefault(symbol.replace('USDT', 'USDC'), coin)
    except Exception as e:
        print(f"⚠️ 无法加载配置文件 {CONFIG_PATH}: {e}")
        CONFIG_DATA = {}
        PORTFOLIO_RULES = {}
        EXECUTION_MODE = 'live'
        COIN_SYMBOL_MAP = {}
        SYMBOL_TO_COIN = {}

_load_config()

if not COIN_SYMBOL_MAP:
    default_map = {
        'BTC': 'BTCUSDT',
        'ETH': 'ETHUSDT',
        'BNB': 'BNBUSDT',
        'SOL': 'SOLUSDT',
        'XRP': 'XRPUSDT',
        'ADA': 'ADAUSDT',
        'DOGE': 'DOGEUSDT'
    }
    COIN_SYMBOL_MAP.update(default_map)
    for coin, symbol in default_map.items():
        SYMBOL_TO_COIN.setdefault(symbol, coin)
        if symbol.endswith('USDT'):
            SYMBOL_TO_COIN.setdefault(symbol.replace('USDT', 'USDC'), coin)

try:
    from src.market_scanner import MarketScanner
    from binance.client import Client
    from dotenv import load_dotenv
    
    # 加载环境变量（自动从当前目录或父目录查找.env文件）
    load_dotenv()
    
    # 如果找不到，尝试从项目根目录加载
    if not os.getenv('BINANCE_API_KEY'):
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
    
    # 初始化币安客户端（只用于获取公开市场数据）
    binance_client = Client(
        api_key=os.getenv('BINANCE_API_KEY'),
        api_secret=os.getenv('BINANCE_SECRET')
    )
    
    # 配置文件路径（兼容不同运行目录）
    market_scanner = MarketScanner(binance_client, CONFIG_PATH)
    SCANNER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 警告: 市场扫描器初始化失败: {e}")
    print("前端将只显示历史数据，不显示实时价格")
    SCANNER_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# 配置 - 使用绝对路径定位数据文件（这些文件由src/portfolio_manager.py生成）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(PROJECT_ROOT, 'src/portfolio_stats.json')
AI_DECISIONS_FILE = os.path.join(PROJECT_ROOT, 'src/ai_decisions.json')
RUNTIME_FILE = os.path.join(PROJECT_ROOT, 'src/current_runtime.json')

# 记录Web服务启动时间
WEB_START_TIME = datetime.now()

def load_json_file(filepath):
    """安全地加载JSON文件"""
    try:
        # 如果是绝对路径，直接使用；否则相对于项目根目录
        if os.path.isabs(filepath):
            full_path = filepath
        else:
            full_path = os.path.join(PROJECT_ROOT, filepath)
            
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ 文件不存在: {full_path}")
        return None
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
        return None


def fetch_mark_price(symbol: str) -> float:
    """获取合约标记价格（用于dry-run计算盈亏）"""
    if not symbol or not SCANNER_AVAILABLE:
        return 0.0
    try:
        mark = binance_client.futures_mark_price(symbol=symbol)
        return float(mark.get('markPrice', 0))
    except Exception:
        try:
            ticker = binance_client.futures_symbol_ticker(symbol=symbol)
            return float(ticker.get('price', 0))
        except Exception:
            return 0.0

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/runtime')
def get_runtime():
    """获取Web服务和交易程序的运行状态"""
    # 尝试读取当前运行状态（本次运行）
    runtime_data = load_json_file(RUNTIME_FILE)
    current_start_time = None
    current_runtime_text = "未运行"
    current_invocations = 0
    
    if runtime_data:
        try:
            current_start_time = datetime.fromisoformat(runtime_data['program_start_time'])
            current_invocations = runtime_data.get('invocation_count', 0)
            
            # 计算本次运行时长
            current_runtime = datetime.now() - current_start_time
            current_minutes = int(current_runtime.total_seconds() / 60)
            current_hours = current_minutes / 60
            
            if current_hours < 1:
                current_runtime_text = f"{current_minutes}分钟"
            else:
                current_runtime_text = f"{current_hours:.1f}小时 ({current_minutes}分钟)"
        except:
            pass
    
    # 读取累计运行时长（从stats文件）
    stats = load_json_file(STATS_FILE)
    total_start_time = None
    total_runtime_text = "未运行"
    
    if stats and 'start_time' in stats:
        try:
            total_start_time = datetime.fromisoformat(stats['start_time'])
            total_runtime = datetime.now() - total_start_time
            total_minutes = int(total_runtime.total_seconds() / 60)
            total_hours = total_minutes / 60
            
            if total_hours < 1:
                total_runtime_text = f"{total_minutes}分钟"
            else:
                total_runtime_text = f"{total_hours:.1f}小时 ({total_minutes}分钟)"
        except:
            pass
    
    return jsonify({
        # 本次运行（从current_runtime.json读取）
        'current_start_time': current_start_time.strftime('%Y-%m-%d %H:%M:%S') if current_start_time else None,
        'current_runtime': current_runtime_text,
        'current_invocations': current_invocations,
        # 累计运行（从portfolio_stats.json读取）
        'total_start_time': total_start_time.strftime('%Y-%m-%d %H:%M:%S') if total_start_time else None,
        'total_runtime': total_runtime_text,
        # 当前时间
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/stats')
def get_stats():
    """获取统计数据"""
    stats = load_json_file(STATS_FILE)
    if not stats:
        return jsonify({'error': '无法加载统计数据'}), 500
    
    # 计算运行时长
    start_time = datetime.fromisoformat(stats.get('start_time', datetime.now().isoformat()))
    runtime = datetime.now() - start_time
    runtime_hours = int(runtime.total_seconds() / 3600)
    runtime_days = runtime_hours // 24
    runtime_hours_in_day = runtime_hours % 24
    
    # 计算胜率
    total_trades = stats.get('total_trades', 0)
    win_trades = stats.get('win_trades', 0)
    win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
    
    return jsonify({
        'total_trades': total_trades,
        'win_trades': win_trades,
        'lose_trades': stats.get('lose_trades', 0),
        'win_rate': round(win_rate, 1),
        'total_pnl': round(stats.get('total_pnl', 0), 2),
        'runtime_days': runtime_days,
        'runtime_hours': runtime_hours_in_day,
        'start_time': stats.get('start_time'),
        'last_update': stats.get('last_update')
    })

@app.route('/api/positions')
def get_positions():
    """获取当前持仓"""
    stats = load_json_file(STATS_FILE)
    local_positions = stats.get('current_positions', {}) if stats else {}
    
    if EXECUTION_MODE == 'dry_run':
        positions = []
        total_unrealized_pnl = 0.0
        for coin, pos in (local_positions or {}).items():
            if not pos:
                continue
            symbol = COIN_SYMBOL_MAP.get(coin, f"{coin}USDT")
            entry_price = float(pos.get('entry_price', 0) or 0)
            amount = float(pos.get('amount', 0) or 0)
            side = pos.get('side', '')
            mark_price = fetch_mark_price(symbol) or entry_price
            
            pnl = 0.0
            if entry_price and amount:
                if side == 'long':
                    pnl = (mark_price - entry_price) * amount
                elif side == 'short':
                    pnl = (entry_price - mark_price) * amount
            
            total_unrealized_pnl += pnl
            price_decimals = 5 if coin in ['DOGE', 'XRP'] else 2
            positions.append({
                'coin': coin,
                'side': side,
                'entry_price': round(entry_price, price_decimals),
                'amount': round(amount, 8),
                'entry_time': pos.get('entry_time', ''),
                'pnl': round(pnl, 2),
                'current_price': round(mark_price, price_decimals),
                'stop_loss': pos.get('stop_loss', 0),
                'take_profit': pos.get('take_profit', 0),
                'stop_order_id': pos.get('stop_order_id', 0)
            })
        
        return jsonify({
            'positions': positions,
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'mode': 'dry_run'
        })
    
    if not SCANNER_AVAILABLE:
        return jsonify({'error': '币安客户端不可用'}), 503
    
    try:
        binance_positions = binance_client.futures_position_information()
        positions = []
        total_unrealized_pnl = 0.0
        for pos in binance_positions:
            amount = float(pos.get('positionAmt', 0))
            if abs(amount) < 1e-8:
                continue
            symbol = pos.get('symbol')
            coin = SYMBOL_TO_COIN.get(symbol)
            if not coin:
                # 兼容 symbol → coin 匹配失败的情况
                if symbol and symbol.endswith('USDT'):
                    coin = symbol.replace('USDT', '')
                elif symbol and symbol.endswith('USDC'):
                    coin = symbol.replace('USDC', '')
            if not coin:
                continue
            
            entry_price = float(pos.get('entryPrice', 0))
            pnl = float(pos.get('unRealizedProfit', 0))
            mark_price = float(pos.get('markPrice', entry_price))
            total_unrealized_pnl += pnl
            
            local_pos = local_positions.get(coin, {}) if local_positions else {}
            stop_loss = local_pos.get('stop_loss', 0)
            take_profit = local_pos.get('take_profit', 0)
            stop_order_id = local_pos.get('stop_order_id', 0)
            entry_time = local_pos.get('entry_time', '')
            
            price_decimals = 5 if coin in ['DOGE', 'XRP'] else 2
            positions.append({
                'coin': coin,
                'side': 'long' if amount > 0 else 'short',
                'entry_price': round(entry_price, price_decimals),
                'amount': abs(amount),
                'entry_time': entry_time,
                'pnl': round(pnl, 2),
                'current_price': round(mark_price, price_decimals),
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'stop_order_id': stop_order_id
            })
        
        return jsonify({
            'positions': positions,
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'mode': 'live'
        })
    except Exception as e:
        print(f"❌ 获取持仓信息失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """获取交易历史"""
    stats = load_json_file(STATS_FILE)
    if not stats:
        return jsonify({'error': '无法加载交易历史'}), 500
    
    # 获取所有交易历史（用于绘制完整的盈亏曲线）
    trade_history = stats.get('trade_history', [])
    all_trades = trade_history[::-1]  # 倒序，最新的在前
    
    return jsonify({'trades': all_trades})

@app.route('/api/prices')
def get_prices():
    """获取实时价格"""
    if not SCANNER_AVAILABLE:
        return jsonify({'error': '市场扫描器不可用'}), 503
    
    try:
        prices = {}
        for coin, symbol in COIN_SYMBOL_MAP.items():
            try:
                ticker = binance_client.get_symbol_ticker(symbol=symbol)
                prices[coin] = {
                    'price': float(ticker['price']),
                    'symbol': symbol
                }
            except:
                pass
        
        return jsonify({'prices': prices})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_decisions')
def get_ai_decisions():
    """获取AI决策日志"""
    decisions = load_json_file(AI_DECISIONS_FILE)
    if not decisions:
        return jsonify({'decisions': []})
    
    # 获取最近10条决策
    recent_decisions = decisions.get('decisions', [])[-10:][::-1]
    
    return jsonify({'decisions': recent_decisions})

@app.route('/api/account')
def get_account():
    """获取账户信息"""
    stats = load_json_file(STATS_FILE)
    
    if EXECUTION_MODE == 'dry_run':
        if not stats:
            return jsonify({'error': 'dry_run 统计数据不可用'}), 500
        
        dry_cfg = PORTFOLIO_RULES.get('dry_run', {}) if PORTFOLIO_RULES else {}
        initial_balance = float(dry_cfg.get('initial_balance', 2000))
        leverage = float(PORTFOLIO_RULES.get('leverage', 3)) if PORTFOLIO_RULES else 3.0
        leverage = leverage if leverage > 0 else 1.0
        
        current_positions = stats.get('current_positions', {}) or {}
        total_pnl = float(stats.get('total_pnl', 0) or 0)
        
        used_margin = 0.0
        unrealized = 0.0
        for coin, pos in current_positions.items():
            if not pos:
                continue
            entry_price = float(pos.get('entry_price', 0) or 0)
            amount = float(pos.get('amount', 0) or 0)
            if entry_price <= 0 or amount <= 0:
                continue
            symbol = COIN_SYMBOL_MAP.get(coin, f"{coin}USDT")
            mark_price = fetch_mark_price(symbol) or entry_price
            side = pos.get('side', 'long')
            used_margin += (entry_price * amount) / leverage
            if side == 'long':
                unrealized += (mark_price - entry_price) * amount
            else:
                unrealized += (entry_price - mark_price) * amount
        
        total_balance = initial_balance + total_pnl + unrealized
        available_balance = max(total_balance - used_margin, 0.0)
        margin_ratio = (used_margin / total_balance * 100) if total_balance > 0 else 0.0
        
        return jsonify({
            'total_balance': round(total_balance, 2),
            'free_balance': round(available_balance, 2),
            'used_margin': round(used_margin, 2),
            'margin_ratio': round(margin_ratio, 1),
            'mode': 'dry_run'
        })
    
    if not SCANNER_AVAILABLE:
        return jsonify({'error': '币安客户端不可用'}), 503
    
    try:
        account = binance_client.futures_account()
        total_balance = float(account.get('totalWalletBalance', 0))
        available_balance = float(account.get('availableBalance', 0))
        used_margin = float(account.get('totalInitialMargin', 0))
        margin_ratio = (used_margin / total_balance * 100) if total_balance > 0 else 0
        return jsonify({
            'total_balance': round(total_balance, 2),
            'free_balance': round(available_balance, 2),
            'used_margin': round(used_margin, 2),
            'margin_ratio': round(margin_ratio, 1),
            'mode': 'live'
        })
    except Exception as e:
        print(f"❌ 获取账户信息失败: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI交易机器人可视化系统")
    print("=" * 60)
    print(f"📊 数据文件: {STATS_FILE}")
    print(f"🤖 AI决策日志: {AI_DECISIONS_FILE}")
    print(f"🔒 监听地址: 127.0.0.1:5000 (仅本地访问)")
    print(f"🌐 访问方式: SSH隧道 - ssh -L 5000:localhost:5000 user@server")
    print(f"   然后浏览器访问: http://localhost:5000")
    print(f"⚠️  注意: 此服务只读取数据，不执行交易")
    print("=" * 60)
    
    # 启动Flask应用（仅监听本地）
    app.run(host='0.0.0.0', port=5000, debug=False)
