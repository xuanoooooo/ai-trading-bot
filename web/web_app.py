import json
import os
import shutil
import time
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import ccxt
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

app = Flask(__name__, static_folder='dist', static_url_path='/')
CORS(app) # Enable CORS for all routes

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'coins_config.json')
PORTFOLIO_STATS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'portfolio_stats.json')
AI_DECISIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai_decisions.json')
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts')
DEFAULT_PROMPT_FILE = os.path.join(PROMPTS_DIR, 'default.txt')

# Initialize exchange client (read from config)
exchange = None
try:
    # Read exchange name from config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            exchange_name = config.get('exchange', 'binance').lower()
    else:
        exchange_name = 'binance'
    
    # 根据交易所名称读取对应的API密钥
    api_key_name = f"{exchange_name.upper()}_API_KEY"
    api_secret_name = f"{exchange_name.upper()}_SECRET"
    api_key = os.getenv(api_key_name)
    api_secret = os.getenv(api_secret_name)
    
    if api_key and api_secret:
        exchange_class = getattr(ccxt, exchange_name)
        
        # 基础配置
        exchange_config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {}
        }
        
        # 不同交易所的特殊配置
        if exchange_name == 'binance':
            exchange_config['options'] = {
                'defaultType': 'future',
            }
        elif exchange_name == 'gateio':
            exchange_config['options'] = {
                'defaultType': 'swap',
            }
        elif exchange_name == 'okx':
            exchange_config['options'] = {
                'defaultType': 'swap',
            }
            password = os.getenv('OKX_PASSWORD')
            if password:
                exchange_config['password'] = password
        elif exchange_name == 'bybit':
            exchange_config['options'] = {
                'defaultType': 'linear',
            }
        else:
            exchange_config['options'] = {
                'defaultType': 'swap',
            }
        
        exchange = exchange_class(exchange_config)
        exchange.load_markets()
        print(f"✅ {exchange_name.upper()} Exchange initialized in Web App")
    else:
        print(f"⚠️ {exchange_name.upper()} credentials not found in .env")
        print(f"   Please set {api_key_name} and {api_secret_name}")
except Exception as e:
    print(f"⚠️ Failed to initialize Exchange: {e}")

# Cache for account info
cached_account_info = None
last_account_update = 0
CACHE_DURATION = 10  # seconds

# Helper function to read JSON files
def read_json_file(file_path, default_value={}):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_value

def get_realtime_account_info():
    """Get account info from exchange with caching"""
    global cached_account_info, last_account_update
    
    if not exchange:
        return None
        
    now = time.time()
    if cached_account_info and (now - last_account_update < CACHE_DURATION):
        return cached_account_info
        
    try:
        balance = exchange.fetch_balance({'type': 'future'})
        total_balance = balance['total'].get('USDT', 0)
        free_balance = balance['free'].get('USDT', 0)
        
        # Get all positions to calculate unrealized PnL
        positions = exchange.fetch_positions()
        total_unrealized_pnl = sum(
            float(pos.get('unrealizedPnl', 0) or 0) 
            for pos in positions 
            if float(pos.get('contracts', 0) or 0) != 0
        )
        
        cached_account_info = {
            'total_balance': total_balance,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_equity': total_balance + total_unrealized_pnl,
            'available_balance': free_balance
        }
        last_account_update = now
        return cached_account_info
    except Exception as e:
        print(f"⚠️ Exchange API Error: {e}")
        return None

# Serve React App
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# API to get configuration
@app.route('/api/config', methods=['GET'])
def get_config():
    config = read_json_file(CONFIG_FILE)
    return jsonify(config)

