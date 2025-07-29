from abc import ABCMeta, abstractmethod
from time import sleep
from typing import Any

from commons.logger import logger
from commons.configuration import get_sleep
from commons.broker import Broker
from commons.rabbitmq import broker


class Consumer(object):
    """
    Abstract class for consumer routine
    """

    __metaclass__ = ABCMeta

    def __init__(self, broker: Broker, sleep: float, **kwargs):
        self.broker = broker
        self.sleep = sleep
        self.kwargs = kwargs

    @abstractmethod
    def consume(self):
        """
        This is the consuming action
        """
        pass


class rabbitConsumer(Consumer):

    def consume(self):
        """
        This is a blocking routine invoking queue reading
        """

        def action(data):
            logger.info(data)

        def callback_fun(channel, method, properties, body):
            """
            RabbitMQ dependent callback
            """
            del channel, method, properties
            action(body.decode("utf-8"))
            sleep(self.sleep)

        self.broker.get(callback=callback_fun)


def main(broker: Broker) -> None:
    consumer = Consumer(broker, get_sleep())
    consumer.consume()


if __name__ == "__main__":
    main(broker)
