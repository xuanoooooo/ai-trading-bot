"""
市场扫描器 - 获取所有币种的市场数据和技术指标
复用 deepseekBNB_stats.py 的技术指标计算逻辑
"""
import pandas as pd
from binance.client import Client
from typing import Dict, List
import json


def calculate_technical_indicators(df):
    """计算技术指标 - 复用自 deepseekBNB_stats.py"""
    try:
        # 移动平均线
        df['sma_5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()

        # 指数移动平均线
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # 相对强弱指数 (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # 布林带
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # 成交量均线
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']

        # ATR (Average True Range) - 波动率指标
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr_14'] = df['true_range'].rolling(14).mean()  # 14周期ATR

        # 填充NaN值
        df = df.bfill().ffill()

        return df
    except Exception as e:
        print(f"技术指标计算失败: {e}")
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
    
    def get_coin_long_term_data(self, coin: str) -> Dict:
        """获取单个币种的30分钟K线数据（不做趋势判断）"""
        try:
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取60根30分钟K线（1.25天数据，足够计算SMA50）
            klines_1h = self.binance_client.futures_klines(
                symbol=symbol,
                interval='30m',
                limit=60
            )
            
            # 转换为DataFrame
            df_1h = pd.DataFrame(klines_1h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df_1h = df_1h[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_1h['timestamp'] = pd.to_datetime(df_1h['timestamp'], unit='ms')
            df_1h['open'] = df_1h['open'].astype(float)
            df_1h['high'] = df_1h['high'].astype(float)
            df_1h['low'] = df_1h['low'].astype(float)
            df_1h['close'] = df_1h['close'].astype(float)
            df_1h['volume'] = df_1h['volume'].astype(float)
            
            # 计算技术指标
            df_1h = calculate_technical_indicators(df_1h)
            
            current_1h = df_1h.iloc[-1]
            
            # 获取最近10个30分钟指标值（时间序列）
            rsi_series_1h = df_1h['rsi'].tail(10).tolist()
            macd_series_1h = df_1h['macd'].tail(10).tolist()
            atr_series_1h = df_1h['atr_14'].tail(10).tolist()
            
            # 只返回原始数据，不做趋势判断
            return {
                'coin': coin,
                'timeframe': '30m',
                'price': current_1h['close'],
                'sma_20': current_1h.get('sma_20', 0),
                'sma_50': current_1h.get('sma_50', 0),
                'macd': current_1h.get('macd', 0),
                'rsi': current_1h.get('rsi', 0),
                'atr': current_1h.get('atr_14', 0),
                # 时间序列数据（最近10个值，从旧到新）
                'rsi_series': rsi_series_1h,
                'macd_series': macd_series_1h,
                'atr_series': atr_series_1h
            }
            
        except Exception as e:
            print(f"❌ 获取{coin}的30分钟K线失败: {e}")
            return None
    
    def get_coin_4h_data(self, coin: str) -> Dict:
        """获取单个币种的2小时K线数据（轻量级，无时间序列）"""
        try:
            coin_info = next((c for c in self.coins_config['coins'] if c['symbol'] == coin), None)
            if not coin_info:
                return None
            
            symbol = coin_info['binance_symbol']
            
            # 获取60根2小时K线（5天数据，足够计算SMA50）
            klines_4h = self.binance_client.futures_klines(
                symbol=symbol,
                interval='2h',
                limit=60
            )
            
            # 转换为DataFrame
            df_4h = pd.DataFrame(klines_4h, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df_4h = df_4h[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_4h['timestamp'] = pd.to_datetime(df_4h['timestamp'], unit='ms')
            df_4h['open'] = df_4h['open'].astype(float)
            df_4h['high'] = df_4h['high'].astype(float)
            df_4h['low'] = df_4h['low'].astype(float)
            df_4h['close'] = df_4h['close'].astype(float)
            df_4h['volume'] = df_4h['volume'].astype(float)
            
            # 计算技术指标
            df_4h = calculate_technical_indicators(df_4h)
            
            current_4h = df_4h.iloc[-1]
            
            # 只返回当前值，不返回时间序列（轻量级）
            return {
                'coin': coin,
                'timeframe': '2h',
                'price': current_4h['close'],
                'sma_20': current_4h.get('sma_20', 0),
                'sma_50': current_4h.get('sma_50', 0),
                'macd': current_4h.get('macd', 0),
                'rsi': current_4h.get('rsi', 0)
            }
            
        except Exception as e:
            print(f"❌ 获取{coin}的2小时K线失败: {e}")
            return None
    
    def scan_coin(self, coin: str, timeframe='5m', limit=96) -> Dict:
        """扫描单个币种的市场数据"""
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
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # 计算技术指标
            df = calculate_technical_indicators(df)
            
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # 计算涨跌幅
            change_15m = ((current['close'] - previous['close']) / previous['close']) * 100
            
            # 获取24小时涨跌
            ticker = self.binance_client.futures_ticker(symbol=symbol)
            change_24h = float(ticker['priceChangePercent'])
            
            # 判断趋势（客观数据，不做主观判断）
            sma_20 = current['sma_20']
            sma_50 = current['sma_50']
            close = current['close']
            
            # 计算价格相对位置
            if sma_20 > sma_50:
                trend_direction = 'up'
            elif sma_20 < sma_50:
                trend_direction = 'down'
            else:
                trend_direction = 'neutral'
            
            # 计算趋势强度（SMA20与SMA50的差距）
            trend_strength = abs((sma_20 - sma_50) / sma_50 * 100) if sma_50 > 0 else 0
            
            # 计算价格相对SMA20的位置
            price_vs_sma20 = ((close - sma_20) / sma_20 * 100) if sma_20 > 0 else 0
            
            # 获取最近10个指标值（时间序列）
            rsi_series = df['rsi'].tail(10).tolist()
            macd_series = df['macd'].tail(10).tolist()
            sma_20_series = df['sma_20'].tail(10).tolist()
            atr_series = df['atr_14'].tail(10).tolist()
            
            # 获取资金费率和持仓量
            try:
                funding_rate_data = self.binance_client.futures_funding_rate(symbol=symbol, limit=1)
                funding_rate = float(funding_rate_data[0]['fundingRate'])
            except:
                funding_rate = 0.0
            
            try:
                open_interest_data = self.binance_client.futures_open_interest(symbol=symbol)
                open_interest = float(open_interest_data['openInterest'])
            except:
                open_interest = 0.0
            
            return {
                'coin': coin,
                'symbol': symbol,
                'price': current['close'],
                'change_24h': change_24h,
                'change_15m': change_15m,
                'rsi': current['rsi'],
                'macd': current['macd'],
                'macd_signal': current['macd_signal'],
                'sma_20': current['sma_20'],
                'sma_50': current['sma_50'],
                'bb_position': current['bb_position'],
                'volume_ratio': current['volume_ratio'],
                'atr': current['atr_14'],
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'price_vs_sma20': price_vs_sma20,
                'precision': coin_info['precision'],
                'min_order_value': coin_info['min_order_value'],
                # 时间序列数据（最近10个值，从旧到新）
                'rsi_series': rsi_series,
                'macd_series': macd_series,
                'sma_20_series': sma_20_series,
                'atr_series': atr_series,
                # 市场情绪数据
                'funding_rate': funding_rate,
                'open_interest': open_interest
            }
            
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
            if data:
                market_data[coin] = data
                trend_emoji = {"up": "📈", "down": "📉", "neutral": "➡️"}.get(data['trend_direction'], "❓")
                # 低价币种显示更多小数位
                price_fmt = f"${data['price']:,.4f}" if coin in ['DOGE', 'XRP'] else f"${data['price']:,.2f}"
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
            df_15m = calculate_technical_indicators(df_15m)
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
            df_1h = calculate_technical_indicators(df_1h)
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
            df_4h = calculate_technical_indicators(df_4h)
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
            rsi_series_15m = df_15m['rsi'].tail(10).tolist()
            macd_series_15m = df_15m['macd'].tail(10).tolist()
            atr_series_15m = df_15m['atr_14'].tail(10).tolist()
            
            rsi_series_1h = df_1h['rsi'].tail(10).tolist()
            macd_series_1h = df_1h['macd'].tail(10).tolist()
            atr_series_1h = df_1h['atr_14'].tail(10).tolist()
            
            return {
                'price': btc_price,
                'change_15m': btc_change_15m,
                # 15分钟数据
                'rsi_15m': current_15m.get('rsi', 0),
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

