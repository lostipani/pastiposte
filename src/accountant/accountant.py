import asyncio, json, uuid
from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.configuration import get_sleep
from commons.rabbitmq import broker
from commons.logger import logger
from accountant.binance_connector import BinanceConnector


class Accountant(rabbitMQConsumer):
    """Main accountant service."""

    def __init__(self, broker: Broker, sleep: float):
        super().__init__(broker, sleep)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.connector = BinanceConnector()
        self.active_orders = {}  # key=id_pasticoni, value=order data

    def _action(self, data):
        """Required by abstract base class, not used."""
        pass

    async def publish_execution_update(self, event):
        """Publish order status updates to RabbitMQ."""
        msg = {
            "id_pasticoni": event.get("c") or event.get("orderId"),
            "status": event.get("X") or event.get("status"),
            "symbol": event.get("s"),
            "price": event.get("p"),
            "quantity": event.get("q"),
            "eventTime": event.get("E"),
        }
        self.broker.add(json.dumps(msg).encode("utf-8"))
        logger.info(f"Published execution update for {msg['id_pasticoni']}")

    async def listen_exchange_ws(self):
        async def handle_event(event):
            etype = event.get("e")
            if etype in ("executionReport", "ORDER_TRADE_UPDATE"):
                await self.publish_execution_update(event)

        await self.connector.listen_ws(handle_event)

    async def poll_exchange_http(self):
        while True:
            orders = await self.connector.fetch_open_orders()
            logger.info(f"Open orders: {orders}")
            await asyncio.sleep(60)

    def consume_new_orders(self):
        """Listen for new analyst orders."""
        from pika.adapters.blocking_connection import BlockingChannel

        def callback_fun(channel: BlockingChannel, method, properties, body):
            msg = json.loads(body.decode("utf-8"))
            oid = msg.get("id_pasticoni")
            self.active_orders[oid] = msg
            logger.info(f"Received new order {oid} from analyst")

        self.broker.get(callback=callback_fun)

    async def publish_updates(self):
        while True:
            await asyncio.sleep(5)
            msg = {"id": str(uuid.uuid4()), "event": "heartbeat"}
            self.broker.add(json.dumps(msg).encode("utf-8"))
            logger.info("Published update")

    def consume(self):
        """Entry point from rabbitMQConsumer interface."""
        self.loop.run_until_complete(self.run_all())

    async def run_all(self):
        tasks = [
            self.listen_exchange_ws(),
            self.poll_exchange_http(),
            asyncio.to_thread(
                self.consume_new_orders
            ),  # runs the blocking pika consumer in a thread
            self.publish_updates(),
        ]
        await asyncio.gather(*tasks)


def main(broker: Broker) -> None:
    acc = Accountant(broker, get_sleep())
    acc.consume()


if __name__ == "__main__":
    main(broker)
