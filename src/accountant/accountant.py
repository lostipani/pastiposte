import json
import uuid
from typing import Dict, List

from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.configuration import get_sleep
from commons.rabbitmq import broker
from commons.logger import logger


class Accountant(rabbitMQConsumer):
    """Main accountant service."""

    def __init__(self, broker: Broker, sleep: float):
        super().__init__(broker, sleep)
        self.active_orders: Dict[uuid.UUID, List[str]] = {}

    def _action(self, data, *args):
        if args[1].routing_key == "account.orders":
            logger.info(data)
        elif args[1].routing_key == "orders.outgoing":
            data = json.loads(data)
            self.active_orders[data.get("id_pasticoni")] = data.get(
                "tracked_by"
            )
            logger.info(self.active_orders)
        else:
            raise NotImplementedError


def main(broker: Broker) -> None:
    acc = Accountant(broker, get_sleep())
    acc.consume()


if __name__ == "__main__":
    main(broker)
