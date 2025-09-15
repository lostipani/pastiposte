from os import getenv
from binance.spot import Spot

client = Spot(
    api_key=getenv("BINANCE_API_KEY"),
    api_secret=getenv("BINANCE_API_SECRET"),
    base_url="https://api.binance.com",
    # base_url="https://testnet.binance.vision"
)

# 1) Connectivity / server time
print(client.time())  # should return {"serverTime": ...}

# 2) Account snapshot (balances, permissions)
acct = client.account()
print([b for b in acct["balances"] if float(b["free"]) > 0])

# 3) Place a $10 market BUY on BTCUSDT using quote qty
#order = client.new_order(
#    symbol="BTCUSDT", side="BUY", type="MARKET", quoteOrderQty="10"
#)

info = client.exchange_info(symbol="BTCUSDC")
print(info["symbols"][0]["filters"])

order = client.new_order(
    symbol="BTCUSDC",
    side="BUY",
    type="LIMIT",
    timeInForce="GTC",       # GTC | IOC | FOK
    quantity="0.0004",        # base asset qty (must match LOT_SIZE filter)
    price="28123"            # must match PRICE_FILTER tick size
)
print(order)                 # contains orderId, status, etc.

# ----- check order status -----
status = client.get_order(symbol="BTCUSDC", orderId=order["orderId"])
print(status)




