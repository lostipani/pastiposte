from commons.broker import Broker
from commons.parser import get_rabbitmq_params

broker_params = get_rabbitmq_params()
broker = Broker.factory(
    backend="rabbitmq",
    host=broker_params.get("host"),
    exchange=broker_params.get("exchange"),
    exchange_type=broker_params.get("exchange_type"),
    routing_key=broker_params.get("routing_key"),
)
