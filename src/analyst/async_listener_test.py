import asyncio
import aio_pika
import os
import json

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")
EXCHANGE_NAME = os.getenv("BROKER_EXCHANGE", "exchange")

ROUTING_KEY_CANDLES = os.getenv("ROUTING_KEY_CANDLES", "kline_1m")
ROUTING_KEY_ORDERS = os.getenv("ROUTING_KEY_ORDERS", "exchange_response")

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


async def brain_loop():
    """Central processor that handles all incoming events serially."""
    while True:
        routing_key, body = await EVENT_Q.get()
        try:
            if routing_key == ROUTING_KEY_CANDLES:
                data = (
                    json.loads(body.replace("'", '"'))
                    if body.strip().startswith("{")
                    else body
                )
                print(f"[CANDLE] {str(data)[:100]}")
            elif routing_key == ROUTING_KEY_ORDERS:
                data = (
                    json.loads(body) if body.strip().startswith("{") else body
                )
                print(f"[ORDER_UPDATE] {str(data)[:100]}")
            else:
                print(f"[UNKNOWN {routing_key}] {body[:80]}")
        finally:
            EVENT_Q.task_done()


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
