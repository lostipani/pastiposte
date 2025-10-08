import os
import asyncio
import aio_pika
import json
from commons.models import LimitOrder, Side

BROKER_HOST = os.getenv("BROKER_HOST", "rabbitmq")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE", "exchange")
BROKER_ROUTING_KEY_IN = os.getenv("BROKER_ROUTING_KEY_IN", "kline_1m")
BROKER_ROUTING_KEY_OUT = os.getenv("BROKER_ROUTING_KEY_OUT", "outgoing_orders")
BROKER_ROUTING_KEY_ACCOUNTANT = os.getenv(
    "BROKER_ROUTING_KEY_ACCOUNTANT", "exchange_response"
)


async def consume_market_data():
    """Consumes klines and emits orders."""
    connection = await aio_pika.connect_robust(BROKER_HOST)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        BROKER_EXCHANGE, aio_pika.ExchangeType.DIRECT
    )

    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(exchange, BROKER_ROUTING_KEY_IN)

    print("Analyst ready. Listening for market data...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    print(f"Received kline: {data}")
                except Exception:
                    print("Invalid kline message.")
                    continue

                # Example logic: send fixed limit order
                order = LimitOrder(
                    symbol="BTCUSDC",
                    side=Side.BUY,
                    price=50_000,
                    volume=0.0004,
                )
                body = json.dumps(order.dict()).encode()

                await exchange.publish(
                    aio_pika.Message(
                        body=body,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=BROKER_ROUTING_KEY_OUT,
                )
                print("Order sent:", order.dict())


async def consume_accountant_updates():
    """Consumes accountant (Binance) updates and prints acknowledgment."""
    connection = await aio_pika.connect_robust(BROKER_HOST)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        BROKER_EXCHANGE, aio_pika.ExchangeType.DIRECT
    )

    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(exchange, BROKER_ROUTING_KEY_ACCOUNTANT)

    print("Analyst listening for accountant updates...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("I saw the update, thank you")


async def main():
    # Run both consumers concurrently
    await asyncio.gather(
        consume_market_data(),
        consume_accountant_updates(),
    )


if __name__ == "__main__":
    asyncio.run(main())
