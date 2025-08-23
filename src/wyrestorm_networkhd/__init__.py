"""Wyrestorm NetworkHD Python Client Library.

A Python client library for WyreStorm NetworkHD devices, providing
a high-level interface for device control and monitoring.

For usage examples, see README.md.
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

# RS232 client (optional - requires async-pyserial)
try:
    from .core.client_rs232 import NetworkHDClientRS232

    _RS232_AVAILABLE = True
except ImportError:
    _RS232_AVAILABLE = False

__all__ = [
    "NetworkHDClientSSH",
    "NHDAPI",
    "__version__",
]

# Conditionally export RS232 client if available
if _RS232_AVAILABLE:
    __all__.append("NetworkHDClientRS232")
