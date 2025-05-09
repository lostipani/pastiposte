import json
import time
from typing import Any, Dict
from urllib.parse import urlparse

import requests
from requests import HTTPError
from retry import retry
from websockets.sync.client import connect

from commons.logger import logger
from commons.configuration import get_URL, get_period
from commons.broker import Broker
from commons.rabbitmq import broker


class Listener:

    def __init__(self):
        pass

    @staticmethod
    def factory(url: str):
        if urlparse(url).scheme in {"ws", "wss"}:
            return ListenerWS(url)
        elif urlparse(url).scheme in {"http", "https"}:
            return ListenerHTTP(url)
        else:
            raise NotImplementedError


class ListenerWS(Listener):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self, broker: Broker, period: float):
        def _action(message) -> None:
            """
            This is the action of the listener
            """
            broker.add(
                str({"source": self.url, "message": json.loads(message)})
            )

        try:
            with connect(self.url) as websocket:
                for message in websocket:
                    _action(message)
                    time.sleep(period)
        except ConnectionRefusedError as error:
            logger.error(error)
            raise


class ListenerHTTP(Listener):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self, broker: Broker, period: float):
        def _action(message) -> None:
            """
            This is the action of the listener
            """
            broker.add(str({"source": self.url, "message": message}))

        @retry(HTTPError, tries=3, delay=2, logger=logger)
        def _get(url: str) -> Dict[str, Any]:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        while True:
            message = _get(self.url)
            _action(message)
            time.sleep(period)


def main(broker: Broker):
    listener = Listener.factory(get_URL())
    listener.run(broker, get_period())


if __name__ == "__main__":
    main(broker)
