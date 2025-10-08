import os, time, json

import psycopg

from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.configuration import get_sleep
from commons.rabbitmq import broker
from commons.logger import logger

DB_URL = os.environ.get("DATABASE_URL")


class DBWriter(rabbitMQConsumer):

    def _validate_envelope(self, o):
        required = [
            "timestamp",
            "id_pasticoni",
            "pair",
            "side",
            "quantity",
            "type",
            "status",
            "timeInForce",
            "newOrderRespType",
        ]
        for field in required:
            if field not in o:
                raise ValueError(f"missing field: {field}")

    def _insert_order(self, o):
        conn = self.kwargs["db_conn"]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (timestamp, id_pasticoni, pair, side, quantity, price,
                                    type, status, timeInForce, newOrderRespType)
                VALUES (%(timestamp)s, %(id_pasticoni)s, %(pair)s, %(side)s, %(quantity)s,
                        %(price)s, %(type)s, %(status)s, %(timeInForce)s, %(newOrderRespType)s)
                ON CONFLICT (id_pasticoni)
                DO UPDATE
                SET status = EXCLUDED.status,
                    price = EXCLUDED.price,
                    quantity = EXCLUDED.quantity,
                    timestamp = EXCLUDED.timestamp;
                """,
                {
                    "timestamp": o.get("timestamp"),
                    "id_pasticoni": o.get("id_pasticoni"),
                    "pair": o.get("pair"),
                    "side": o.get("side"),
                    "quantity": o.get("quantity"),
                    "price": o.get("price"),
                    "type": o.get("type"),
                    "status": o.get("status"),
                    "timeInForce": o.get("timeInForce"),
                    "newOrderRespType": o.get("newOrderRespType"),
                },
            )
        conn.commit()
        logger.info(
            f"Order {o.get('id_pasticoni')} written/updated with status {o.get('status')}"
        )


'''
    def _insert_order(self, o):
        conn = self.kwargs["db_conn"]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (timestamp, id_pasticoni,pair, side, quantity, price, type, status, timeInForce, newOrderRespType)
                VALUES (%(timestamp)s, %(id_pasticoni)s, %(pair)s, %(side)s, %(quantity)s, %(price)s, %(type)s, %(status)s, %(timeInForce)s, %(newOrderRespType)s);
            """,
                {
                    "timestamp": o.get("timestamp"),
                    "id_pasticoni": o.get("id_pasticoni"),
                    "pair": o.get("pair"),
                    "side": o.get("side"),
                    "quantity": o.get("quantity"),
                    "price": o.get("price"),
                    "type": o.get("type"),
                    "status": o.get("status"),
                    "timeInForce": o.get("timeInForce"),
                    "newOrderRespType": o.get("newOrderRespType"),
                    "tracked_by": o.get("tracked_by"),
                },
            )
        conn.commit()

    def _action(self, message):
        body = json.loads(message)
        self._validate_envelope(body)
        self._insert_order(body)

'''


def wait_for_orders_table(conn, retries=30, delay=1.0):
    q = """select 1 from information_schema.tables
           where table_schema='public' and table_name='orders'"""
    for _ in range(retries):
        with conn.cursor() as cur:
            cur.execute(q)
            if cur.fetchone():
                return
        time.sleep(delay)
    raise RuntimeError(
        "orders table not found; schema-migrator may have failed"
    )


def main(broker: Broker) -> None:
    db = psycopg.connect(DB_URL, autocommit=False)
    wait_for_orders_table(db)
    db_writer = DBWriter(broker, get_sleep(), db_conn=db)
    db_writer.consume()


if __name__ == "__main__":
    main(broker)
