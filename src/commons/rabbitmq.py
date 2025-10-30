from interfaces.broker import Broker
from commons.configuration import Configuration

config = Configuration()
broker = Broker.factory(
    backend="rabbitmq",
    host=config.get("host"),
    exchange=config.get("exchange"),
    exchange_type=config.get("exchange_type"),
    routing_key_in=config.get("routing_key_in"),
    routing_key_out=config.get("routing_key_out"),
)
