import asyncio, json, uuid, os
import psycopg
from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.configuration import get_sleep, get_rabbitmq_params
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
        """Required by abstract base class (unused)."""
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
        # Publish generic update for DB writer
        self.broker.add(json.dumps(msg).encode("utf-8"))
        # logger.info(f"Published execution update for {msg['id_pasticoni']}")

        # Also send to analysts or others who are tracking this order
        order = self.active_orders.get(msg["id_pasticoni"])
        if order and order.get("tracked_by"):
            for analyst_id in order["tracked_by"]:
                routing_key = f"orders.exec_updates.{analyst_id}"
                self.broker.channel.basic_publish(
                    exchange=self.broker.params.get("exchange"),
                    routing_key=routing_key,
                    body=json.dumps(msg).encode("utf-8"),
                )
                logger.info(f"Sent update to analyst {analyst_id}")

    async def reconcile(self):
        """Compare DB open orders and exchange open orders at startup."""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("Missing DATABASE_URL for reconciliation")
            return

        logger.info("Starting reconciliation between DB and exchange")
        # Fetch open orders from exchange
        open_orders_exchange = await self.connector.fetch_open_orders()
        exchange_ids = {str(o["orderId"]) for o in open_orders_exchange}

        # Fetch open orders from DB
        try:
            async with await psycopg.AsyncConnection.connect(db_url) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT id_pasticoni, status FROM orders WHERE status='OPEN'"
                    )
                    open_orders_db = {str(row[0]): row[1] async for row in cur}
        except Exception as e:
            logger.error(f"DB reconciliation failed: {e}")
            return

        # Compare and publish corrections
        for db_id in open_orders_db:
            if db_id not in exchange_ids:
                await self.publish_execution_update(
                    {"orderId": db_id, "status": "CANCELLED"}
                )

        for order in open_orders_exchange:
            oid = str(order["orderId"])
            if oid not in open_orders_db:
                await self.publish_execution_update(
                    {"orderId": oid, "status": "NEW"}
                )

        logger.info("Reconciliation complete")

    async def periodic_reconcile(self):
        """Repeat reconcile() every 60 seconds."""
        while True:
            try:
                await self.reconcile()
            except Exception as e:
                logger.error(f"Periodic reconcile failed: {e}")
            await asyncio.sleep(60)

    async def listen_exchange_ws(self):
        async def handle_event(event):
            etype = event.get("e")
            if etype in ("executionReport"):
                # this catches all events fromt he binance API
                logger.info("EXECUTION EVENT!!!")
                # await self.publish_execution_update(event)
            if (
                event.get("e") == "executionReport"
                and event.get("X") == "CANCELED"
            ):
                # this is only in case of cancellation
                logger.info("order canceled → notifying analyst!!!!")
                # then we notify the analyst
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

        # Separate connection to avoid thread conflict
        params = get_rabbitmq_params()
        local_broker = Broker.factory(backend="rabbitmq", **params)
        local_broker.get(callback=callback_fun)

    async def publish_updates(self):
        while True:
            await asyncio.sleep(1)
            msg = {"id": str(uuid.uuid4()), "event": "heartbeat"}
            self.broker.add(json.dumps(msg).encode("utf-8"))
            # logger.info("Published update")

    def consume(self):
        """Entry point."""
        # Run reconciliation first, then start normal tasks
        self.loop.run_until_complete(self.reconcile())
        self.loop.run_until_complete(self.run_all())

    async def run_all(self):
        tasks = [
            self.listen_exchange_ws(),
            self.poll_exchange_http(),
            asyncio.to_thread(self.consume_new_orders),
            self.publish_updates(),
            self.periodic_reconcile(),  # <-- add this line
        ]
        await asyncio.gather(*tasks)


def main(broker: Broker) -> None:
    acc = Accountant(broker, get_sleep())
    acc.consume()


if __name__ == "__main__":
    main(broker)
