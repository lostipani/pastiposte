import os
from typing import Dict
from commons.logger import logging


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances.get(cls)


class Configuration(object, metaclass=Singleton):
    def __init__(self):
        self.settings = os.environ
        self.unprefix_broker_params()

    def unprefix_broker_params(self):
        return {
            env.replace("BROKER_", "").lower(): self.settings[env]
            for env in self.settings
            if "BROKER_" in env.upper()
        }


def get_URL() -> str:
    try:
        return str(os.environ.get("URL", None))
    except KeyError:
        logging.error("missing URL")
        raise MissingParametersException


def get_sleep() -> float:
    try:
        return float(os.environ["SLEEP"])
    except KeyError:
        logging.error("missing SLEEP, in seconds")
        raise MissingParametersException


def get_rabbitmq_params() -> Dict[str, str]:
    try:
        return {
            env.replace("BROKER_", "").lower(): os.environ[env]
            for env in os.environ
            if "BROKER_" in env.upper()
        }
    except KeyError:
        logging.error("missing RabbitMQ parameter(s)")
        raise MissingParametersException
