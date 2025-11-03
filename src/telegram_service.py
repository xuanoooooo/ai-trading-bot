import html
import os
import time
from dataclasses import dataclass
from threading import Event, Thread
from queue import Queue, Empty
from typing import Any, Dict, List, Optional

import requests


@dataclass
class TelegramTradePayload:
    coin: str
    side: str
    amount: float
    price: float
    position_value: float
    leverage: int
    reason: str = ""
    stop_loss: float = 0.0
    take_profit: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    exit_reason: str = ""


class TelegramService:
    """基于Telegram Bot API的轻量级通知与命令服务（HTTP实现）"""

    def __init__(
        self,
        config: Dict[str, Any],
        portfolio_stats,
        market_scanner,
        dry_run_mode: bool = False,
    ):
        self.config = config or {}
        self.enabled = bool(self.config.get("enabled", False))
        self.allow_unauthorized = bool(self.config.get("allow_unauthorized", False))
        self.parse_mode = self.config.get("parse_mode", "HTML").upper()
        self.portfolio_stats = portfolio_stats
        self.market_scanner = market_scanner
        self.dry_run_mode = dry_run_mode

        token_env = self.config.get("bot_token_env", "TELEGRAM_BOT_TOKEN")
        self.bot_token = os.getenv(token_env) or self.config.get("bot_token")

        chat_ids = self.config.get("chat_ids", [])
        if isinstance(chat_ids, str):
            chat_ids = [chat_ids]
        chat_ids_env = self.config.get("chat_ids_env", "TELEGRAM_CHAT_IDS")
        chat_ids_from_env = os.getenv(chat_ids_env)
        if chat_ids_from_env:
            chat_ids.extend([cid.strip() for cid in chat_ids_from_env.split(",") if cid.strip()])

        self.chat_ids = self._normalize_chat_ids(chat_ids)
        self.command_chat_ids = set(self.chat_ids)

        self.session: Optional[requests.Session] = None
        self.outbox: Queue = Queue()
        self.sender_thread: Optional[Thread] = None
        self.poll_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.last_update_id: Optional[int] = None

        if not self.enabled:
            return

        if not self.bot_token:
            print("⚠️ Telegram 未启用：缺少 bot token")
            self.enabled = False
            return

        if not self.chat_ids and not self.allow_unauthorized:
            print("⚠️ Telegram 未启用：未配置 chat_id，且未允许未知聊天")
            self.enabled = False
            return

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    @staticmethod
    def _normalize_chat_ids(ids: List[Any]) -> List[int]:
        normalized = []
        for value in ids:
            try:
                normalized.append(int(str(value).strip()))
            except (TypeError, ValueError):
                continue
        return normalized

    def start(self):
        if not self.enabled:
            return

        self.session = requests.Session()
        self.stop_event.clear()

        self._ensure_webhook_cleared()

        self.sender_thread = Thread(target=self._sender_loop, name="TelegramSender", daemon=True)
        self.sender_thread.start()

        self.poll_thread = Thread(target=self._polling_loop, name="TelegramPolling", daemon=True)
        self.poll_thread.start()

        print("✅ Telegram 机器人已启动（HTTP模式）")

    def stop(self):
        if not self.enabled:
            return
        self.stop_event.set()
        if self.sender_thread and self.sender_thread.is_alive():
            self.sender_thread.join(timeout=2)
        if self.poll_thread and self.poll_thread.is_alive():
            self.poll_thread.join(timeout=2)
        if self.session:
            try:
                self.session.close()
            except Exception:
                pass

    # -------------------------
    # 外部接口
    # -------------------------
    def notify_trade(self, event: str, payload: TelegramTradePayload):
        if not self.enabled:
            return

        if event == "open":
            emoji = "🚀" if payload.side == "long" else "🛬"
            sl_text = f"🛡️ 止损 {payload.stop_loss:.4f}" if payload.stop_loss else "🛡️ 止损 未设置"
            tp_text = f"🎯 止盈 {payload.take_profit:.4f}" if payload.take_profit else "🎯 止盈 未设置"
            text = (
                f"{emoji} <b>开仓 {html.escape(payload.coin)}</b>\n"
                f"🔸 方向：{payload.side.upper()} | 数量 {payload.amount:.4f}\n"
                f"💵 入场价：{payload.price:.4f} | 名义金额：{payload.position_value:.2f} USDT\n"
                f"{sl_text} | {tp_text}\n"
                f"🧠 原因：{html.escape(payload.reason or 'AI 决策')}"
            )
        elif event == "close":
            emoji = "✅" if payload.pnl >= 0 else "⚠️"
            text = (
                f"{emoji} <b>平仓 {html.escape(payload.coin)}</b>\n"
                f"🔸 方向：{payload.side.upper()} | 数量 {payload.amount:.4f}\n"
                f"💵 平仓价：{payload.price:.4f}\n"
                f"💰 盈亏：<b>{payload.pnl:+.2f} USDT</b> ({payload.pnl_percent:+.2f}%)\n"
                f"🏁 原因：{html.escape(payload.exit_reason or '手动/AI 决策')}"
            )
        elif event == "stop":
            text = (
                f"🛡️ <b>止损触发 {html.escape(payload.coin)}</b>\n"
                f"🔸 方向：{payload.side.upper()} | 触发价 {payload.price:.4f}\n"
                f"💰 盈亏：{payload.pnl:+.2f} USDT"
            )
        else:
            text = f"ℹ️ {html.escape(payload.coin)} 事件：{event}"

        self._broadcast(text)

    # -------------------------
    # 内部实现
    # -------------------------
    def _sender_loop(self):
        while not self.stop_event.is_set():
            try:
                chat_id, text, parse_mode = self.outbox.get(timeout=0.5)
            except Empty:
                continue

            try:
                self._send_message(chat_id, text, parse_mode=parse_mode)
            except Exception as exc:
                print(f"⚠️ Telegram 消息发送失败（chat_id={chat_id}）: {exc}")

    def _polling_loop(self):
        poll_url = f"{self.base_url}/getUpdates"
        while not self.stop_event.is_set():
            try:
                params = {
                    "timeout": 20,
                    "offset": self.last_update_id + 1 if self.last_update_id else None,
                }
                response = self.session.get(poll_url, params=params, timeout=25)
                data = response.json()
                if not data.get("ok"):
                    raise ValueError(data)

                for update in data.get("result", []):
                    self.last_update_id = update.get("update_id")
                    self._handle_update(update)
            except Exception as exc:
                print(f"⚠️ Telegram 轮询失败: {exc}")
                time.sleep(3)

    def _handle_update(self, update: Dict[str, Any]):
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "").strip()
        if not chat_id or not text:
            return

        if self.allow_unauthorized:
            self._register_chat(chat_id)
        elif chat_id not in self.command_chat_ids:
            self._send_message(chat_id, "🚫 未授权的聊天，无法使用此机器人。")
            return

        command = text.split()[0].lower()
        if command in ("/start", "/help"):
            self._send_message(chat_id, self._build_help_message())
        elif command in ("/overview", "/status"):
            self._send_message(chat_id, self._build_overview_message())
        elif command in ("/positions", "/pos"):
            self._send_message(chat_id, self._build_positions_message(self._get_positions_snapshot()))
        elif command in ("/pnl", "/profit"):
            self._send_message(chat_id, self._build_pnl_message())
        elif command in ("/recent", "/history"):
            self._send_message(chat_id, self._build_recent_trades_message())
        else:
            self._send_message(chat_id, "🤖 未知命令，使用 /help 查看可用列表。")

    def _register_chat(self, chat_id: int):
        if chat_id not in self.command_chat_ids:
            self.command_chat_ids.add(chat_id)
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)

    def _broadcast(self, text: str, parse_mode: Optional[str] = None):
        if not self.chat_ids and not self.allow_unauthorized:
            return
        targets = self.chat_ids or list(self.command_chat_ids)
        for chat_id in targets:
            self.outbox.put((chat_id, text, parse_mode or self.parse_mode))

    def _send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None):
        if not self.session:
            return
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode or self.parse_mode,
            "disable_notification": False,
        }
        response = self.session.post(url, json=payload, timeout=15)
        data = response.json()
        if not data.get("ok"):
            raise ValueError(data)

    def _ensure_webhook_cleared(self):
        if not self.session:
            return
        url = f"{self.base_url}/deleteWebhook"
        try:
            resp = self.session.post(url, json={"drop_pending_updates": True}, timeout=10)
            data = resp.json()
            if not data.get("ok"):
                print(f"⚠️ 删除Telegram Webhook失败: {data}")
        except Exception as exc:
            print(f"⚠️ 删除Telegram Webhook时异常: {exc}")

    # -------------------------
    # 构建消息
    # -------------------------
    def _build_help_message(self) -> str:
        return (
            "🤖 <b>AI 交易助手</b>\n"
            "可用命令：\n"
            "• /overview —— 帐户概览与收益摘要\n"
            "• /positions —— 当前持仓（表格）\n"
            "• /pnl —— 当前盈亏与24小时表现\n"
            "• /recent —— 最近10笔成交\n"
            "• /help —— 查看命令列表"
        )

    def _build_overview_message(self) -> str:
        stats = self.portfolio_stats
        runtime = stats.get_runtime_info()
        total_trades = stats.total_trades
        win_trades = stats.win_trades
        lose_trades = stats.lose_trades
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0
        total_pnl = stats.total_pnl

        account_info = self._get_account_snapshot()
        balance_text = ""
        if account_info:
            balance_text = (
                f"\n💼 账户余额：<b>{account_info.get('total_balance', 0):.2f} USDT</b>\n"
                f"💧 可用资金：{account_info.get('free_balance', 0):.2f} USDT | "
                f"📦 保证金占用：{account_info.get('used_margin', 0):.2f} USDT"
            )

        mode_prefix = "🧪 Dry-Run" if self.dry_run_mode else "🛠️ Live"

        return (
            f"{mode_prefix} 模式状态\n"
            f"📊 <b>账户概览</b>\n"
            f"📈 总交易：{total_trades} 笔 | ✅ 胜 {win_trades} | ❌ 负 {lose_trades} | 🎯 胜率 {win_rate:.1f}%\n"
            f"💰 累计盈亏：<b>{total_pnl:+.2f} USDT</b>\n"
            f"⏱️ 运行时长：{runtime['total_days']}天 {runtime['hours_in_day']}小时 {runtime['minutes_in_hour']}分钟"
            f"{balance_text}"
        )

    def _build_positions_message(self, positions: Dict[str, Dict[str, Any]]) -> str:
        header = "📂 <b>当前持仓</b>\n"
        if not positions:
            return header + "😴 当前没有任何持仓。"

        rows = []
        for coin, pos in positions.items():
            if not pos:
                continue
            side = pos.get("side", "-")
            emoji = "📈" if side == "long" else "📉"
            amount = pos.get("amount", 0)
            entry_price = pos.get("entry_price", 0)
            pnl = pos.get("pnl", 0)
            roe = pos.get("roe", 0)
            stop_loss = pos.get("stop_loss", 0)
            take_profit = pos.get("take_profit", 0)
            rows.append(
                f"{emoji} <b>{html.escape(coin)}</b> | {side.upper()} | 数量 {amount:.4f}\n"
                f"   📌 入场 ${entry_price:.4f} | 🛡️ {stop_loss or '—'} | 🎯 {take_profit or '—'}\n"
                f"   💹 浮盈 {pnl:+.2f} USDT | 🔁 ROE {roe:+.2f}%"
            )

        if not rows:
            return header + "😴 当前没有任何持仓。"

        return header + "\n".join(rows)

    def _build_pnl_message(self) -> str:
        stats = self.portfolio_stats
        recent = stats.get_recent_trades(5)
        pnl_last_24h = stats.get_win_rate(24)
        text = (
            "💹 <b>盈亏概览</b>\n"
            f"🕒 24小时交易：{pnl_last_24h.get('total', 0)} 笔 | "
            f"✅ {pnl_last_24h.get('wins', 0)} | ❌ {pnl_last_24h.get('losses', 0)} | "
            f"🎯 胜率 {pnl_last_24h.get('win_rate', 0):.1f}%\n"
            f"💰 24小时盈亏：{pnl_last_24h.get('total_pnl', 0):+.2f} USDT\n"
        )

        if recent:
            text += "🧾 <b>最近交易</b>\n"
            for trade in reversed(recent):
                coin = trade.get("coin", "?")
                side = trade.get("side", "-")
                pnl = trade.get("pnl", 0)
                pnl_percent = trade.get("pnl_percent", 0)
                exit_reason = trade.get("exit_reason", "unknown")
                exit_time = trade.get("exit_time", "")[:16].replace("T", " ")
                emoji = "✅" if pnl >= 0 else "❌"
                text += (
                    f"{emoji} {exit_time} | {coin} {side.upper()} | {pnl:+.2f} USDT ({pnl_percent:+.2f}%)\n"
                    f"   🏁 {exit_reason}\n"
                )
        else:
            text += "😴 最近没有交易记录。\n"
        return text

    def _build_recent_trades_message(self) -> str:
        stats = self.portfolio_stats
        recent = stats.get_recent_trades(10)
        if not recent:
            return "📜 最近没有成交记录。"

        lines = ["📜 <b>最近 10 笔成交</b>"]
        for trade in reversed(recent):
            coin = trade.get("coin", "?")
            side = trade.get("side", "-")
            pnl = trade.get("pnl", 0)
            pnl_percent = trade.get("pnl_percent", 0)
            duration = trade.get("duration_minutes", 0)
            exit_reason = trade.get("exit_reason", "unknown")
            exit_time = trade.get("exit_time", "")[:16].replace("T", " ")
            emoji = "✅" if pnl >= 0 else "❌"
            lines.append(
                f"{emoji} {exit_time} | {coin} {side.upper()} | {pnl:+.2f} USDT ({pnl_percent:+.2f}%) | 🕒 {duration} 分钟\n"
                f"   🏁 {exit_reason}"
            )
        return "\n".join(lines)

    # -------------------------
    # 数据获取
    # -------------------------
    def _get_positions_snapshot(self) -> Dict[str, Dict[str, Any]]:
        if not self.market_scanner:
            return {}
        try:
            return self.market_scanner.get_portfolio_positions()
        except Exception as exc:
            print(f"⚠️ 获取持仓快照失败: {exc}")
            return {}

    def _get_account_snapshot(self) -> Dict[str, Any]:
        if not self.market_scanner:
            return {}
        try:
            return self.market_scanner.get_account_info()
        except Exception as exc:
            print(f"⚠️ 获取账户信息失败: {exc}")
            return {}
