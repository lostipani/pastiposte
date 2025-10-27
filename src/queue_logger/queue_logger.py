from typing import Any

from interfaces.broker import Broker
from interfaces.consumer import rabbitMQConsumer
from commons.logger import logger
from commons.configuration import Configuration
from commons.rabbitmq import broker


class queueLogger(rabbitMQConsumer):

    def _action(self, data: Any):
        logger.info(data)


def main(broker: Broker) -> None:
    config = Configuration()
    queue_logger = queueLogger(broker, config["sleep"])
    queue_logger.consume()


if __name__ == "__main__":
    main(broker)
