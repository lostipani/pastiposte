# enter into the container
#  docker exec -it deploy-analyst-1 bash
# run the script
# python -m analyst.strategy_test

import asyncio
import aio_pika
import os
import json

from analyst.events import parse_raw, CandleEvent, OrderUpdateEvent
from analyst.state import StrategyState

from analyst.events import parse_raw, CandleEvent, OrderUpdateEvent
from analyst.strategy_matrix import MatrixStrategy
from analyst.async_publisher import AsyncPublisher


RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")
EXCHANGE_NAME = os.getenv("BROKER_EXCHANGE", "exchange")

ROUTING_KEY_CANDLES = os.getenv("ROUTING_KEY_CANDLES", "kline_1m")
ROUTING_KEY_ORDERS = os.getenv("ROUTING_KEY_ORDERS", "orders.exec_updates")

EVENT_Q = asyncio.Queue()


async def consume_queue(routing_key: str):
    """Connect, create ephemeral queue, bind, and push messages to EVENT_Q."""
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=False
    )
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange, routing_key)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = message.body.decode()
                await EVENT_Q.put((routing_key, body))


STATE = StrategyState()
PUBLISHER = AsyncPublisher()
STRATEGY = None  # set after publisher starts


async def brain_loop():
    while True:
        routing_key, body = await EVENT_Q.get()
        try:
            ev = parse_raw(routing_key, body)
            if ev is None:
                continue
            await STRATEGY.handle(ev)
        finally:
            EVENT_Q.task_done()


async def main():
    await PUBLISHER.start()
    global STRATEGY
    STRATEGY = MatrixStrategy(
        PUBLISHER, k_sigma=2.0, trail_pct=0.02, min_n=20, default_qty=0.001
    )
    consumers = [
        asyncio.create_task(consume_queue(ROUTING_KEY_CANDLES)),
        asyncio.create_task(consume_queue(ROUTING_KEY_ORDERS)),
        asyncio.create_task(brain_loop()),
    ]
    print(
        f"Listening on routing keys '{ROUTING_KEY_CANDLES}' and '{ROUTING_KEY_ORDERS}'"
    )
    await asyncio.gather(*consumers)


async def main():
    # Run both listeners concurrently and the brain loop
    consumers = [
        asyncio.create_task(consume_queue(ROUTING_KEY_CANDLES)),
        asyncio.create_task(consume_queue(ROUTING_KEY_ORDERS)),
        asyncio.create_task(brain_loop()),
    ]
    print(
        f"Listening on routing keys '{ROUTING_KEY_CANDLES}' and '{ROUTING_KEY_ORDERS}'"
    )
    await asyncio.gather(*consumers)


if __name__ == "__main__":
    asyncio.run(main())
