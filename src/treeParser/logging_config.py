"""
logging_config.py

Centralized logging configuration for the Nokia Classic CLI parser.
"""

from __future__ import annotations

import logging
from pathlib import Path


DEFAULT_FORMAT = (
    "%(asctime)s "
    "%(levelname)-8s "
    "%(name)s "
    "%(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    verbose: bool = False,
    log_file: Path | None = None,
) -> None:
    """
    Configure application logging.

    Parameters
    ----------
    verbose
        Enable DEBUG logging.

    log_file
        Optional log file.
    """

    level = logging.DEBUG if verbose else logging.INFO

    #
    # Remove existing handlers.
    #

    root = logging.getLogger()

    while root.handlers:
        root.removeHandler(root.handlers[0])

    formatter = logging.Formatter(
        fmt=DEFAULT_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )

    #
    # Console handler.
    #

    console = logging.StreamHandler()

    console.setLevel(level)

    console.setFormatter(formatter)

    root.addHandler(console)

    #
    # Optional file logging.
    #

    if log_file is not None:

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        file_handler.setLevel(level)

        file_handler.setFormatter(formatter)

        root.addHandler(file_handler)

    root.setLevel(level)