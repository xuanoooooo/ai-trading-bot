import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class DryRunFuturesAdapter:
    """仿真期货执行器：保留行情请求，拦截下单并在本地模拟成交"""

    def __init__(
        self,
        real_client,
        leverage: int = 3,
        initial_balance: float = 2000.0,
        fee_rate: float = 0.0004,
        slippage: float = 0.0005,
    ):
        self._client = real_client
        self.leverage = leverage
        self.initial_balance = float(initial_balance)
        self.available_balance = float(initial_balance)
        self.fee_rate = float(fee_rate)
        self.slippage = float(slippage)
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.open_orders: Dict[int, Dict[str, Any]] = {}
        self.order_seq = int(time.time() * 1000)
        self.known_symbols: List[str] = []
        self.symbol_by_coin: Dict[str, str] = {}
        self.last_prices: Dict[str, float] = {}
        self.realized_pnl = 0.0
        self._stats = None
        self.leverage_by_symbol: Dict[str, int] = {}

    def __getattr__(self, item):
        """其余属性透明转发给真实客户端"""
        return getattr(self._client, item)

    def attach_statistics(self, stats):
        """绑定统计模块，方便在仿真成交后更新记录"""
        self._stats = stats

    def register_symbols(self, symbol_map: Dict[str, str]):
        self.symbol_by_coin.update(symbol_map)
        for symbol in symbol_map.values():
            if symbol not in self.known_symbols:
                self.known_symbols.append(symbol)

    def _next_order_id(self) -> int:
        self.order_seq += 1
        return self.order_seq

    # --- 行情辅助 ---
    def _get_price(self, symbol: str) -> float:
        if symbol in self.last_prices:
            return self.last_prices[symbol]
        # 优先使用标记价格，失败时退化为最新成交价
        try:
            mark_price = self._client.futures_mark_price(symbol=symbol)
            price = float(mark_price['markPrice'])
        except Exception:
            ticker = self._client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
        self.last_prices[symbol] = price
        return price

    def _current_timestamp(self) -> int:
        return int(time.time() * 1000)

    # --- 账户与仓位 ---
    def _compute_unrealized_pnl(self) -> float:
        total = 0.0
        for symbol, pos in self.positions.items():
            price = self._get_price(symbol)
            entry_price = pos['entryPrice']
            qty = abs(pos['positionAmt'])
            if qty == 0:
                continue
            if pos['side'] == 'long':
                total += (price - entry_price) * qty
            else:
                total += (entry_price - price) * qty
        return total

    def _total_margin(self) -> float:
        return sum(pos['margin'] for pos in self.positions.values())

    def futures_account(self) -> Dict[str, Any]:
        unrealized = self._compute_unrealized_pnl()
        total_margin = self._total_margin()
        wallet_balance = self.available_balance + total_margin + unrealized
        return {
            'totalWalletBalance': f"{wallet_balance:.8f}",
            'availableBalance': f"{self.available_balance:.8f}",
            'totalUnrealizedProfit': f"{unrealized:.8f}",
            'totalPositionInitialMargin': f"{total_margin:.8f}",
            'assets': [
                {
                    'asset': 'USDT',
                    'walletBalance': f"{wallet_balance:.8f}",
                    'availableBalance': f"{self.available_balance:.8f}",
                }
            ],
        }

    def futures_position_information(self) -> List[Dict[str, Any]]:
        positions = []
        # 返回已知币种，保证与真实接口结构一致
        symbols = self.known_symbols or list(self.positions.keys())
        for symbol in symbols:
            pos = self.positions.get(symbol)
            if not pos:
                positions.append(
                    {
                        'symbol': symbol,
                        'positionAmt': '0',
                        'entryPrice': '0',
                        'unRealizedProfit': '0',
                        'initialMargin': '0',
                    }
                )
                continue
            price = self._get_price(symbol)
            qty = pos['positionAmt']
            unrealized = (price - pos['entryPrice']) * qty if pos['side'] == 'long' else (pos['entryPrice'] - price) * abs(qty)
            positions.append(
                {
                    'symbol': symbol,
                    'positionAmt': f"{qty:.8f}",
                    'entryPrice': f"{pos['entryPrice']:.8f}",
                    'unRealizedProfit': f"{unrealized:.8f}",
                    'initialMargin': f"{pos['margin']:.8f}",
                }
            )
        return positions

    # --- 下单流程 ---
    def futures_change_leverage(self, symbol: str, leverage: int):
        self.leverage_by_symbol[symbol] = leverage
        # 返回与真实接口兼容的结构
        return {'symbol': symbol, 'leverage': leverage}

    def futures_create_order(self, **kwargs) -> Dict[str, Any]:
        symbol = kwargs['symbol']
        side = kwargs['side']
        order_type = kwargs.get('type', 'MARKET')
        quantity = float(kwargs.get('quantity', 0))
        stop_price = float(kwargs.get('stopPrice', 0))
        reduce_only = kwargs.get('reduceOnly', False)

        if order_type == 'STOP_MARKET':
            return self._create_stop_order(symbol, side, quantity, stop_price, reduce_only)

        return self._execute_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            reduce_only=reduce_only,
            manual_trigger=True,
        )[0]

    def _create_stop_order(self, symbol: str, side: str, quantity: float, stop_price: float, reduce_only: bool) -> Dict[str, Any]:
        order_id = self._next_order_id()
        now = self._current_timestamp()
        order = {
            'symbol': symbol,
            'orderId': order_id,
            'status': 'NEW',
            'type': 'STOP_MARKET',
            'side': side,
            'stopPrice': stop_price,
            'origQty': f"{quantity:.8f}",
            'executedQty': "0",
            'updateTime': now,
            'reduceOnly': reduce_only,
        }
        self.open_orders[order_id] = order
        return order

    def _execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False,
        manual_trigger: bool = False,
        trigger_price: Optional[float] = None,
        reason: str = 'manual',
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        now = self._current_timestamp()
        market_price = trigger_price if trigger_price is not None else self._get_price(symbol)
        if market_price <= 0:
            market_price = self._get_price(symbol)

        price_adjust = self.slippage if side == 'BUY' else -self.slippage
        if reduce_only:
            price_adjust = -self.slippage if side == 'SELL' else self.slippage
        executed_price = market_price * (1 + price_adjust)

        fee = executed_price * quantity * self.fee_rate
        order_id = self._next_order_id()
        order = {
            'symbol': symbol,
            'orderId': order_id,
            'status': 'FILLED',
            'type': 'MARKET',
            'side': side,
            'price': f"{executed_price:.8f}",
            'avgPrice': f"{executed_price:.8f}",
            'origQty': f"{quantity:.8f}",
            'executedQty': f"{quantity:.8f}",
            'cumQuote': f"{executed_price * quantity:.8f}",
            'updateTime': now,
            'reduceOnly': reduce_only,
        }

        if reduce_only:
            report = self._close_position(symbol, side, quantity, executed_price, fee, reason)
        else:
            report = self._open_position(symbol, side, quantity, executed_price, fee)

        if manual_trigger and report and report.get('message'):
            print(report['message'])

        return order, report

    def _open_position(self, symbol: str, side: str, quantity: float, price: float, fee: float) -> Dict[str, Any]:
        direction = 'long' if side == 'BUY' else 'short'
        leverage = self.leverage_by_symbol.get(symbol, self.leverage)
        notional = price * quantity
        margin = notional / leverage

        if self.available_balance < margin + fee:
            print(f"⚠️ Dry-Run余额不足，尝试开仓 {symbol} 被拒绝（需要 {margin + fee:.2f} USDT）")
            return {'message': f"Dry-Run余额不足，无法开{direction}仓 {symbol}"}

        self.available_balance -= (margin + fee)
        position_amt = quantity if direction == 'long' else -quantity
        self.positions[symbol] = {
            'symbol': symbol,
            'side': direction,
            'positionAmt': position_amt,
            'entryPrice': price,
            'quantity': quantity,
            'margin': margin,
            'open_time': self._current_timestamp(),
        }
        self.realized_pnl -= fee
        message = f"🧪 Dry-Run 开{direction}仓 {symbol}: {quantity:.4f} @ {price:.4f} (杠杆{leverage}x)"
        return {'message': message}

    def _close_position(self, symbol: str, side: str, quantity: float, price: float, fee: float, reason: str) -> Optional[Dict[str, Any]]:
        position = self.positions.get(symbol)
        if not position or abs(position['positionAmt']) < 1e-8:
            return {'message': f"⚠️ Dry-Run 未找到 {symbol} 持仓，跳过平仓"}

        current_qty = abs(position['positionAmt'])
        close_qty = min(quantity, current_qty)

        if position['side'] == 'long' and side != 'SELL':
            return {'message': f"⚠️ Dry-Run 平仓方向不匹配 {symbol}"}
        if position['side'] == 'short' and side != 'BUY':
            return {'message': f"⚠️ Dry-Run 平仓方向不匹配 {symbol}"}

        entry_price = position['entryPrice']
        if position['side'] == 'long':
            pnl = (price - entry_price) * close_qty
        else:
            pnl = (entry_price - price) * close_qty

        pnl_after_fee = pnl - fee
        self.realized_pnl += pnl_after_fee

        ratio = close_qty / current_qty if current_qty > 0 else 1
        margin_release = position['margin'] * ratio
        position['margin'] -= margin_release
        position['quantity'] -= close_qty
        if position['side'] == 'long':
            position['positionAmt'] -= close_qty
        else:
            position['positionAmt'] += close_qty

        self.available_balance += margin_release + pnl_after_fee

        closed = False
        if abs(position['positionAmt']) < 1e-6:
            self.positions.pop(symbol, None)
            closed = True

        coin = self._coin_from_symbol(symbol)
        msg_reason = "止损触发" if reason == 'stop' else "手动平仓"
        message = f"🧪 Dry-Run {msg_reason} {symbol}: {close_qty:.4f} @ {price:.4f} | PnL {pnl_after_fee:+.2f} USDT"
        report = {
            'symbol': symbol,
            'coin': coin,
            'side': position['side'],
            'entry_price': entry_price,
            'exit_price': price,
            'amount': close_qty,
            'pnl': pnl_after_fee,
            'fee': fee,
            'closed': closed,
            'reason': reason,
            'message': message,
        }

        if closed:
            self._cancel_symbol_orders(symbol)

        if self._stats and coin and closed and reason == 'stop':
            self._stats.record_stop_loss_triggered(
                coin=coin,
                side=position['side'],
                entry_price=entry_price,
                stop_price=price,
                amount=close_qty,
                trigger_time=datetime.now(),
                pnl=pnl_after_fee,
                entry_time=datetime.fromtimestamp(position['open_time'] / 1000.0),
            )
            self._stats.record_trade_exit(coin, price, 'stop_loss_triggered')

        return report

    def _cancel_symbol_orders(self, symbol: str):
        for order in self.open_orders.values():
            if order['symbol'] == symbol and order['status'] == 'NEW':
                order['status'] = 'CANCELED'
                order['updateTime'] = self._current_timestamp()

    # --- 仿真订单管理 ---
    def futures_cancel_all_open_orders(self, symbol: str):
        self._cancel_symbol_orders(symbol)
        return []

    def futures_cancel_order(self, symbol: str, orderId: int):
        order = self.open_orders.get(orderId)
        if order and order['symbol'] == symbol and order['status'] == 'NEW':
            order['status'] = 'CANCELED'
            order['updateTime'] = self._current_timestamp()
        return order

    def futures_get_open_orders(self) -> List[Dict[str, Any]]:
        return [order for order in self.open_orders.values() if order['status'] == 'NEW']

    def futures_get_order(self, symbol: str, orderId: int) -> Dict[str, Any]:
        order = self.open_orders.get(orderId)
        if not order:
            raise ValueError(f"Unknown order {orderId}")
        return order

    # --- 行情同步：触发止损/止盈 ---
    def sync_with_market_data(self, market_data: Dict[str, Dict[str, Any]], portfolio_stats=None):
        if portfolio_stats:
            self.attach_statistics(portfolio_stats)

        for coin, data in market_data.items():
            symbol = self.symbol_by_coin.get(coin)
            if not symbol:
                continue
            price = data.get('price')
            if price is None:
                continue
            self.last_prices[symbol] = price

        for order_id, order in list(self.open_orders.items()):
            if order['status'] != 'NEW':
                continue
            symbol = order['symbol']
            price = self.last_prices.get(symbol)
            if price is None:
                continue

            trigger = False
            if order['side'] == 'SELL' and price <= order['stopPrice']:
                trigger = True
            elif order['side'] == 'BUY' and price >= order['stopPrice']:
                trigger = True

            if trigger:
                order['status'] = 'FILLED'
                order['executedQty'] = order['origQty']
                order['avgPrice'] = f"{price:.8f}"
                order['updateTime'] = self._current_timestamp()
                qty = float(order['origQty'])
                _, report = self._execute_market_order(
                    symbol=symbol,
                    side=order['side'],
                    quantity=qty,
                    reduce_only=True,
                    manual_trigger=False,
                    trigger_price=price,
                    reason='stop',
                )
                if report and report.get('message'):
                    print(report['message'])

    def _coin_from_symbol(self, symbol: str) -> Optional[str]:
        for coin, sym in self.symbol_by_coin.items():
            if sym == symbol:
                return coin
        if symbol.endswith("USDT"):
            return symbol.replace("USDT", "")
        return None
