import json
import time
from websockets.sync.client import connect

from commons.logger import logger
from commons.parser import get_URI, get_listener_period
from commons.broker import Broker
from rabbitmq import broker


def listener(URI: str, broker: Broker, period: float) -> None:

    def action(message):
        """
        This is the action of the listener
        """
        data = {"source": URI, "message": json.loads(message)}
        broker.add(str(data))

    try:
        with connect(URI) as websocket:
            for message in websocket:
                action(message)
                time.sleep(period)
    except ConnectionRefusedError as error:
        logger.error(error)
        raise


def main(broker: Broker):
    listener(get_URI(), broker, get_listener_period())


if __name__ == "__main__":
    main(broker)
