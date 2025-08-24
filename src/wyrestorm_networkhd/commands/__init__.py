"""Convenience wrapper for all command groups.

This module provides the NHDAPI class that organizes all NetworkHD API commands
into logical groups for easy access.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core._client import _BaseNetworkHDClient


class NHDAPI:
    """Typed wrapper for all NHD command groups.

    Provides organized access to all NetworkHD API commands, grouped by functionality.
    Each command group contains related commands for a specific domain.

    This class supports any NetworkHD client implementation, including SSH and RS232 clients.
    Future client implementations are automatically supported.

    Args:
        client: A NetworkHD client instance (NetworkHDClientSSH, NetworkHDClientRS232, etc.)

    Example:
        ```python
        from wyrestorm_networkhd import NetworkHDClientSSH, NHDAPI

        # Create a client
        client = NetworkHDClientSSH(
            host="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            ssh_host_key_policy="auto_add"
        )

        # Create API wrapper
        api = NHDAPI(client)

        # Use command groups
        await api.api_query.get_device_info()
        ```
    """

    def __init__(self, client: "_BaseNetworkHDClient"):
        # Import the base class for runtime validation
        from ..core._client import _BaseNetworkHDClient

        # Validate that the client type is supported
        if not isinstance(client, _BaseNetworkHDClient):
            raise TypeError(
                f"Client must be a NetworkHD client (like NetworkHDClientSSH or NetworkHDClientRS232), "
                f"got {type(client).__name__}"
            )

        # Store the client
        self.client = client

        # Dynamically discover and initialize all command groups
        self._initialize_command_groups(client)

    def _initialize_command_groups(self, client: "_BaseNetworkHDClient") -> None:
        """Dynamically discover and initialize all command group classes.

        This method automatically finds all command modules in the commands package
        and initializes their command classes, making NHDAPI automatically support
        any new command groups without code changes.

        Args:
            client: The NetworkHD client to pass to each command group
        """
        import importlib
        import inspect
        import pkgutil
        from pathlib import Path

        # Get the path to the commands package
        commands_path = Path(__file__).parent

        # Iterate through all modules in the commands package
        for _, name, _ in pkgutil.iter_modules([str(commands_path)]):
            # Skip private modules and __init__.py
            if name.startswith("_") or name == "__init__":
                continue

            try:
                # Import the module
                module = importlib.import_module(f".{name}", package=__name__)

                # Find command classes in the module (classes ending with 'Commands')
                for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        class_name.endswith("Commands")
                        and class_obj.__module__ == module.__name__
                        and hasattr(class_obj, "__init__")
                    ):
                        # Create attribute name from module name (snake_case)
                        attr_name = name

                        # Initialize the command group and add it as an attribute
                        command_instance = class_obj(client)
                        setattr(self, attr_name, command_instance)

            except ImportError:
                # Skip modules that can't be imported (missing dependencies, etc.)
                continue
