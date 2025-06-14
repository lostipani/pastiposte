import time
import ast
import statistics
from collections import deque

from commons.logger import logger
from commons.configuration import get_sleep
from commons.broker import Broker
from commons.rabbitmq import broker


class Analyst:
    def __init__(self, N=3):
        self.N = N
        self.closes = deque(maxlen=N)
        self.timestamps_seen = set()
        self.active_order = False
        self.trailing_stop = None
        self.mean = None
        self.std = None
        self.max_price_since_order = None

    def on_closed_candle(self, kline: dict):
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

            logger.info(f"[CANDLE CLOSED] Open: {open_:.2f}, High: {high:.2f}, Low: {low:.2f}, Close: {close:.2f}")
            logger.info(f"[STATS] Mean: {self.mean:.2f}, Std: {self.std:.2f}")

            if not self.active_order and close < self.mean - 2 * self.std:
                self.active_order = True
                self.trailing_stop = close - self.std
                self.max_price_since_order = close
                logger.info(f"[ORDER] OPEN at {close:.2f}, trailing stop at {self.trailing_stop:.2f}")

    def on_open_candle(self, close: float):
        if self.active_order:
            # aggiorna il massimo raggiunto da quando l'ordine è stato aperto
            if close > self.max_price_since_order:
                self.max_price_since_order = close

            # aggiorna trailing stop se siamo saliti oltre una std
            new_trailing_stop = self.max_price_since_order - self.std
            if new_trailing_stop > self.trailing_stop:
                self.trailing_stop = new_trailing_stop
                logger.info(f"[TRAILING STOP] Updated to {self.trailing_stop:.2f}")

            # chiusura posizione
            if close < self.trailing_stop:
                logger.info(f"[STOP LOSS] Price {close:.2f} hit stop {self.trailing_stop:.2f}. Position closed.")
                self.active_order = False
                self.trailing_stop = None
                self.max_price_since_order = None
        else:
            logger.info(f"[LIVE PRICE] Close: {close:.2f}")


analyst = Analyst(N=3)


def consumer(broker: Broker, sleep: float):
    def action(data):
        try:
            parsed = ast.literal_eval(data)
            message = parsed["message"]
            kline = message["data"]["k"]

            close = float(kline["c"])
            is_closed = kline["x"]

            if is_closed:
                analyst.on_closed_candle(kline)
            else:
                analyst.on_open_candle(close)

        except Exception as e:
            logger.error(f"[ERROR] Messaggio non valido: {e}")

    def callback_fun(channel, method, properties, body):
        del channel, method, properties
        action(body.decode("utf-8"))
        time.sleep(sleep)

    broker.get(callback=callback_fun)


def main(broker: Broker) -> None:
    consumer(broker, get_sleep())


if __name__ == "__main__":
    main(broker)

