"""NetworkHD API client exceptions.

This module defines custom exception classes for the NetworkHD API client.
These exceptions provide detailed error information and help with debugging.
"""


class NetworkHDError(Exception):
    """Base exception for NetworkHD API errors"""

    pass


class ConnectionError(NetworkHDError):
    """Exception raised when connection fails"""

    pass


class CommandError(NetworkHDError):
    """Exception raised when command execution fails"""

    pass


class ResponseError(NetworkHDError):
    """Exception raised when response parsing fails"""

    pass


class DeviceNotFoundError(NetworkHDError):
    """Exception raised when a device does not exist"""

    def __init__(self, device_name: str):
        self.device_name = device_name
        super().__init__(f'"{device_name} does not exist."')


class UnknownCommandError(NetworkHDError):
    """Exception raised when command is not recognized"""

    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Unknown command: {command}")


class DeviceQueryError(NetworkHDError):
    """Exception raised when device query returns error in JSON response"""

    def __init__(self, device_name: str, error_message: str):
        self.device_name = device_name
        self.error_message = error_message
        super().__init__(f"Device '{device_name}': {error_message}")
