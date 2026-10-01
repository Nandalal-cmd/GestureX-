"""Logging configuration shared by GestureFX modules."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a concise console logger once for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
