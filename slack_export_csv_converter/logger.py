# -*- coding: utf-8 -*-
import logging


def setup_logger() -> None:
    """Sets up root logger of python standard library

    This function defines how to format and where to send the messages.
    After calling this function just use logging.debug() and the like to log messages.

    Args:

    Returns:
        None
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.INFO)
    logger.addHandler(stderr_handler)
