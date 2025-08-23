"""NetworkHD API client logging configuration.

This module provides logging configuration for the NetworkHD API client.
Logging is automatically configured when the client is used, but can be customized
for different environments and requirements.

Features:
- Automatic logging setup with sensible defaults
- Configurable log levels and formats
- File and console logging support
- Environment variable configuration
- Structured logging for better debugging

Default behavior:
- Log level: INFO
- Output: Console
- Format: Standard Python logging format
- Automatic setup when client is imported

For usage examples, see README.md.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """Set up logging configuration for the package.

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

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("paramiko").setLevel(logging.WARNING)  # Reduce paramiko noise
    logging.getLogger("asyncio").setLevel(logging.WARNING)  # Reduce asyncio noise


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Default logging setup
setup_logging()
