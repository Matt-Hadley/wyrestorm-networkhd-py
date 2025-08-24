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


# Dynamically discover and import all client classes
def _discover_and_import_clients():
    """Dynamically discover all client classes in the core module.

    Returns:
        dict: Mapping of client class names to their classes
    """
    import importlib
    import inspect
    import pkgutil
    from pathlib import Path

    clients = {}

    # Get the path to the core package
    core_path = Path(__file__).parent / "core"

    # Iterate through all modules in the core package
    for _, name, _ in pkgutil.iter_modules([str(core_path)]):
        if name.startswith("client_"):  # Only look at client modules
            try:
                # Import the module
                module_name = f".core.{name}"
                module = importlib.import_module(module_name, package=__name__)

                # Find all classes in the module that are client classes
                for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                    if class_name.startswith("NetworkHDClient") and class_obj.__module__ == module.__name__:
                        clients[class_name] = class_obj

            except ImportError:
                # Skip modules with missing dependencies
                continue

    return clients


# Discover and import all available clients
_DISCOVERED_CLIENTS = _discover_and_import_clients()

# Add discovered clients to module namespace
for client_name, client_class in _DISCOVERED_CLIENTS.items():
    globals()[client_name] = client_class

# Build __all__ list dynamically
__all__ = [
    "NHDAPI",
    "__version__",
] + list(_DISCOVERED_CLIENTS.keys())
