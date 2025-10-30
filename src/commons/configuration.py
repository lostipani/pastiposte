import os
import re
from collections import UserDict
from commons.logger import logger


class Singleton(type(UserDict)):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances.get(cls)


class Configuration(UserDict, metaclass=Singleton):
    def __init__(self):
        super().__init__(os.environ)
        self.unprefix_broker_params()
        self.cast_to_numeric()

    def unprefix_broker_params(self):
        """
        BROKER_FOO -> foo
        JOO -> joo
        """
        self.data = {
            (
                key.replace("BROKER_", "").lower()
                if "BROKER_" in key.upper()
                else key.lower()
            ): val
            for key, val in self.data.items()
        }

    def cast_to_numeric(self):
        """
        '4' -> 4.0
        '03.76' -> 3.76
        '.42' -> 0.42
        """
        for key, val in self.data.items():
            if re.match(r"^(\d*\.\d+)$|^(\d+)$", val):
                self.data[key] = float(val)
