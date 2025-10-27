import time, json, ast, uuid

from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker

from commons.configuration import Configuration
from commons.rabbitmq import broker


class Analyst(rabbitMQConsumer):

    def _build_order(self, close_price, symbol):
        return {
            "order_id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pair": symbol,
            "side": "BUY",
            "qty": 0.1,
            "type": "MARKET",
            "status": "NEW",
            "strategy_id": "minute-tick",
            "note": f"close={close_price}",
            "version": 1,
        }

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
        kline, _ = self._parse_payload(message)
        symbol = self._symbol_from(kline)
        close = self._close_from(kline)
        order = self._build_order(close, symbol)
        broker.add(json.dumps(order).encode("utf-8"))


def main(broker: Broker) -> None:
    config = Configuration()
    analyst = Analyst(broker, config["sleep"])
    analyst.consume()


if __name__ == "__main__":
    main(broker)
