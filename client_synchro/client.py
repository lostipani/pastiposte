import json
import time
from websockets.sync.client import connect

from commons.logger import logger
from commons.parser import get_URI, get_listener_period, get_consumer_period
from commons.broker import Broker


def listener(broker: Broker, message: str, period: float):
    broker.add(json.loads(message)["value"])
    time.sleep(period)


def consumer(broker: Broker, period: float):
    logger.info(broker.get())
    time.sleep(period)


def main(broker: Broker) -> None:
    try:
        with connect(get_URI()) as websocket:
            for message in websocket:
                listener(broker, message, get_listener_period())
                consumer(broker, get_consumer_period())
    except ConnectionRefusedError as error:
        logger.error(error)
        raise


if __name__ == "__main__":
    broker = Broker.factory(backend=[])
    main(broker)
