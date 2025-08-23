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
from .commands import NHDAPI
from .core.client import ConnectionType, HostKeyPolicy, NetworkHDClient

__all__ = [
    "NetworkHDClient",
    "HostKeyPolicy",
    "ConnectionType",
    "NHDAPI",
    "__version__",
]
