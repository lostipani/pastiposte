# check_wallet_and_orders.py
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")
print(os.getenv("BINANCE_API_KEY"))


client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

print("\n--- WALLET BALANCES ---")
balances = client.get_account()['balances']
for b in balances:
    free = float(b['free'])
    locked = float(b['locked'])
    if free > 0 or locked > 0:
        print(f"{b['asset']}: free={free}, locked={locked}")

print("\n--- OPEN ORDERS ---")
orders = client.get_open_orders()
for o in orders:
    print(f"Symbol: {o['symbol']} | ID: {o['orderId']} | Side: {o['side']} | "
          f"Price: {o['price']} | Qty: {o['origQty']} | Status: {o['status']}")

