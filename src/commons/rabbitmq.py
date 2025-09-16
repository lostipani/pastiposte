from interfaces.broker import Broker
from commons.configuration import get_rabbitmq_params

broker_params = get_rabbitmq_params()
broker = Broker.factory(
    backend="rabbitmq",
    host=broker_params.get("host"),
    exchange=broker_params.get("exchange"),
    exchange_type=broker_params.get("exchange_type"),
    routing_key_in=broker_params.get("routing_key_in"),
    routing_key_out=broker_params.get("routing_key_out"),
)
