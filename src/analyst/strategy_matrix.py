import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from analyst.events import CandleEvent, OrderUpdateEvent
from analyst.state import StrategyState


@dataclass
class OrderMeta:
    side: str  # "BUY"|"SELL"
    qty: float
    price: float


class MatrixStrategy:
    def __init__(
        self,
        publisher,
        k_sigma: float = 2.0,
        trail_pct: float = 0.02,
        min_n: int = 20,
        default_qty: float = 0.001,
    ):
        self.pub = publisher
        self.k = k_sigma
        self.tpct = trail_pct
        self.min_n = min_n
        self.qty = default_qty
        self.state = StrategyState()
        self.orders: Dict[str, OrderMeta] = {}  # id -> meta

    async def handle(self, ev):
        if isinstance(ev, CandleEvent):
            await self._on_candle(ev)
        elif isinstance(ev, OrderUpdateEvent):
            await self._on_order_update(ev)

    async def _on_candle(self, e: CandleEvent):
        ps = self.state.ps(e.pair)
        ps.last = e.price
        ps.stats.update(e.price)

        # Entry
        if (
            ps.stats.n >= self.min_n
            and ps.open_order_id is None
            and ps.position_qty == 0
        ):
            if ps.stats.std > 0 and e.price < (
                ps.stats.mean - self.k * ps.stats.std
            ):
                await self._place_limit_buy(e.pair, self.qty, e.price)

        # Trailing stop manage
        if ps.position_qty > 0:
            new_stop = max(
                ps.trailing_stop or 0.0, e.price * (1.0 - self.tpct)
            )
            if ps.trailing_stop is None or new_stop > ps.trailing_stop:
                ps.trailing_stop = new_stop
            if e.price < ps.trailing_stop:
                await self._place_limit_sell(e.pair, ps.position_qty, e.price)

    async def _on_order_update(self, e: OrderUpdateEvent):
        ps = self.state.ps(e.pair)
        # we match by open_order_id if present
        if ps.open_order_id and e.order_id != ps.open_order_id:
            return

        meta = self.orders.get(e.order_id)
        if e.status == "CANCELED":
            ps.open_order_id = None
            return

        if e.status in {"FILLED", "PARTIALLY_FILLED"} and meta:
            if meta.side == "BUY":
                ps.position_qty += e.executed_qty or meta.qty  # fallback
                ps.open_order_id = None
                if ps.trailing_stop is None and ps.last:
                    ps.trailing_stop = ps.last * (1.0 - self.tpct)
            elif meta.side == "SELL":
                ps.position_qty -= e.executed_qty or meta.qty
                ps.open_order_id = None
                if ps.position_qty <= 0:
                    ps.position_qty = 0.0
                    ps.trailing_stop = None

    async def _place_limit_buy(self, pair: str, qty: float, price: float):
        oid = self._uuid()
        order = {
            "id_pasticoni": oid,
            "id_strategy": 42,
            "symbol": pair,
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": f"{qty:.8f}",
            "price": f"{price:.8f}",
            "status": "NEW",
        }
        await self.pub.publish_order(order)
        self.state.ps(pair).open_order_id = oid
        self.orders[oid] = OrderMeta(side="BUY", qty=qty, price=price)

    async def _place_limit_sell(self, pair: str, qty: float, price: float):
        oid = self._uuid()
        order = {
            "id_pasticoni": oid,
            "id_strategy": 42,
            "symbol": pair,
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": f"{qty:.8f}",
            "price": f"{price:.8f}",
            "status": "NEW",
        }
        await self.pub.publish_order(order)
        self.state.ps(pair).open_order_id = oid
        self.orders[oid] = OrderMeta(side="SELL", qty=qty, price=price)

    @staticmethod
    def _uuid() -> str:
        return uuid.uuid4().hex[:22]  # short id like your logs
