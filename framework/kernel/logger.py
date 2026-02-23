import logging
from logging.handlers import RotatingFileHandler

from .config import get_config
from ..kernel.path import get_log_path


LOGGER_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}.get(get_config("LOGGER_LEVEL", "WARNING"), logging.WARNING)
LOG_FORMATTER = logging.Formatter(
    get_config("LOG_FORMAT", '[%(levelname)s] %(asctime)s [%(name)s<%(filename)s:%(lineno)d>] - %(message)s')
)

ENABLE_CONSOLELOG = get_config("ENABLE_CONSOLELOG", True)

ENABLE_FILELOG = get_config("ENABLE_FILELOG", False)
FILELOG_MAXBYTES = get_config("FILELOG_MAXBYTES", 3 * 1024 * 1024)
FILELOG_COUNT = get_config("FILELOG_COUNT", 5)


def set_handler(handler: logging.Handler) -> logging.Handler:
    handler.setFormatter(LOG_FORMATTER)
    handler.setLevel(LOGGER_LEVEL)
    return handler


def get_stream_handler(level: int | str | None = None) -> logging.Handler:
    stream_handler = set_handler(logging.StreamHandler())
    if level is None:
        return stream_handler

    try:
        stream_handler.setLevel(level)
    except ValueError:
        pass
    except TypeError:
        pass

    return stream_handler


def get_file_handler(name: str) -> logging.Handler:
    return set_handler(RotatingFileHandler(
        get_log_path(name) / "log.txt",
        maxBytes=FILELOG_MAXBYTES,
        backupCount=FILELOG_COUNT,
        encoding="utf-8",
        delay=True,
        mode="a",
    ))


def get_logger(name: str, console_level: int | str | None = None, force_filelog: bool = False) -> logging.Logger:
    """
    Get the logger of the unified configuration of the framework.
    :param name: logger name
    :param console_level: If this parameter is none, use the global configuration.
    :param force_filelog: If this parameter is true, the ENABLE_FILELOG will be ignored and the log will be forced to be saved to the file.
    :return: logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER_LEVEL)
    logger.propagate = False

    logger.handlers.clear()

    if ENABLE_CONSOLELOG:
        logger.addHandler(get_stream_handler(console_level))

    if force_filelog or ENABLE_FILELOG:
        logger.addHandler(get_file_handler(name))

    return logger


__all__ = [
    "get_logger",
]
