import time
from os import getenv

from binance.spot import Spot

from commons.configuration import get_URL, get_sleep
from interfaces.broker import Broker
from commons.rabbitmq import broker
from commons.logger import logger


class TransmitterBinanceHTTP:
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

    def run(self, sleep: float):

        def callback_fun(channel, method, properties, body):
            """
            RabbitMQ dependent callback
            message contains
            symbol=kwargs["symbol"]
            symbol="BTCUSDC",
            side="BUY",
            type="LIMIT",
            timeInForce="GTC",
            quantity="0.0004",
            price="28123"
            """
            del channel, method, properties
            # self.client.new_order(**body)
            logger.info(body)
            time.sleep(sleep)

        self.broker.get(callback=callback_fun)


def main(broker: Broker):
    transmitter = TransmitterBinanceHTTP(get_URL(), broker)
    transmitter.run(get_sleep())


if __name__ == "__main__":
    main(broker)
