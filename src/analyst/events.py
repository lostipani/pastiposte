from dataclasses import dataclass
from typing import Optional, Union
import json, ast


@dataclass
class CandleEvent:
    pair: str
    ts: int
    price: float


@dataclass
class OrderUpdateEvent:
    pair: str
    order_id: str
    status: str
    executed_qty: float
    price: float


Event = Union[CandleEvent, OrderUpdateEvent]


def parse_raw(routing_key: str, body: str) -> Optional[Event]:
    try:
        d = json.loads(body)
    except json.JSONDecodeError:
        try:
            d = ast.literal_eval(body)  # listener sends str(dict)
        except Exception:
            return None

    if routing_key == "kline_1m":
        msg = d.get("message", d)
        pair = msg.get("s") or msg.get("symbol") or msg.get("pair")
        ts = int(msg.get("E") or msg.get("ts") or 0)
        if isinstance(msg.get("k"), dict) and msg["k"].get("c"):
            price = float(msg["k"]["c"])
        else:
            price = float(msg.get("price") or msg.get("p") or 0.0)
        if not pair:
            return None
        return CandleEvent(pair=pair, ts=ts, price=price)

    # order updates (skip heartbeats)
    if d.get("event") == "heartbeat":
        return None
    pair = d.get("symbol") or d.get("pair")
    oid = str(d.get("orderId") or d.get("id_pasticoni") or "")
    status = d.get("status") or d.get("X") or "UNKNOWN"
    executed = float(d.get("executedQty") or d.get("z") or 0.0)
    price = float(d.get("price") or d.get("p") or 0.0)
    if not pair or not oid:
        return None
    return OrderUpdateEvent(
        pair=pair,
        order_id=oid,
        status=status,
        executed_qty=executed,
        price=price,
    )
