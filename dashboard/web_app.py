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

# 添加父目录到路径，以便导入market_scanner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from market_scanner import MarketScanner
    from binance.client import Client
    from dotenv import load_dotenv
    
    # 加载环境变量（使用duobizhong目录下的.env）
    load_dotenv('/root/DS/duobizhong/.env')
    
    # 初始化币安客户端（只用于获取公开市场数据）
    binance_client = Client(
        api_key=os.getenv('BINANCE_API_KEY'),
        api_secret=os.getenv('BINANCE_SECRET')
    )
    
    # 初始化市场扫描器
    market_scanner = MarketScanner(binance_client, '../config/coins_config.json')
    SCANNER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 警告: 市场扫描器初始化失败: {e}")
    print("前端将只显示历史数据，不显示实时价格")
    SCANNER_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# 配置
STATS_FILE = '../portfolio_stats.json'
AI_DECISIONS_FILE = '../ai_decisions.json'
RUNTIME_FILE = '../current_runtime.json'

# 记录Web服务启动时间
WEB_START_TIME = datetime.now()

def load_json_file(filepath):
    """安全地加载JSON文件"""
    try:
        full_path = os.path.join(os.path.dirname(__file__), filepath)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
        return None

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
    """获取当前持仓 - 直接从币安API读取"""
    if not SCANNER_AVAILABLE:
        return jsonify({'error': '币安客户端不可用'}), 503
    
    try:
        # 直接调用币安API获取持仓信息
        binance_positions = binance_client.futures_position_information()
        
        # 加载本地记录（用于获取止损止盈信息）
        stats = load_json_file(STATS_FILE)
        local_positions = stats.get('current_positions', {}) if stats else {}
        
        positions = []
        total_unrealized_pnl = 0
        
        # 币种映射（币安symbol转币种名）
        symbol_to_coin = {
            'BNBUSDC': 'BNB',
            'ETHUSDC': 'ETH',
            'SOLUSDC': 'SOL',
            'XRPUSDC': 'XRP',
            'DOGEUSDC': 'DOGE'
        }
        
        # 遍历币安持仓
        for pos in binance_positions:
            amount = float(pos['positionAmt'])
            if abs(amount) > 0:  # 有持仓
                symbol = pos['symbol']
                coin = symbol_to_coin.get(symbol)
                
                if coin:  # 如果是我们关注的币种
                    entry_price = float(pos['entryPrice'])
                    pnl = float(pos['unRealizedProfit'])
                    mark_price = float(pos['markPrice'])
                    
                    total_unrealized_pnl += pnl
                    
                    # 从本地记录获取止损止盈和开仓时间
                    local_pos = local_positions.get(coin, {})
                    if local_pos:
                        stop_loss = local_pos.get('stop_loss', 0)
                        take_profit = local_pos.get('take_profit', 0)
                        stop_order_id = local_pos.get('stop_order_id', 0)
                        entry_time = local_pos.get('entry_time', '')
                    else:
                        stop_loss = 0
                        take_profit = 0
                        stop_order_id = 0
                        entry_time = ''
                    
                    # 根据币种设置合适的价格精度
                    # DOGE和XRP价格低，需要更多小数位
                    if coin in ['DOGE', 'XRP']:
                        price_decimals = 5
                    else:
                        price_decimals = 2
                    
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
            'total_unrealized_pnl': round(total_unrealized_pnl, 2)
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
        coins = ['BTC', 'BNB', 'ETH', 'SOL', 'XRP', 'DOGE']
        
        for coin in coins:
            try:
                if coin == 'BTC':
                    ticker = binance_client.get_symbol_ticker(symbol='BTCUSDC')
                else:
                    ticker = binance_client.get_symbol_ticker(symbol=f'{coin}USDC')
                
                prices[coin] = {
                    'price': float(ticker['price']),
                    'symbol': coin
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
    """获取账户信息 - 直接从币安API读取"""
    if not SCANNER_AVAILABLE:
        return jsonify({'error': '币安客户端不可用'}), 503
    
    try:
        # 直接调用币安API获取账户信息
        account = binance_client.futures_account()
        
        # 提取关键信息
        total_balance = float(account.get('totalWalletBalance', 0))
        available_balance = float(account.get('availableBalance', 0))
        used_margin = float(account.get('totalInitialMargin', 0))
        
        # 计算保证金占用率
        margin_ratio = (used_margin / total_balance * 100) if total_balance > 0 else 0
        
        return jsonify({
            'total_balance': round(total_balance, 2),
            'free_balance': round(available_balance, 2),
            'used_margin': round(used_margin, 2),
            'margin_ratio': round(margin_ratio, 1)
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
    app.run(host='127.0.0.1', port=5000, debug=False)

