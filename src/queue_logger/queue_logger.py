from typing import Any

from src.interfaces.broker import Broker
from src.interfaces.consumer import rabbitMQConsumer
from src.commons.logger import logger
from src.commons.configuration import get_sleep
from src.commons.rabbitmq import broker


class queueLogger(rabbitMQConsumer):

    def _action(self, data: Any):
        logger.info(data)


def main(broker: Broker) -> None:
    queue_logger = queueLogger(broker, get_sleep())
    queue_logger.consume()


if __name__ == "__main__":
    main(broker)
