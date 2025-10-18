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
# orders = client.get_open_orders()
orders = client.get_all_orders(symbol="BTCUSDC")
for o in orders:
    print(f"Symbol: {o['symbol']} | ID: {o['orderId']} | Side: {o['side']} | "
          f"Price: {o['price']} | Qty: {o['origQty']} | Status: {o['status']}")

# Open orders
# client.get_open_orders()
# All orders (open + closed + filled) for a symbol
# client.get_all_orders(symbol="BTCUSDC")
# Recent trades you made (executed transactions)
# client.get_my_trades(symbol="BTCUSDC")
# Account snapshot (wallet + positions + transactions summary)
# client.get_account_snapshot(type="SPOT")
# Binance retains order history for about 90 days via this endpoint. For full historical data, you must use the official data export service (on the Binance website, under Transaction History → Export).
# client.get_all_orders(symbol="BTCUSDC", limit=1000, orderId=last_order_id)
# For complete history (beyond 90 days), you must download CSVs from your Binance account or use the Binance Data API (https://data.binance.com
