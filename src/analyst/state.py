from dataclasses import dataclass, field
from typing import Dict, Optional
import math


@dataclass
class RollStats:
    n: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def update(self, x: float):
        self.n += 1
        d = x - self.mean
        self.mean += d / self.n
        self.m2 += d * (x - self.mean)

    @property
    def std(self) -> float:
        return math.sqrt(self.m2 / self.n) if self.n > 1 else 0.0


@dataclass
class PairState:
    stats: RollStats = field(default_factory=RollStats)
    last: float = 0.0
    open_order_id: Optional[str] = None
    position_qty: float = 0.0
    trailing_stop: Optional[float] = None


class StrategyState:
    def __init__(self):
        self.pairs: Dict[str, PairState] = {}

    def ps(self, pair: str) -> PairState:
        if pair not in self.pairs:
            self.pairs[pair] = PairState()
        return self.pairs[pair]
