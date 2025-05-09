import time
from typing import Any, Dict
import requests
from requests.exceptions import HTTPError
from retry import retry

from commons.logger import logger
from commons.configuration import get_URI, get_period
from commons.broker import Broker
from commons.rabbitmq import broker


def fetcher(URI: str, broker: Broker, period: float) -> None:

    def action(message):
        """
        This is the action of the fetcher
        """
        data = {"source": URI, "message": message}
        broker.add(str(data), routing_key="fetcher")

    @retry(HTTPError, tries=3, delay=2, logger=logger)
    def get(URI: str) -> Dict[str, Any]:
        response = requests.get(URI)
        response.raise_for_status()
        return response.json()

    while True:
        message = get(URI)
        action(message)
        time.sleep(period)


def main(broker: Broker):
    fetcher(get_URI(), broker, get_period())


if __name__ == "__main__":
    main(broker)
