__version__ = "0.1.0"


import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from yimba_api.storage.db import BaseMongoModel, NosqlClient, PyObjectId  # noqa: F401

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "yimba-api.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(
    logger_name: str,
    level: str = "debug",
    file_handler: bool = False,
) -> logging.Logger:

    logger = logging.getLogger(logger_name)

    match level.lower():
        case "critical":
            logger.setLevel(logging.CRITICAL)
        case "error":
            logger.setLevel(logging.ERROR)
        case "warning":
            logger.setLevel(logging.WARNING)
        case "error":
            logger.setLevel(logging.ERROR)
        case "info":
            logger.setLevel(logging.INFO)
        case "debug":
            logger.setLevel(logging.DEBUG)
        case "notset":
            logger.setLevel(logging.NOTSET)
        case _:
            raise Exception(f"Invalid log level: {level}")

    logger.addHandler(get_console_handler())
    if file_handler:
        logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
