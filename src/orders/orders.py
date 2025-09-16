"""Order definition module."""

from datetime import datetime, timezone
from typing import List, Literal
from dataclasses import dataclass
import uuid


class OrderArgumentError(Exception):
    pass


@dataclass
class Order:
    """Order base class."""

    id_strategy: int
    pair: str
    id_binance: int
    side: Literal["SELL", "BUY"]
    type: Literal[
        "LIMIT",
        "MARKET",
        "STOP_LOSS",
        "STOP_LOSS_LIMIT",
        "TAKE_PROFIT",
        "TAKE_PROFIT_LIMIT",
        "LIMIT_MAKER",
    ]
    id_pasticoni: uuid.UUID | None = None
    timestamp: str | None = None
    newOrderRespType: Literal["ACK", "RESULT", "FULL"] = "FULL"
    timeInForce: Literal["GTC", "IOC", "FOK"] = "GTC"
    status: Literal[
        "FILLED", "PARTIAL", "OPEN", "FROZEN", "CANCELLED", "PARTIAL-CANCELLED"
    ] = "OPEN"
    comments: str | None = None
    id_competitors: List[int] | None = None

    def _xor_args_parser(self, *args, **kwargs):
        """
        Parse mutually exclusive pairs as order attributes.
        """
        #        if kwargs.get(args[0], False) ^ kwargs.get(args[1], False):
        #            raise OrderArgumentError(f"provide {args[0]} XOR {args[1]}")
        try:
            setattr(self, args[0], kwargs[args[0]])
        except KeyError:
            setattr(self, args[1], kwargs[args[1]])

    def _or_args_parser(self, *args, **kwargs):
        """
        Parse union of pairs as order attributes.
        """
        if not kwargs.get(args[0]) and not kwargs.get(args[1]):
            raise OrderArgumentError(f"provide {args[0]} OR {args[1]}")
        for arg in args:
            if arg in kwargs.keys():
                setattr(self, arg, kwargs[arg])


class LimitOrder(Order):
    """
    Limit Order.

    Args:
        pair
        side
        id_strategy
        id_binance
        price
        quantity: the amount of the asset the user wants to buy or sell at the
                  market price. Excludes quoteOrderQty
        timestamp: Default now.
        newOrderRespType: Default FULL
        timeInForce: Default GTC
        status: Default OPEN
        comments: Default None
    """

    def __init__(
        self,
        pair: str,
        side: Literal["SELL", "BUY"],
        price: float,
        quantity: float,
        id_strategy: int,
        id_binance: int,
        **kwargs,
    ):
        super().__init__(
            pair=pair,
            side=side.upper(),
            type="LIMIT",
            id_strategy=id_strategy,
            id_binance=id_binance,
            id_competitors=kwargs.get("id_competitors"),
            newOrderRespType=kwargs.get("newOrderRespType", "FULL"),
            timeInForce=kwargs.get("timeInForce", "GTC"),
            status=kwargs.get("status", "OPEN"),
            comments=kwargs.get("comments", None),
        )
        self.price = price
        self.quantity = quantity
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.id_pasticoni = uuid.uuid4()


class MarketOrder(Order):
    """
    Market Order.

    Args:
        pair
        side
        id_strategy
        id_binance
        timestamp: Default now.
        quantity: the amount of the asset the user wants to buy or sell at the
                  market price. Excludes quoteOrderQty
        quoteOrderQty: the amount of the asset the user wants to spend/receive
                       the correct quantity will be determined based on the
                       market liquidity. Excludes quantity
        newOrderRespType: Default FULL
        timeInForce: Default GTC
        status: Default OPEN
        comments: Default None
        icb_delta: Iceberg's delta. Default None
        icb_tip: Iceberg's tip. Default None
    """

    def __init__(
        self,
        pair: str,
        side: Literal["SELL", "BUY"],
        id_strategy: int,
        id_binance: int,
        **kwargs,
    ):
        super().__init__(
            pair=pair,
            side=side.upper(),
            type="MARKET",
            id_strategy=id_strategy,
            id_binance=id_binance,
            id_competitors=kwargs.get("id_competitors"),
            newOrderRespType=kwargs.get("newOrderRespType", "FULL"),
            timeInForce=kwargs.get("timeInForce", "GTC"),
            status=kwargs.get("status", "OPEN"),
            comments=kwargs.get("comments", None),
        )
        self._xor_args_parser("quoteOrderQty", "quantity", **kwargs)
        self.icb_delta = kwargs.get("icb_delta")
        self.icb_tip = kwargs.get("icb_tip")
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.id_pasticoni = uuid.uuid4()
