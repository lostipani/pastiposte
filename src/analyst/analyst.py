import json, ast
from datetime import datetime
import uuid
import os
from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker

from commons.configuration import get_sleep
from commons.rabbitmq import broker
from orders import orders


import threading
from commons.configuration import get_rabbitmq_params
from interfaces.broker import Broker


def consume_exchange_response_updates():
    """Listen to global accountant updates (exchange_response)."""
    params = get_rabbitmq_params()
    params["routing_key_in"] = os.getenv(
        "BROKER_ROUTING_KEY_ACCOUNTANT", "exchange_response"
    )
    response_broker = Broker.factory(backend="rabbitmq", **params)

    def callback_fun(channel, method, properties, body):
        update = json.loads(body)
        logger.info(
            f"########## Received global accountant update: {update} ##########"
        )

    response_broker.get(callback=callback_fun)


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
            quantity=0.0001,
            tracked_by=[os.getenv("ANALYST_ID", "analyst_1")],
        )
        broker.add(
            json.dumps(
                order.__dict__,
                default=lambda obj: (
                    obj.__dict__
                    if not isinstance(obj, uuid.UUID)
                    else str(obj)
                ),
            ).encode("utf-8")
        )


def main(broker: Broker) -> None:
    # Start main analyst logic first
    analyst = Analyst(broker, get_sleep())

    # Start accountant listener threads AFTER analyst is running
    update_thread = threading.Thread(
        target=consume_accountant_updates, daemon=True
    )
    update_thread.start()

    global_thread = threading.Thread(
        target=consume_exchange_response_updates, daemon=True
    )
    global_thread.start()

    analyst.consume()


if __name__ == "__main__":
    main(broker)
