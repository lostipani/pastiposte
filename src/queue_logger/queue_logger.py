from typing import Any

from interfaces.message_broker import Broker
from interfaces.consumer import RabbitMQConsumer
from commons.logger import logger
from commons.configuration import Configuration
from commons.broker import broker


class QueueLogger(RabbitMQConsumer):

    def _action(self, message: Any):
        logger.info(message)


def main(broker: Broker) -> None:
    config = Configuration()
    queue_logger = QueueLogger(broker, config["sleep"])
    queue_logger.consume()


if __name__ == "__main__":
    main(broker)
