import time

from commons.logger import logger
from commons.parser import get_broker_params, get_consumer_period
from commons.broker import Broker


def consumer(broker: Broker, period: float):

    def action(data):
        """
        This is the action of the consumer
        """
        logger.info(data)

    def callback_fun(channel, method, properties, body):
        """
        RabbitMQ dependent callback function to deal with incoming message
        """
        del channel, method, properties
        action(body.decode("utf-8"))
        time.sleep(period)

    broker.get(callback=callback_fun, queue="http", routing_key="fetcher")
    broker.get(callback=callback_fun, queue="ws", routing_key="listener")


def main(broker: Broker) -> None:
    consumer(broker, get_consumer_period())


if __name__ == "__main__":
    broker_params = get_broker_params()
    broker = Broker.factory(
        backend="rabbitmq",
        host=broker_params.get("host"),
        exchange="x",
        exchange_type="direct",
    )
    main(broker)
