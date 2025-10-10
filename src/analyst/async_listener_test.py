import asyncio
import aio_pika
import os

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")
EXCHANGE_NAME = os.getenv("BROKER_EXCHANGE", "exchange")
ROUTING_KEY = os.getenv("BROKER_ROUTING_KEY_IN", "kline_1m")


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"[{ROUTING_KEY}] {message.body.decode()[:120]}")


async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare exchange first (same name/type as publisher)
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True
    )

    # Declare an exclusive, auto-deleted queue with random name
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange, ROUTING_KEY)

    print(f"Listening on routing key '{ROUTING_KEY}' via queue '{queue.name}'")
    await queue.consume(on_message)

    await asyncio.Future()  # keep alive


if __name__ == "__main__":
    asyncio.run(main())
