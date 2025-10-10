import os, json, aio_pika

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")
EXCHANGE = os.getenv("BROKER_EXCHANGE", "exchange")
ROUTING_OUT = os.getenv(
    "BROKER_ROUTING_KEY_OUT", "orders.new"
)  # accountant listens here


class AsyncPublisher:
    def __init__(self):
        self._conn = None
        self._chan = None
        self._ex = None

    async def start(self):
        self._conn = await aio_pika.connect_robust(RABBIT_URL)
        self._chan = await self._conn.channel()
        await self._chan.set_qos(prefetch_count=1)
        self._ex = await self._chan.declare_exchange(
            EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=False
        )

    async def publish_order(self, order: dict):
        body = json.dumps(order).encode("utf-8")
        msg = aio_pika.Message(
            body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self._ex.publish(msg, routing_key=ROUTING_OUT)
