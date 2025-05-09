import os
from typing import Dict
from .logger import logging


def get_URI() -> str:
    if uri := os.environ.get("WS_URL", None):
        return str(uri)
    elif uri := os.environ.get("HTTP_URL", None):
        return str(uri)
    else:
        logging.error("missing URL to server")
        raise KeyError


def get_period() -> float:
    try:
        return float(os.environ["PERIOD"])
    except KeyError:
        logging.error("missing period, in seconds")
        raise


def get_rabbitmq_params() -> Dict[str, str]:
    try:
        return {
            env.replace("BROKER_", "").lower(): os.environ[env]
            for env in os.environ
            if "BROKER_" in env.upper()
        }
    except KeyError:
        logging.error("missing RabbitMQ parameter(s)")
        raise
