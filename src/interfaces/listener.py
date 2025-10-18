import os
import json
import time
from typing import Any, Dict
from urllib.parse import urlparse

import requests
from requests import HTTPError
from retry import retry
from websockets.sync.client import connect

from commons.logger import logger
from commons.configuration import get_URL, get_authn_URL, get_sleep
from commons.rabbitmq import broker
from interfaces.broker import Broker


class Listener:

    def __init__(self):
        pass

    @staticmethod
    def factory(url: str, **kwargs):
        if urlparse(url).scheme in {"ws", "wss"}:
            if kwargs["authn_url"]:
                return ListenerWSAuthn(url, kwargs["authn_url"])
            return ListenerWS(url)
        elif urlparse(url).scheme in {"http", "https"}:
            return ListenerHTTP(url)
        else:
            raise NotImplementedError


class ListenerWS(Listener):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self, broker: Broker, sleep: float):
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
                    time.sleep(sleep)
        except ConnectionRefusedError as error:
            logger.error(error)
            raise


class ListenerWSAuthn(Listener):
    """
    Listener Websocket with authentication via API TOKEN.
    """

    def __init__(self, url: str, authn_url: str):
        super().__init__()
        self.url = url
        self.authn_url = authn_url
        self.api_key = os.getenv("BINANCE_API_KEY")

    def get_listen_key(self) -> str:
        response = requests.get(
            self.authn_url, headers={"X-MBX-APIKEY": self.api_key}
        )
        response.raise_for_status()
        return response.json()["listenKey"]

    def run(self, broker: Broker, sleep: float):
        def _action(message) -> None:
            """
            This is the action of the listener
            """
            broker.add(
                str({"source": self.url, "message": json.loads(message)})
            )

        url = f"{self.url}/{self.get_listen_key()}"
        try:
            with connect(url) as websocket:
                for message in websocket:
                    _action(message)
                    time.sleep(sleep)
        except ConnectionRefusedError as error:
            logger.error(error)
            raise


class ListenerHTTP(Listener):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self, broker: Broker, sleep: float):
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
            time.sleep(sleep)


def main(broker: Broker):
    listener = Listener.factory(get_URL(), authn_url=get_authn_URL())
    listener.run(broker, get_sleep())


if __name__ == "__main__":
    main(broker)
