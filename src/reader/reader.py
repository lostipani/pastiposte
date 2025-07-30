from typing import Any

from commons.logger import logger
from commons.configuration import get_sleep
from commons.rabbitmq import broker
from src.interfaces.broker import Broker
from src.interfaces.consumer import rabbitMQConsumer

class Reader(rabbitMQConsumer):
    
    def _action(self, data: Any):
        logger.info(data)

def main(broker: Broker) -> None:
    reader = Reader(broker, get_sleep())
    reader.consume()


if __name__ == "__main__":
    main(broker)
