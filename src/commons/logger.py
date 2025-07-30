import os
import logging

logging.basicConfig(
    format="%(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger("uvicorn.error")
