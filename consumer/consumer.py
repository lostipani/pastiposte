import time

from commons.logger import logger
from commons.configuration import get_sleep
from commons.broker import Broker
from commons.rabbitmq import broker


def consumer(broker: Broker, sleep: float):

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
        time.sleep(sleep)

    broker.get(callback=callback_fun)


def main(broker: Broker) -> None:
    consumer(broker, get_sleep())


if __name__ == "__main__":
    main(broker)
