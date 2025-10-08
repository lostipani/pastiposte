import os
import json
import asyncio
import threading
import pika
import aio_pika
from commons.models import LimitOrder, Side
from commons.logger import logger

# Broker parameters
BROKER_HOST = os.getenv("BROKER_HOST", "rabbitmq")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE", "exchange")
BROKER_ROUTING_KEY_IN = os.getenv("BROKER_ROUTING_KEY_IN", "kline_1m")
BROKER_ROUTING_KEY_OUT = os.getenv("BROKER_ROUTING_KEY_OUT", "outgoing_orders")
BROKER_ROUTING_KEY_ACCOUNTANT = os.getenv(
    "BROKER_ROUTING_KEY_ACCOUNTANT", "exchange_response"
)


async def consume_market_data():
    """Listen to market data and emit orders."""
    connection = await aio_pika.connect_robust(BROKER_HOST)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        BROKER_EXCHANGE, aio_pika.ExchangeType.DIRECT
    )

    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(exchange, BROKER_ROUTING_KEY_IN)

    logger.info("Analyst ready. Listening for market data...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    logger.info(f"Received kline: {data}")
                except Exception:
                    logger.warning("Invalid kline message.")
                    continue

                # Emit a simple fixed limit order
                order = LimitOrder(
                    symbol="BTCUSDC", side=Side.BUY, price=50000, volume=0.0001
                )
                body = json.dumps(order.dict()).encode()

                await exchange.publish(
                    aio_pika.Message(
                        body=body,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=BROKER_ROUTING_KEY_OUT,
                )
                logger.info(f"Order sent: {order.dict()}")


def consume_accountant_updates():
    """Listen for accountant updates like cancellations."""
    params = pika.ConnectionParameters(host=BROKER_HOST)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.exchange_declare(
        exchange=BROKER_EXCHANGE, exchange_type="direct", durable=False
    )
    q = ch.queue_declare(queue="", exclusive=True).method.queue
    ch.queue_bind(
        exchange=BROKER_EXCHANGE,
        queue=q,
        routing_key=BROKER_ROUTING_KEY_ACCOUNTANT,
    )

    def on_msg(ch_, method, props, body):
        try:
            data = json.loads(body.decode("utf-8"))
            status = (data.get("status") or "").upper()
            if status in ("CANCELED", "CANCELLED"):
                logger.info(
                    f"Got the cancellation for order {data.get('id_pasticoni')}"
                )
        except Exception as e:
            logger.error(f"Accountant update parse error: {e}")
        finally:
            ch_.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=q, on_message_callback=on_msg, auto_ack=False)
    logger.info("Listening for accountant updates...")
    ch.start_consuming()


def main():
    # Start accountant listener thread
    t = threading.Thread(target=consume_accountant_updates, daemon=True)
    t.start()

    # Run the async market data consumer loop
    asyncio.run(consume_market_data())


if __name__ == "__main__":
    main()
