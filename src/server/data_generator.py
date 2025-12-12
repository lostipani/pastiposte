import random
import string
from typing import Any


def _format(data: Any):
    return {"response": data}


def gauss_list(size: int, mean: float = 0, std: float = 1):
    return _format([random.gauss(mean, std) for _ in range(size)])


def char_scalar():
    return _format(random.choice(string.ascii_letters))
