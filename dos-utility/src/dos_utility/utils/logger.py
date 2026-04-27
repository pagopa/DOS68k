"""Shared logger utility for all services."""

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name (str): The name of the logger (typically __name__ of the calling module).
        level (int): The logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)

    return logger
