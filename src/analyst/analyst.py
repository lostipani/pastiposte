import time
import ast
import statistics
from collections import deque
from typing import Any, Dict

from commons.logger import logger
from commons.configuration import get_sleep
from commons.rabbitmq import broker
from src.interfaces.broker import Broker
from src.interfaces.consumer import rabbitMQConsumer


class Analyst(rabbitMQConsumer):
    """
    Analyse time series

    Args
        window
        active_order
        trailing_stop
        mean
        std
        max_price_since_order
    """

    def __init__(self, broker: Broker, sleep: float, window: int, **kwargs):
        super().__init__(broker, sleep)
        self.N: int = window
        self.closes = deque(maxlen=window)
        self.timestamps_seen = set()
        self.active_order = kwargs.get("active_order", None)
        self.trailing_stop = kwargs.get("trailing_stop", None)
        self.mean = kwargs.get("mean", None)
        self.std = kwargs.get("std", None)
        self.max_price_since_order = kwargs.get("max_price_since_order", None)

    def on_closed_candle(self, kline: dict):
        # casting to int loses less than second resolution
        # does set membership testing work as expected with float members?
        timestamp = int(kline["t"])
        if timestamp in self.timestamps_seen:
            return
        self.timestamps_seen.add(timestamp)

        close = float(kline["c"])
        open_ = float(kline["o"])
        high = float(kline["h"])
        low = float(kline["l"])

        self.closes.append(close)

        if len(self.closes) == self.N:
            self.mean = statistics.mean(self.closes)
            self.std = statistics.stdev(self.closes)

            logger.info(
                (
                    "[CANDLE CLOSED] Open: %.2f, High: %.2f,"
                    " Low: %.2f, Close: %.2f"
                ),
                open_,
                high,
                low,
                close,
            )
            logger.info(
                ("[STATS] Mean: %.2f, Std: %.2f"),
                self.mean,
                self.std,
            )

            if not self.active_order and close < self.mean - 2 * self.std:
                self.active_order = True
                self.trailing_stop = close - self.std
                self.max_price_since_order = close
                logger.info(
                    "[ORDER] OPEN at %.2f, trailing stop at %.2f",
                    close,
                    self.trailing_stop,
                )

    def on_open_candle(self, close: float):
        if self.active_order:
            # aggiorna il massimo raggiunto da quando l'ordine è stato aperto
            if close > self.max_price_since_order:
                self.max_price_since_order = close

            # aggiorna trailing stop se siamo saliti oltre una std
            new_trailing_stop = self.max_price_since_order - self.std
            if new_trailing_stop > self.trailing_stop:
                self.trailing_stop = new_trailing_stop
                logger.info(
                    "[TRAILING STOP] Updated to %.2f", self.trailing_stop
                )

            # chiusura posizione
            if close < self.trailing_stop:
                logger.info(
                    "[STOP LOSS] Price %.2f hit stop %.2f. Position closed.",
                    close,
                    self.trailing_stop,
                )
                self.active_order = False
                self.trailing_stop = None
                self.max_price_since_order = None
        else:
            logger.info("[LIVE PRICE] Close: %.2f", close)


    def _action(self, data):
        def _parse_message(data) -> Dict[str, Any]:
            parsed = ast.literal_eval(data)
            return {
                "kline": parsed["message"]["data"]["k"],
                "close": float(parsed["message"]["data"]["k"]["c"]),
                "is_closed": parsed["message"]["data"]["k"]["x"],
            }

        try:
            parsed = _parse_message(data)
            if parsed["is_closed"]:
                self.on_closed_candle(parsed["kline"])
            else:
                self.on_open_candle(parsed["close"])
        except KeyError:
            logger.error("Missing data in message")
            raise


def main(broker: Broker) -> None:
    analyst = Analyst(broker, get_sleep(), window=3)
    analyst.consume()


if __name__ == "__main__":
    main(broker)
