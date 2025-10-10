import asyncio
import aio_pika
import os

RABBIT_URL = os.getenv(
    "RABBIT_URL", "amqp://guest:guest@rabbitmq/"
)  # same host as compose
QUEUE_NAME = os.getenv("BROKER_ROUTING_KEY_IN", "kline_1m")


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"[{QUEUE_NAME}] {message.body.decode()[:120]}")


async def main():
    # Connect once
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare or get existing queue
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    # Start consuming asynchronously
    await queue.consume(on_message)

    print(f"Listening on queue '{QUEUE_NAME}'... Ctrl+C to stop.")
    await asyncio.Future()  # keep process alive


if __name__ == "__main__":
    asyncio.run(main())
