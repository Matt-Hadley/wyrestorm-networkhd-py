"""Wyrestorm NetworkHD Python Client Library.

A Python client library for WyreStorm NetworkHD devices, providing
a high-level interface for device control and monitoring.

For usage examples, see README.md.
"""

from typing import TYPE_CHECKING, Any

# Version automatically managed by setuptools-scm
try:
    from ._version import __version__
except ImportError:
    # Development mode fallback
    __version__ = "dev"

from .commands import NHDAPI
from .core.client_ssh import NetworkHDClientSSH, normalize_fingerprints
from .exceptions import (
    AuthenticationError,
    CommandError,
    ConnectionError,
    ConnectionLostError,
    DeviceNotFoundError,
    DeviceQueryError,
    HostKeyMismatchError,
    NetworkHDError,
    ReconnectionError,
    ResponseError,
    TimeoutError,
    UnknownCommandError,
)

if TYPE_CHECKING:
    from .core.client_rs232 import NetworkHDClientRS232


def __getattr__(name: str) -> Any:
    # RS232 needs the optional async-pyserial dependency (the "rs232" extra), so import it only when asked for.
    if name == "NetworkHDClientRS232":
        from .core.client_rs232 import NetworkHDClientRS232

        return NetworkHDClientRS232
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# NetworkHDClientRS232 is left out so that `import *` works without the rs232 extra.
__all__ = [
    "NHDAPI",
    "AuthenticationError",
    "CommandError",
    "ConnectionError",
    "ConnectionLostError",
    "DeviceNotFoundError",
    "DeviceQueryError",
    "HostKeyMismatchError",
    "NetworkHDClientSSH",
    "NetworkHDError",
    "ReconnectionError",
    "ResponseError",
    "TimeoutError",
    "UnknownCommandError",
    "__version__",
    "normalize_fingerprints",
]
