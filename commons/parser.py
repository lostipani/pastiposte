import os
from typing import Any, Dict
from .logger import logging


def get_URI() -> str:
    if uri := os.environ.get("WS_URL", None):
        return str(uri)
    elif uri := os.environ.get("HTTP_URL", None):
        return str(uri)
    else:
        logging.error("missing URL to server")
        raise KeyError


def get_server_period() -> float:
    try:
        return float(os.environ["SERVER_PERIOD"])
    except KeyError:
        logging.error("missing server production period, in seconds")
        raise


def get_listener_period() -> float:
    try:
        return float(os.environ["LISTENER_PERIOD"])
    except KeyError:
        logging.error("missing client's listener period, in seconds")
        raise


def get_fetcher_period() -> float:
    try:
        return float(os.environ["FETCHER_PERIOD"])
    except KeyError:
        logging.error("missing client's fetcher period, in seconds")
        raise


def get_consumer_period() -> float:
    try:
        return float(os.environ["CONSUMER_PERIOD"])
    except KeyError:
        logging.error("missing client's consumer period, in seconds")
        raise


def get_broker_params() -> Dict[str, Any]:
    try:
        return {"host": (os.environ["BROKER_HOST"])}
    except KeyError:
        logging.error("missing broker's hostname")
        raise
