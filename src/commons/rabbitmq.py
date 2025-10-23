from interfaces.broker import Broker
from commons.configuration import Configuration

config = Configuration()
broker = Broker.factory(
    backend="rabbitmq",
    host=config["host"],
    exchange=config["exchange"],
    exchange_type=config["exchange_type"],
    routing_key_in=config["routing_key_in"],
    routing_key_out=config["routing_key_out"],
)
