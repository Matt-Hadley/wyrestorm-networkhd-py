"""WyreStorm NetworkHD API Client

A Python client library for interacting with WyreStorm NetworkHD API operations.
"""

# Version automatically managed by setuptools-scm
try:
    from ._version import __version__
except ImportError:
    # Development mode fallback
    __version__ = "dev"

# Main exports
from .client import ConnectionType, HostKeyPolicy, NetworkHDClient
from .commands import NHDAPI

__all__ = [
    "NetworkHDClient",
    "ConnectionType",
    "HostKeyPolicy",
    "NHDAPI",
    "__version__",
]
