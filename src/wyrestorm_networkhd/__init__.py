"""Wyrestorm NetworkHD Python Client Library.

A Python client library for WyreStorm NetworkHD devices, providing
a high-level interface for device control and monitoring.

For usage examples, see README.md and example.py files.
"""

# Version automatically managed by setuptools-scm
try:
    from ._version import __version__
except ImportError:
    # Development mode fallback
    __version__ = "dev"

# Main exports
from .commands import NHDAPI
from .core.client_ssh import NetworkHDClientSSH

__all__ = [
    "NetworkHDClientSSH",
    "NHDAPI",
    "__version__",
]
