"""NetworkHD API client exceptions.

This module defines custom exception classes for the NetworkHD API client.
These exceptions provide detailed error information and help with debugging.

``ConnectionError`` and ``TimeoutError`` shadow the builtins of the same name but also subclass them, so
``except builtins.ConnectionError`` / ``except builtins.TimeoutError`` still catch them.
"""

import builtins


class NetworkHDError(Exception):
    """Base exception for NetworkHD API errors"""

    pass


# ============================================================================
# CONNECTION-RELATED EXCEPTIONS
# ============================================================================


class ConnectionError(NetworkHDError, builtins.ConnectionError):
    """Exception raised when connection fails or the client is not connected"""

    pass


class ConnectionLostError(ConnectionError):
    """Exception raised when connection is unexpectedly lost"""

    def __init__(self, host: str, reason: str | None = None):
        self.host = host
        self.reason = reason
        message = f"Connection to '{host}' was lost"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class ReconnectionError(ConnectionError):
    """Exception raised when reconnection attempts fail"""

    def __init__(self, host: str, attempts: int, last_error: str):
        self.host = host
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Failed to reconnect to '{host}' after {attempts} attempts. Last error: {last_error}")


class AuthenticationError(NetworkHDError):
    """Exception raised when authentication fails"""

    def __init__(self, username: str, host: str):
        self.username = username
        self.host = host
        super().__init__(f"Authentication failed for user '{username}' on '{host}'")


class TimeoutError(NetworkHDError, builtins.TimeoutError):
    """Exception raised when operations timeout, e.g. no response to a command"""

    def __init__(self, operation: str, timeout: float):
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"Operation '{operation}' timed out after {timeout}s")


# ============================================================================
# COMMAND AND RESPONSE EXCEPTIONS
# ============================================================================


class CommandError(NetworkHDError):
    """Exception raised when command execution fails"""

    pass


class ResponseError(NetworkHDError, ValueError):
    """Exception raised when response parsing fails"""

    pass


class UnknownCommandError(CommandError):
    """Exception raised when the device answers "unknown command" (unknown command or incorrect parameters)"""

    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Unknown command: {command}")


# ============================================================================
# DEVICE-RELATED EXCEPTIONS
# ============================================================================


class DeviceNotFoundError(NetworkHDError):
    """Exception raised when a device does not exist"""

    def __init__(self, device_name: str):
        self.device_name = device_name
        super().__init__(f'"{device_name} does not exist."')


class DeviceQueryError(NetworkHDError):
    """Exception raised when device query returns error in JSON response"""

    def __init__(self, device_name: str, error_message: str):
        self.device_name = device_name
        self.error_message = error_message
        super().__init__(f"Device '{device_name}': {error_message}")
