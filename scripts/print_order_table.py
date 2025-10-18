import psycopg
import time
import os
from prettytable import PrettyTable

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app_writer:app_writer@localhost:5432/db_orders",
)


def print_orders():
    seen_ids = set()
    print("Connecting to database:", DB_URL)
    with psycopg.connect(DB_URL) as conn:
        while True:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id_pasticoni, pair, side, price, quantity, status, tracked_by
                       FROM orders
                       ORDER BY timestamp DESC
                       LIMIT 10;"""
                )
                rows = cur.fetchall()

            os.system("clear")
            table = PrettyTable(
                ["ID", "PAIR", "SIDE", "PRICE", "QTY", "STATUS", "TRACKED_BY"]
            )
            new_ids = {r[0] for r in rows}

            for r in rows:
                mark = "*" if r[0] not in seen_ids else ""
                table.add_row(
                    [f"{r[0]}{mark}", r[1], r[2], r[3], r[4], r[5], r[6]]
                )

            print("=== Latest Orders ===")
            print(table)
            if new_ids - seen_ids:
                print("\n* = new since last refresh")
            seen_ids = new_ids
            time.sleep(2)


if __name__ == "__main__":
    print_orders()
