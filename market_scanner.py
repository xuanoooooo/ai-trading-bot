"""
市场扫描器 - 获取所有币种的市场数据和技术指标
复用 deepseekBNB_stats.py 的技术指标计算逻辑
"""
import pandas as pd
from binance.client import Client
from typing import Dict, List
import json


def calculate_technical_indicators(df, timeframe='5m'):
    """根据不同的时间周期计算相应的技术指标"""
    try:
        # 5分钟周期: 无指标
        if timeframe == '5m':
            # 即使是5分钟，也需要计算ATR，因为止损逻辑需要它
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift())
            df['low_close'] = abs(df['low'] - df['close'].shift())
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            df['atr_14'] = df['true_range'].rolling(14).mean()
            df = df.bfill().ffill()
            return df

        # 通用计算: EMA(20, 50)
        if timeframe in ['15m', '1h', '4h']:
            df['ema_20'] = df['close'].ewm(span=20, min_periods=1).mean()
            df['ema_50'] = df['close'].ewm(span=50, min_periods=1).mean()

        # 15分钟周期: EMA, RSI, MACD
        if timeframe == '15m':
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi_14'] = 100 - (100 / (1 + rs))
            # MACD
            df['ema_12'] = df['close'].ewm(span=12, min_periods=1).mean()
            df['ema_26'] = df['close'].ewm(span=26, min_periods=1).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, min_periods=1).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            # ATR for stop loss
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift())
            df['low_close'] = abs(df['low'] - df['close'].shift())
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            df['atr_14'] = df['true_range'].rolling(14).mean()


        # 1小时周期: EMA, RSI, MACD, ATR, Bollinger Bands
        if timeframe == '1h':
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            # MACD
            df['ema_12'] = df['close'].ewm(span=12, min_periods=1).mean()
            df['ema_26'] = df['close'].ewm(span=26, min_periods=1).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, min_periods=1).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            # ATR
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift())
            df['low_close'] = abs(df['low'] - df['close'].shift())
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            df['atr_14'] = df['true_range'].rolling(14).mean()
            # Bollinger Bands
            df['bb_middle_20'] = df['close'].rolling(20).mean()
            bb_std = df['close'].rolling(20).std()
            df['bb_upper_20'] = df['bb_middle_20'] + (bb_std * 2)
            df['bb_lower_20'] = df['bb_middle_20'] - (bb_std * 2)
            df['bb_position'] = (df['close'] - df['bb_lower_20']) / (df['bb_upper_20'] - df['bb_lower_20'])

        # 4小时周期: EMA, RSI, MACD, ATR
        if timeframe == '4h':
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            # MACD
            df['ema_12'] = df['close'].ewm(span=12, min_periods=1).mean()
            df['ema_26'] = df['close'].ewm(span=26, min_periods=1).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, min_periods=1).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            # ATR
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift())
            df['low_close'] = abs(df['low'] - df['close'].shift())
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            df['atr_14'] = df['true_range'].rolling(14).mean()

        # 填充NaN值
        df = df.bfill().ffill()
        return df
    except Exception as e:
        print(f"技术指标计算失败 ({timeframe}): {e}")
        return df


