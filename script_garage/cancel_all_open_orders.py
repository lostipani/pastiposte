# script to canel all the open orders
from binance.client import Client
from dotenv import load_dotenv
import os, time

# Load API keys
load_dotenv(dotenv_path="../.env")
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

print("\n--- FETCHING OPEN ORDERS ---")
open_orders = client.get_open_orders()
if not open_orders:
    print("No open orders found.")
    exit(0)

print(f"Found {len(open_orders)} open orders.\n")

# Group by symbol (Binance requires symbol for cancel)
orders_by_symbol = {}
for o in open_orders:
    orders_by_symbol.setdefault(o["symbol"], []).append(o)

# Cancel all orders symbol by symbol
for symbol, orders in orders_by_symbol.items():
    print(f"\nCancelling {len(orders)} orders for {symbol}...")
    for o in orders:
        try:
            resp = client.cancel_order(symbol=symbol, orderId=o["orderId"])
            print(
                f"Cancelled {symbol} order {o['orderId']} → {resp['status']}"
            )
            time.sleep(0.2)  # short delay to avoid hitting rate limits
        except Exception as e:
            print(f"Error cancelling {symbol} order {o['orderId']}: {e}")

print("\n✅ All cancellable orders processed.")
