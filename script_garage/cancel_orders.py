# cancel_orders.py
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

# example: cancel specific orders by ID and symbol
to_cancel = [
    {"symbol": "BTCUSDT", "orderId": 12345678},
    {"symbol": "ETHUSDT", "orderId": 23456789},
]

for o in to_cancel:
    result = client.cancel_order(symbol=o["symbol"], orderId=o["orderId"])
    print(f"Cancelled: {o['symbol']} order {o['orderId']} -> {result['status']}")