class MarketScanner:
    """市场扫描器 - 获取所有币种的市场数据"""
    
    def __init__(self, binance_client: Client, config_file='config/coins_config.json'):
        self.binance_client = binance_client
        self.config_file = config_file
        self.coins_config = self.load_config()
        self.coins = [c['symbol'] for c in self.coins_config['coins']]
    
    def load_config(self) -> Dict:
        """加载币种配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return {'coins': [], 'portfolio_rules': {}}
    
    def get_coin_1h_data(self, coin: str) -> Dict:
        """获取单个币种的1小时K线数据"""
        try:
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取1小时K线
            klines_1h = self.binance_client.futures_klines(
                symbol=symbol,
                interval='1h',
                limit=100 # 足够计算EMA(50)和BB(20)
            )
            
            df_1h = pd.DataFrame(klines_1h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df_1h = df_1h[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_1h['timestamp'] = pd.to_datetime(df_1h['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df_1h[col] = df_1h[col].astype(float)
            
            # 计算1小时技术指标
            df_1h = calculate_technical_indicators(df_1h, timeframe='1h')
            
            current_1h = df_1h.iloc[-1]
            
            # 获取最近10根K线（用于AI分析中期趋势和形态）
            recent_klines_1h = []
            for _, row in df_1h.tail(10).iterrows():
                recent_klines_1h.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            return {
                'coin': coin,
                'timeframe': '1h',
                'price': current_1h['close'],
                'ema_20': current_1h.get('ema_20', 0),
                'ema_50': current_1h.get('ema_50', 0),
                'atr_14': current_1h.get('atr_14', 0),
                'bb_upper': current_1h.get('bb_upper_20', 0),
                'bb_lower': current_1h.get('bb_lower_20', 0),
                'bb_position': current_1h.get('bb_position', 0),
                'klines': recent_klines_1h  # 新增：最近10根K线
            }
            
        except Exception as e:
            print(f"❌ 获取{coin}的1小时K线失败: {e}")
            return None
    
    def get_coin_4h_data(self, coin: str) -> Dict:
        """获取单个币种的4小时K线数据"""
        try:
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取4小时K线
            klines_4h = self.binance_client.futures_klines(
                symbol=symbol,
                interval='4h',
                limit=100 # 足够计算EMA(50)
            )
            
            df_4h = pd.DataFrame(klines_4h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df_4h = df_4h[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_4h['timestamp'] = pd.to_datetime(df_4h['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df_4h[col] = df_4h[col].astype(float)
            
            # 计算4小时技术指标
            df_4h = calculate_technical_indicators(df_4h, timeframe='4h')
            
            current_4h = df_4h.iloc[-1]
            
            # 获取最近6根K线（用于AI分析长期趋势和方向）
            recent_klines_4h = []
            for _, row in df_4h.tail(6).iterrows():
                recent_klines_4h.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            return {
                'coin': coin,
                'timeframe': '4h',
                'price': current_4h['close'],
                'ema_20': current_4h.get('ema_20', 0),
                'ema_50': current_4h.get('ema_50', 0),
                'atr_14': current_4h.get('atr_14', 0),
                'klines': recent_klines_4h  # 新增：最近6根K线
            }
            
        except Exception as e:
            print(f"❌ 获取{coin}的4小时K线失败: {e}")
            return None
    
    def get_coin_15m_data(self, coin: str) -> Dict:
        """获取单个币种的15分钟K线数据"""
        try:
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取15分钟K线
            klines_15m = self.binance_client.futures_klines(
                symbol=symbol,
                interval='15m',
                limit=100 # 足够计算EMA(50)和MACD
            )
            
            df_15m = pd.DataFrame(klines_15m, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df_15m = df_15m[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_15m['timestamp'] = pd.to_datetime(df_15m['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df_15m[col] = df_15m[col].astype(float)
            
            # 计算15分钟技术指标
            df_15m = calculate_technical_indicators(df_15m, timeframe='15m')
            
            current_15m = df_15m.iloc[-1]
            
            # 获取最近16根K线（用于AI分析战术层趋势，覆盖4小时）
            recent_klines_15m = []
            for _, row in df_15m.tail(16).iterrows():
                recent_klines_15m.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            return {
                'coin': coin,
                'timeframe': '15m',
                'price': current_15m['close'],
                'ema_20': current_15m.get('ema_20', 0),
                'ema_50': current_15m.get('ema_50', 0),
                'rsi_14': current_15m.get('rsi_14', 0),
                'macd': current_15m.get('macd', 0),
                'macd_signal': current_15m.get('macd_signal', 0),
                'atr_14': current_15m.get('atr_14', 0), # ATR for stop loss
                'klines': recent_klines_15m  # 新增：最近16根K线
            }
            
        except Exception as e:
            print(f"❌ 获取{coin}的15分钟K线失败: {e}")
            return None

    def scan_coin(self, coin: str, timeframe='5m', limit=300) -> Dict:
        """扫描单个币种的市场数据（5分钟周期）"""
        try:
            # 找到币种配置
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取K线数据
            klines = self.binance_client.futures_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            # 转换为DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # 计算5分钟技术指标（仅ATR）
            df = calculate_technical_indicators(df, timeframe='5m')
            
            # 获取当前K线和历史K线
            current_kline = df.iloc[-1]
            previous_klines = df.iloc[-26:-1] # 最近25根完整K线
            
            # 获取15分钟数据
            data_15m = self.get_coin_15m_data(coin)

            # 获取1小时数据
            data_1h = self.get_coin_1h_data(coin)

            # 获取4小时数据
            data_4h = self.get_coin_4h_data(coin)

            # 计算当前价格
            current_price = current_kline['close']

            # 获取资金费率和持仓量
            try:
                premium_index = self.binance_client.futures_funding_rate(symbol=symbol, limit=1)
                funding_rate = float(premium_index[0]['fundingRate']) if premium_index else 0
            except:
                funding_rate = 0

            try:
                open_interest_data = self.binance_client.futures_open_interest(symbol=symbol)
                open_interest = float(open_interest_data['openInterest']) if open_interest_data else 0
            except:
                open_interest = 0

            # 计算24小时变化率（使用最近24小时数据）
            change_24h = 0.0
            if len(df) >= 288:  # 5分钟 * 288 = 24小时
                previous_price_24h = df.iloc[-289]['close']  # 24小时前的价格
                change_24h = ((current_price - previous_price_24h) / previous_price_24h) * 100
            
            # 计算RSI（使用15分钟数据）
            rsi = data_15m.get('rsi_14', 0) if data_15m else 0
            
            # 计算趋势方向和强度（基于EMA交叉）
            trend_direction = "neutral"
            trend_strength = 0
            
            if data_1h:
                ema_20 = data_1h.get('ema_20', 0)
                ema_50 = data_1h.get('ema_50', 0)
                if ema_20 > ema_50:
                    trend_direction = "up"
                    trend_strength = ((ema_20 - ema_50) / ema_50) * 100
                elif ema_20 < ema_50:
                    trend_direction = "down"
                    trend_strength = ((ema_50 - ema_20) / ema_50) * 100
                else:
                    trend_direction = "neutral"
                    trend_strength = 0

            # 构建扁平化的数据结构（供portfolio_manager使用）
            result = {
                'coin': coin,
                'price': current_price,
                'change_24h': change_24h,
                'rsi': rsi,
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'funding_rate': funding_rate,
                'open_interest': open_interest,
                'kline_5m': previous_klines.to_dict('records'),  # 5分钟K线历史
                'atr_14_5m': current_kline.get('atr_14', 0),  # 5分钟ATR
                'min_order_value': coin_info.get('min_order_value', 13),  # 最小开仓金额
            }

            # 添加15分钟数据
            if data_15m:
                result['ema_20_15m'] = data_15m.get('ema_20', 0)
                result['ema_50_15m'] = data_15m.get('ema_50', 0)
                result['rsi_14_15m'] = data_15m.get('rsi_14', 0)
                result['macd_15m'] = data_15m.get('macd', 0)
                result['macd_signal_15m'] = data_15m.get('macd_signal', 0)
                result['atr_14_15m'] = data_15m.get('atr_14', 0)
                result['kline_15m'] = data_15m.get('klines', [])  # 新增：15分钟K线数据

            # 添加1小时数据
            if data_1h:
                result['ema_20_1h'] = data_1h.get('ema_20', 0)
                result['ema_50_1h'] = data_1h.get('ema_50', 0)
                result['atr_14_1h'] = data_1h.get('atr_14', 0)
                result['bbands_1h'] = {
                    'upper': data_1h.get('bb_upper', 0),
                    'middle': data_1h.get('bb_middle_20', 0),
                    'lower': data_1h.get('bb_lower', 0),
                    'position': data_1h.get('bb_position', 0)
                }
                result['kline_1h'] = data_1h.get('klines', [])  # 新增：1小时K线数据

            # 添加4小时数据
            if data_4h:
                result['ema_20_4h'] = data_4h.get('ema_20', 0)
                result['ema_50_4h'] = data_4h.get('ema_50', 0)
                result['atr_14_4h'] = data_4h.get('atr_14', 0)
                result['kline_4h'] = data_4h.get('klines', [])  # 新增：4小时K线数据

            return result

        except Exception as e:
            print(f"❌ 扫描{coin}失败: {e}")
            return None
    
    def scan_all_markets(self, timeframe='5m') -> Dict[str, Dict]:
        """扫描所有币种的市场数据"""
        print("\n" + "="*60)
        print("🔍 扫描市场数据...")
        print("="*60)
        
        market_data = {}
        
        for coin in self.coins:
            data = self.scan_coin(coin, timeframe)
            if data and all(k in data for k in ['price', 'change_24h', 'rsi', 'trend_direction', 'trend_strength']):
                market_data[coin] = data
                trend_emoji = {"up": "📈", "down": "📉", "neutral": "➡️"}.get(data.get('trend_direction'), "❓")
                # 低价币种显示更多小数位
                price_fmt = f"${data['price']:.4f}" if coin in ['DOGE', 'XRP'] else f"${data['price']:.2f}"
                print(f"✅ {coin}: {price_fmt} | 24h: {data['change_24h']:+.2f}% | RSI: {data['rsi']:.1f} | SMA20/50: {trend_emoji}{data['trend_direction']} ({data['trend_strength']:.2f}%)")
            else:
                print(f"❌ {coin}: 数据获取失败")
        
        print("="*60 + "\n")
        return market_data
    
    def get_btc_context(self) -> Dict:
        """获取BTC市场背景（增强版：包含15分钟和1小时技术指标）"""
        try:
            import pandas as pd
            
            # 获取BTC当前价格
            btc_ticker = self.binance_client.futures_ticker(symbol='BTCUSDT')
            btc_price = float(btc_ticker['lastPrice'])
            
            # 获取15分钟K线（用于计算技术指标）
            btc_klines_15m = self.binance_client.futures_klines(
                symbol='BTCUSDT',
                interval='15m',
                limit=96  # 24小时数据，足够计算技术指标
            )
            
            # 转换为DataFrame并计算15分钟技术指标
            df_15m = pd.DataFrame(btc_klines_15m, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df_15m['open'] = df_15m['open'].astype(float)
            df_15m['high'] = df_15m['high'].astype(float)
            df_15m['low'] = df_15m['low'].astype(float)
            df_15m['close'] = df_15m['close'].astype(float)
            df_15m['volume'] = df_15m['volume'].astype(float)
            df_15m = calculate_technical_indicators(df_15m, timeframe='15m')
            current_15m = df_15m.iloc[-1]
            previous_15m = df_15m.iloc[-2]
            
            btc_change_15m = ((current_15m['close'] - previous_15m['close']) / previous_15m['close']) * 100
            
            # 获取1小时K线（用于中期趋势）
            btc_klines_1h = self.binance_client.futures_klines(
                symbol='BTCUSDT',
                interval='1h',
                limit=60  # 2.5天数据
            )
            
            # 转换为DataFrame并计算1小时技术指标
            df_1h = pd.DataFrame(btc_klines_1h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df_1h['open'] = df_1h['open'].astype(float)
            df_1h['high'] = df_1h['high'].astype(float)
            df_1h['low'] = df_1h['low'].astype(float)
            df_1h['close'] = df_1h['close'].astype(float)
            df_1h['volume'] = df_1h['volume'].astype(float)
            df_1h = calculate_technical_indicators(df_1h, timeframe='1h')
            current_1h = df_1h.iloc[-1]
            
            # 获取4小时K线（用于长期趋势，轻量级）
            btc_klines_4h = self.binance_client.futures_klines(
                symbol='BTCUSDT',
                interval='4h',
                limit=60  # 10天数据
            )
            
            # 转换为DataFrame并计算4小时技术指标
            df_4h = pd.DataFrame(btc_klines_4h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df_4h['open'] = df_4h['open'].astype(float)
            df_4h['high'] = df_4h['high'].astype(float)
            df_4h['low'] = df_4h['low'].astype(float)
            df_4h['close'] = df_4h['close'].astype(float)
            df_4h['volume'] = df_4h['volume'].astype(float)
            df_4h = calculate_technical_indicators(df_4h, timeframe='4h')
            current_4h = df_4h.iloc[-1]
            
            # 获取BTC的资金费率和持仓量
            try:
                btc_funding = self.binance_client.futures_funding_rate(symbol='BTCUSDT', limit=1)
                btc_funding_rate = float(btc_funding[0]['fundingRate'])
            except:
                btc_funding_rate = 0.0
            
            try:
                btc_oi = self.binance_client.futures_open_interest(symbol='BTCUSDT')
                btc_open_interest = float(btc_oi['openInterest'])
            except:
                btc_open_interest = 0.0
            
            # 获取时间序列数据（最近10个值）
            rsi_series_15m = df_15m.get('rsi_14', pd.Series([0]*10)).tail(10).tolist()
            macd_series_15m = df_15m.get('macd', pd.Series([0]*10)).tail(10).tolist()
            atr_series_15m = df_15m.get('atr_14', pd.Series([0]*10)).tail(10).tolist()

            rsi_series_1h = df_1h.get('rsi', pd.Series([0]*10)).tail(10).tolist()
            macd_series_1h = df_1h.get('macd', pd.Series([0]*10)).tail(10).tolist()
            atr_series_1h = df_1h.get('atr_14', pd.Series([0]*10)).tail(10).tolist()

            return {
                'price': btc_price,
                'change_15m': btc_change_15m,
                # 15分钟数据
                'rsi_15m': current_15m.get('rsi_14', 0),
                'macd_15m': current_15m.get('macd', 0),
                'atr_15m': current_15m.get('atr_14', 0),
                # 1小时数据
                'rsi_1h': current_1h.get('rsi', 0),
                'macd_1h': current_1h.get('macd', 0),
                'atr_1h': current_1h.get('atr_14', 0),
                'sma_20_1h': current_1h.get('sma_20', 0),
                'sma_50_1h': current_1h.get('sma_50', 0),
                # 4小时数据（轻量级）
                'rsi_4h': current_4h.get('rsi', 0),
                'macd_4h': current_4h.get('macd', 0),
                'sma_20_4h': current_4h.get('sma_20', 0),
                'sma_50_4h': current_4h.get('sma_50', 0),
                # 市场情绪
                'funding_rate': btc_funding_rate,
                'open_interest': btc_open_interest,
                # 时间序列数据（最近10个值，从旧到新）
                'rsi_series_15m': rsi_series_15m,
                'macd_series_15m': macd_series_15m,
                'atr_series_15m': atr_series_15m,
                'rsi_series_1h': rsi_series_1h,
                'macd_series_1h': macd_series_1h,
                'atr_series_1h': atr_series_1h
            }
        except Exception as e:
            print(f"获取BTC数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_portfolio_positions(self) -> Dict[str, Dict]:
        """获取当前所有币种的持仓情况"""
        try:
            all_positions = self.binance_client.futures_position_information()
            
            portfolio = {coin: None for coin in self.coins}
            
            # 读取本地记录的止损止盈
            local_positions = {}
            try:
                import json
                import os
                stats_file = os.path.join(os.path.dirname(__file__), 'portfolio_stats.json')
                if os.path.exists(stats_file):
                    with open(stats_file, 'r', encoding='utf-8') as f:
                        stats = json.load(f)
                        local_positions = stats.get('current_positions', {})
            except:
                pass
            
            for pos in all_positions:
                position_amt = float(pos.get('positionAmt', 0))
                if position_amt != 0:
                    symbol = pos.get('symbol', '')
                    coin = symbol.replace('USDT', '')
                    
                    if coin in portfolio:
                        entry_price = float(pos.get('entryPrice', 0))
                        unrealized_pnl = float(pos.get('unRealizedProfit', 0))
                        initial_margin = float(pos.get('initialMargin', 0))
                        
                        # 计算ROE（保证金回报率）
                        roe = 0.0
                        if initial_margin > 0:
                            roe = (unrealized_pnl / initial_margin) * 100
                        
                        portfolio[coin] = {
                            'side': 'long' if position_amt > 0 else 'short',
                            'amount': abs(position_amt),
                            'entry_price': entry_price,
                            'pnl': unrealized_pnl,
                            'roe': roe,  # 新增：保证金回报率
                            'value': abs(position_amt) * entry_price,
                            'stop_loss': local_positions.get(coin, {}).get('stop_loss', 0),
                            'take_profit': local_positions.get(coin, {}).get('take_profit', 0)
                        }
            
            return portfolio
            
        except Exception as e:
            print(f"获取持仓失败: {e}")
            return {coin: None for coin in self.coins}
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        try:
            account_info = self.binance_client.futures_account()
            
            total_balance = float(account_info['totalWalletBalance'])
            free_balance = float(account_info['availableBalance'])
            used_margin = float(account_info['totalPositionInitialMargin'])
            
            margin_ratio = (used_margin / total_balance * 100) if total_balance > 0 else 0
            
            return {
                'total_balance': total_balance,
                'free_balance': free_balance,
                'used_margin': used_margin,
                'margin_ratio': margin_ratio
            }
        except Exception as e:
            print(f"获取账户信息失败: {e}")
            return {
                'total_balance': 0,
                'free_balance': 0,
                'used_margin': 0,
                'margin_ratio': 0
            }

