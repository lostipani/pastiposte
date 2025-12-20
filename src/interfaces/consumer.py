"""
Consumer interfaces
"""

import json
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Dict

from interfaces.message_broker import Broker


class Consumer(ABC):
    """
    Interface class for consumer
    """

    def __init__(self, broker: Broker, sleep: float, **kwargs):
        self.broker = broker
        self.sleep = sleep
        self.kwargs = kwargs

    @abstractmethod
    def consume(self) -> Any:
        """
        This is the consuming routine
        """
        pass


class RabbitMQConsumer(Consumer):
    """
    Interface class for a RabbitMQ dependant consumer
    """

    @abstractmethod
    def _action(self, message: Dict[str, Any]) -> Any:
        """
        This is the consuming action once the message is fetched from the queue
        """
        pass

    def consume(self):
        """
        This is a blocking routine fetching the queue
        """

        def callback_fun(channel, method, properties, body):
            """
            RabbitMQ dependent callback
            """
            del channel, method, properties
            self._action(json.loads(body))
            sleep(self.sleep)

        self.broker.get(callback=callback_fun)
