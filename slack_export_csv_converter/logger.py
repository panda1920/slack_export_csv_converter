# -*- coding: utf-8 -*-
import logging
from pathlib import Path


def setup_logger() -> None:
    """Sets up root logger of python standard library

    This function defines how to format and where to send the logs.
    After calling this function just use logging.debug() and the like throughout the code.

    Args:

    Returns:
        None
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    stderr_handler = logging.StreamHandler()
    stderr_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    stderr_handler.setFormatter(stderr_formatter)
    stderr_handler.setLevel(logging.INFO)
    logger.addHandler(stderr_handler)

    project_path = Path(__file__).resolve().parents[1]
    file_handler = logging.FileHandler(
        str(project_path / "slack_export_csv_converter.log"), encoding="utf-8"
    )
    file_formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
