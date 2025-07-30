from src.interfaces.broker import Broker
from src.commons.configuration import get_rabbitmq_params

broker_params = get_rabbitmq_params()
broker = Broker.factory(
    backend="rabbitmq",
    host=broker_params.get("host"),
    exchange=broker_params.get("exchange"),
    exchange_type=broker_params.get("exchange_type"),
    routing_key=broker_params.get("routing_key"),
)
