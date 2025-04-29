import json
import time
from websockets.sync.client import connect

from commons.logger import logger
from commons.parser import get_URI, get_listener_period, get_broker_params
from commons.broker import Broker


def listener(URI: str, broker: Broker, period: float) -> None:

    def action(message):
        """
        This is the action of the listener
        """
        data = {"source": URI, "message": json.loads(message)}
        broker.add(str(data), routing_key="listener")

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
    broker_params = get_broker_params()
    broker = Broker.factory(
        backend="rabbitmq",
        host=broker_params.get("host"),
        exchange="x",
        exchange_type="direct",
    )
    main(broker)