# API to update configuration
@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return jsonify({"message": "Configuration updated successfully", "config": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to list all prompt files
@app.route('/api/prompts/list', methods=['GET'])
def list_prompts():
    try:
        files = [f for f in os.listdir(PROMPTS_DIR) if f.endswith('.txt')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to get prompt content
@app.route('/api/prompts/content', methods=['GET'])
def get_prompt_content():
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Filename required"}), 400
    
    if '..' in filename or '/' in filename:
        return jsonify({"error": "Invalid filename"}), 400
        
    filepath = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to save prompt content
@app.route('/api/prompts/save', methods=['POST'])
def save_prompt():
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({"error": "Filename and content required"}), 400
        
    filename = data['filename']
    content = data['content']
    
    if not filename.endswith('.txt'):
        filename += '.txt'
        
    if '..' in filename or '/' in filename:
        return jsonify({"error": "Invalid filename"}), 400
        
    filepath = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"message": "Prompt saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to activate prompt
@app.route('/api/prompts/activate', methods=['POST'])
def activate_prompt():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Filename required"}), 400
        
    filename = data['filename']
    
    if '..' in filename or '/' in filename:
        return jsonify({"error": "Invalid filename"}), 400
        
    source_path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(source_path):
        return jsonify({"error": "Source file not found"}), 404
        
    try:
        shutil.copy2(source_path, DEFAULT_PROMPT_FILE)
        return jsonify({"message": f"Prompt '{filename}' activated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Get positions
@app.route('/api/positions', methods=['GET'])
def get_positions():
    # For positions, we still rely on the file for now as it contains PnL logic
    # But we could also fetch from Binance if we wanted to be 100% realtime
    # To keep it simple and consistent with trade history, we'll stick to file for positions list
    # or we could mix them. Let's stick to file for positions to ensure consistency with strategy.
    # If you want realtime positions, we can change this too.
    
    stats = read_json_file(PORTFOLIO_STATS_FILE)
    current_positions = stats.get('current_positions', {})
    
    # Format for frontend
    positions_list = []
    if current_positions:
        for coin, pos in current_positions.items():
            if pos:
                # Calculate realtime PnL if we wanted, but for now use stored
                # To do it properly, we'd need current prices.
                positions_list.append({
                    'symbol': coin,
                    'amount': pos.get('amount', 0),
                    'entryPrice': pos.get('entry_price', 0),
                    'currentPrice': 0, # Frontend doesn't strictly need this if PnL is there
                    'pnl': pos.get('pnl', 0),
                    'side': pos.get('side', 'long')
                })
                
    return jsonify({"positions": positions_list})

# API: Get portfolio statistics (Mixed Source)
@app.route('/api/stats', methods=['GET'])
def get_stats():
    # 1. Load from file
    stats = read_json_file(PORTFOLIO_STATS_FILE)
    
    # 2. Try to get realtime data
    realtime_info = get_realtime_account_info()
    
    response_data = {
        'total_trades': stats.get('total_trades', 0),
        'win_trades': stats.get('win_trades', 0),
        'lose_trades': stats.get('lose_trades', 0),
        'total_pnl': stats.get('total_pnl', 0.0), # Historical PnL (Realized)
        
        # Default to file data if realtime fails
        'total_balance': stats.get('total_balance', 0.0),
        'total_unrealized_pnl': 0.0 
    }
    
    # 3. Override with realtime data if available
    if realtime_info:
        response_data['total_balance'] = realtime_info['total_equity'] # Use Equity as Total Balance
        response_data['total_unrealized_pnl'] = realtime_info['total_unrealized_pnl']
        response_data['available_balance'] = realtime_info['available_balance']
        
    return jsonify(response_data)

# API: Get AI decisions
@app.route('/api/ai_decisions', methods=['GET'])
def get_ai_decisions():
    decisions = read_json_file(AI_DECISIONS_FILE, default_value={'decisions': []})
    return jsonify(decisions)

@app.errorhandler(404)
def not_found(e):
    if not request.path.startswith('/api/'):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    # Ensure necessary data files exist
    if not os.path.exists(PORTFOLIO_STATS_FILE):
        os.makedirs(os.path.dirname(PORTFOLIO_STATS_FILE), exist_ok=True)
        with open(PORTFOLIO_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
    if not os.path.exists(AI_DECISIONS_FILE):
        os.makedirs(os.path.dirname(AI_DECISIONS_FILE), exist_ok=True)
        with open(AI_DECISIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'decisions': []}, f, indent=2, ensure_ascii=False)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
