import json, ast
from datetime import datetime

from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker

from commons.configuration import get_sleep
from commons.rabbitmq import broker
from orders import orders


class Analyst(rabbitMQConsumer):

    def _parse_payload(self, text: str):
        # listener sends str({'source':..., 'message': <json_or_dict>})
        try:
            outer = json.loads(text)
        except json.JSONDecodeError:
            outer = ast.literal_eval(text)
        msg = outer.get("message", outer)
        if isinstance(msg, str):
            try:
                msg = json.loads(msg)
            except json.JSONDecodeError:
                msg = ast.literal_eval(msg)
        kline = msg.get("k", msg)  # binance kline payload nests under "k"
        return kline, msg

    def _symbol_from(self, kline, fallback="BTCUSDT"):
        return kline.get("s") or fallback

    def _close_from(self, kline):
        c = kline.get("c") or kline.get("close")
        return float(c) if c is not None else None

    def _action(self, message):
        del message
        order = orders.LimitOrder(
            pair="BTCUSDC",
            side="BUY",
            id_strategy=0,
            id_binance=1,
            price=50e3,
            quantity=0.0004,
        )
        broker.add(
            json.dumps(
                order.__dict__,
                default=lambda obj: (
                    obj.__dict__
                    if not isinstance(obj, datetime)
                    else obj.isoformat()
                ),
            ).encode("utf-8")
        )


def main(broker: Broker) -> None:
    analyst = Analyst(broker, get_sleep())
    analyst.consume()


if __name__ == "__main__":
    main(broker)
