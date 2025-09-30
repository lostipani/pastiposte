import time
import json
from os import getenv

from binance.spot import Spot

from commons.configuration import get_URL, get_sleep
from interfaces.broker import Broker
from commons.rabbitmq import broker
from commons.logger import logger
from orders.orders import Order



class Accountant:
    def __init__(self, url: str, broker: Broker):
        self.url = url
        self.broker = broker
        self.client = self._connect()

    def _connect(self):
        return Spot(
            api_key=getenv("BINANCE_API_KEY"),
            api_secret=getenv("BINANCE_API_SECRET"),
            base_url=self.url,
        )

    def updateDB(self, sleep: float):

        def callback_fun(channel, method, properties, body):
			order_list = ...
			request_book = ...self.client....(order_list)
			response = write_changes(request_book)
            logger.info(response)
            time.sleep(sleep)

        self.broker.get(callback=callback_fun)


def main(broker: Broker):
    transmitter = Accountant(get_URL(), broker)
    transmitter.updateDB(get_sleep())


if __name__ == "__main__":
    main(broker)
