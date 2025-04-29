import json
import time
from concurrent.futures import ThreadPoolExecutor
from websockets.sync.client import connect

from commons.logger import logger
from commons.parser import get_URI, get_listener_period, get_consumer_period
from commons.broker import Broker


def listener(URI: str, broker: Broker, period: float) -> None:
    try:
        with connect(URI) as websocket:
            for message in websocket:
                broker.add(json.loads(message)["value"])
                time.sleep(period)
    except ConnectionRefusedError as error:
        logger.error(error)
        raise


def consumer(broker: Broker, period: float):
    while True:
        if broker.is_empty():
            logger.warning("no data")
        else:
            logger.info(broker.get())
        time.sleep(period)


def main(broker: Broker):
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(listener, get_URI(), broker, get_listener_period())
        executor.submit(consumer, broker, get_consumer_period())


if __name__ == "__main__":
    from queue import Queue

    broker = Broker.factory(backend=Queue())
    main(broker)
