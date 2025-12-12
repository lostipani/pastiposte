import os, time, json

import psycopg

from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.configuration import Configuration
from commons.rabbitmq import broker
from commons.logger import logger

DB_URL = os.environ.get("DATABASE_URL")


class DBWriter(rabbitMQConsumer):

    def _validate_envelope(self, o):
        required = [
            "order_id",
            "timestamp",
            "pair",
            "side",
            "qty",
            "type",
            "status",
            "version",
        ]
        for k in required:
            if k not in o:
                raise ValueError(f"missing field: {k}")

    def _insert_order(self, o):
        conn = self.kwargs["db_conn"]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (order_id, "timestamp", pair, side, qty, type, status, strategy_id, note, version)
                VALUES (%(order_id)s, %(timestamp)s, %(pair)s, %(side)s, %(qty)s, %(type)s, %(status)s, %(strategy_id)s, %(note)s, %(version)s)
                ON CONFLICT (order_id) DO NOTHING;
            """,
                {
                    "order_id": o.get("order_id"),
                    "timestamp": o.get("timestamp"),
                    "pair": o.get("pair"),
                    "side": o.get("side"),
                    "qty": o.get("qty"),
                    "type": o.get("type"),
                    "status": o.get("status"),
                    "strategy_id": o.get("strategy_id"),
                    "note": o.get("note"),
                    "version": o.get("version", 1),
                },
            )
        conn.commit()

    def _action(self, message):
        body = json.loads(message)
        self._validate_envelope(body)
        self._insert_order(body)
        # broker.add(json.dumps(order).encode("utf-8"))


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
    config = Configuration()
    db = psycopg.connect(DB_URL, autocommit=False)
    wait_for_orders_table(db)
    db_writer = DBWriter(broker, config["sleep"], db_conn=db)
    db_writer.consume()


if __name__ == "__main__":
    main(broker)
