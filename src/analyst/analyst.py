import os
from transitions import Machine
from interfaces.consumer import rabbitMQConsumer
from interfaces.broker import Broker
from commons.logger import logger
from commons.configuration import get_sleep
from commons.rabbitmq import broker


# ---- STATE MACHINE ---- #

class AnalystStateMachine:
    """
    Trading logic state machine.
    States:
        1. WAIT_OPEN        -> waiting for signal to open a position
        2. WAIT_FILL_ENTRY  -> order placed, waiting for entry fill
        3. WAIT_REVERSAL    -> position open, waiting for reversal signal
        4. WAIT_FILL_EXIT   -> order placed, waiting for exit fill
    """

    states = ["WAIT_OPEN", "WAIT_FILL_ENTRY", "WAIT_REVERSAL", "WAIT_FILL_EXIT"]

    transitions = [
        # price condition or strategy signal reached
        {"trigger": "condition_reached", "source": "WAIT_OPEN", "dest": "WAIT_FILL_ENTRY"},
        {"trigger": "condition_reached", "source": "WAIT_REVERSAL", "dest": "WAIT_FILL_EXIT"},
        # order fills
        {"trigger": "filled", "source": "WAIT_FILL_ENTRY", "dest": "WAIT_REVERSAL"},
        {"trigger": "filled", "source": "WAIT_FILL_EXIT", "dest": "WAIT_OPEN"},
    ]

    def __init__(self):
        # callbacks to be connected by Analyst
        self.place_entry_order = None
        self.place_exit_order = None

        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial="WAIT_OPEN",
            ignore_invalid_triggers=True,
            after_state_change="log_state",
        )

    def log_state(self):
        logger.info(f"State changed to {self.state}")

    # automatic callbacks on entering states
    def on_enter_WAIT_FILL_ENTRY(self):
        logger.info("Entering WAIT_FILL_ENTRY: placing entry order")
        if self.place_entry_order:
            self.place_entry_order()

    def on_enter_WAIT_FILL_EXIT(self):
        logger.info("Entering WAIT_FILL_EXIT: placing exit order")
        if self.place_exit_order:
            self.place_exit_order()


# ---- ANALYST CONSUMER ---- #

class Analyst(rabbitMQConsumer):
    def __init__(self, broker: Broker, sleep_time: float):
        super().__init__(broker, sleep_time)
        self.logic = AnalystStateMachine()

        # connect machine callbacks to real actions
        self.logic.place_entry_order = self.place_entry_order
        self.logic.place_exit_order = self.place_exit_order

    def _action(self, message, *args):
        routing_key = args[1].routing_key

        # accountant updates mean fills or order updates
        if routing_key == "orders.exec_updates":
            logger.info("Update from accountant: trigger filled()")
            self.logic.filled()

        # kline messages carry market conditions
        elif routing_key == "kline_1m":
            logger.info("Kline from exchange: trigger condition_reached()")
            self.logic.condition_reached()

        else:
            logger.warning(f"Unknown routing key: {routing_key}")

        logger.info(f"Current state: {self.logic.state}")

    # ---- Actions triggered by state machine ---- #

    def place_entry_order(self):
        logger.info("Placing entry order via Broker...")
        # integrate actual broker call here
        # self.broker.place_limit_order(...)

    def place_exit_order(self):
        logger.info("Placing exit order via Broker...")
        # integrate actual broker call here
        # self.broker.place_limit_order(...)


# ---- ENTRY POINT ---- #

def main(broker: Broker) -> None:
    analyst = Analyst(broker, get_sleep())
    analyst.consume()


if __name__ == "__main__":
    main(broker)

        """
        order = orders.LimitOrder(
            pair="BTCUSDC",
            side="BUY",
            id_strategy=0,
            id_binance=1,
            price=50e3,
            quantity=0.0004,
            newClientOrderId='ID'
            tracked_by=[os.getenv("ANALYST_ID", "analyst_1")],
        )
        """


