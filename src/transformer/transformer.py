import json
from statistics import mean, stdev, StatisticsError
from typing import Any

from interfaces.message_broker import Broker
from interfaces.consumer import RabbitMQConsumer
from commons.logger import logger
from commons.configuration import Configuration
from commons.broker import broker


class Transformer(RabbitMQConsumer):

    def _action(self, message: Any):
        message = json.loads(message)
        try:
            self.broker.add(
                {"avg": mean(message["response"])},
                routing_key="transformed.avg",
            )
            self.broker.add(
                {"std": stdev(message["response"])},
                routing_key="transformed.std",
            )
        except (TypeError, StatisticsError):
            logger.exception("message")
            pass


def main(broker: Broker) -> None:
    config = Configuration()
    transformer = Transformer(broker, config["sleep"])
    transformer.consume()


if __name__ == "__main__":
    main(broker)
