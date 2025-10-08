import psycopg
import time
import os
from pprint import pprint

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app_writer:app_writer@localhost:5432/db_orders",
)


def print_orders():
    print("Connecting to database:", DB_URL)
    with psycopg.connect(DB_URL) as conn:
        while True:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_pasticoni, pair, side, price, quantity, status, tracked_by FROM orders ORDER BY timestamp DESC LIMIT 10;"
                )
                rows = cur.fetchall()
                os.system("clear")
                print("=== Latest Orders ===")
                for r in rows:
                    pprint(r)
            time.sleep(2)


if __name__ == "__main__":
    print_orders()
