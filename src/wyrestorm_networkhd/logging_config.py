"""NetworkHD API client logging configuration.

The library logs under the ``wyrestorm_networkhd`` logger and, like any library, leaves configuring
logging to the application: importing the package adds only a ``NullHandler``. ``setup_logging()`` is an
opt-in helper for scripts and development that attaches console/file handlers to the package logger.

For usage examples, see README.md.
"""

import logging
import sys
from pathlib import Path

_PACKAGE_LOGGER = "wyrestorm_networkhd"

logging.getLogger(_PACKAGE_LOGGER).addHandler(logging.NullHandler())


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """Attach console (and optionally file) handlers to the ``wyrestorm_networkhd`` logger.

    Calling it again replaces the handlers already on that logger (other than the ``NullHandler``), so it can be
    called more than once. The root logger and its handlers are left alone.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console
        log_format: Format string for log messages
        date_format: Format string for timestamps
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Configure the package logger only; replace handlers from a previous call to avoid duplicates
    package_logger = logging.getLogger(_PACKAGE_LOGGER)
    package_logger.setLevel(numeric_level)
    for handler in package_logger.handlers[:]:
        if not isinstance(handler, logging.NullHandler):
            package_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    package_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        package_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
