import json, ast
from datetime import datetime
import os
from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker

from commons.configuration import get_sleep
from commons.logger import logger
from commons.rabbitmq import broker
from orders import orders

from commons.configuration import get_rabbitmq_params
from interfaces.broker import Broker


class Analyst(rabbitMQConsumer):

    def _action(self, message, *args):

        del message

        # If the message comes from the accontant
        if args[1].routing_key == "orders.exec_updates":
            logger.info("Update from accountant")
        # If the message comes from the Listener (i.e. API)
        elif args[1].routing_key == "kline_1m":
            logger.info("Kline from binance")

        """
        order = orders.LimitOrder(
            pair="BTCUSDC",
            side="BUY",
            id_strategy=0,
            id_binance=1,
            price=50e3,
            quantity=0.0004,
            tracked_by=[os.getenv("ANALYST_ID", "analyst_1")],
        )
        """


def main(broker: Broker) -> None:

    # Main analyst logic (market data listener)
    analyst = Analyst(broker, get_sleep())
    analyst.consume()


if __name__ == "__main__":

    main(broker)
