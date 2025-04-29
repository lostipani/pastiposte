import os
import logging

logging.basicConfig(
    format="%(message)s",
    level=os.getenv("LOGLEVEL", "INFO"),
)
logger = logging.getLogger("uvicorn.error")
