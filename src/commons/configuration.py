import os
from typing import Dict
from commons.logger import logging


class MissingParametersException(Exception):
    pass


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
