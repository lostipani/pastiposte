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


import aio_pika
import asyncio
from commons.logger import logger


async def consume_accountant_updates():
    """Listen for updates (like cancellations) from accountant."""
    connection = await aio_pika.connect_robust(
        os.getenv("BROKER_HOST", "rabbitmq")
    )
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        os.getenv("BROKER_EXCHANGE", "exchange"), aio_pika.ExchangeType.DIRECT
    )

    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(
        exchange,
        os.getenv("BROKER_ROUTING_KEY_ACCOUNTANT", "exchange_response"),
    )

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                if data.get("status") == "CANCELED":
                    logger.info(
                        f"Got the cancellation for order {data.get('id_pasticoni')}"
                    )


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


"""
async def main():
    await asyncio.gather(
        consume_market_data(),  # existing market-data loop
        consume_accountant_updates(),  # new cancellation listener
    )
"""

"""
def main(broker: Broker) -> None:
    # Start accountant update listener in a separate thread
    update_thread = threading.Thread(
        target=consume_accountant_updates, daemon=True
    )
    update_thread.start()

    # Main analyst logic (market data listener)
    analyst = Analyst(broker, get_sleep())
    analyst.consume()
"""

if __name__ == "__main__":
    main(broker)
