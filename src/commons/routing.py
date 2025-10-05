"""
Routing key constants for RabbitMQ message exchange.
Used by all services to avoid mismatches.
"""

"""
# Exchange name (shared)
EXCHANGE = "exchange"
EXCHANGE_TYPE = "direct"

# Routing keys
MARKET_DATA = "market.data"  # listeners → analyst
ORDERS_NEW = "orders.new"  # analysts → accountant
ORDERS_EXEC_UPDATES = (
    "orders.exec_updates"  # accountant → db_writer + analysts
)
ORDERS_DB_UPDATES = "orders.db_updates"  # optional future use
EXCHANGE_RESPONSES = "exchange.responses"  # transmitter → accountant/db_writer

# Optional logging or test keys
LOGGING = "logging"
SIMULATION = "simulation"
"""
