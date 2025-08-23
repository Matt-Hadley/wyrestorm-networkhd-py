"""NetworkHD client with inheritance-based architecture."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from ..logging_config import get_logger
from ..models.api_notifications import (
    NotificationObject,
    NotificationParser,
)


class _NotificationHandler:
    """Handles parsing and dispatching of NetworkHD API notifications."""

    def __init__(self):
        self._callbacks: dict[str, list[Callable[[NotificationObject], None]]] = {}
        self._parser = NotificationParser()
        self.logger = get_logger(f"{__name__}._NotificationHandler")

    def register_callback(self, notification_type: str, callback: Callable[[NotificationObject], None]) -> None:
        """Register a callback for a specific notification type."""
        if notification_type not in self._callbacks:
            self._callbacks[notification_type] = []
        self._callbacks[notification_type].append(callback)
        self.logger.debug(f"Registered callback for {notification_type} notifications")

    def unregister_callback(self, notification_type: str, callback: Callable[[NotificationObject], None]) -> None:
        """Unregister a specific callback for a notification type."""
        if notification_type in self._callbacks:
            try:
                self._callbacks[notification_type].remove(callback)
                if not self._callbacks[notification_type]:
                    del self._callbacks[notification_type]
                self.logger.debug(f"Unregistered callback for {notification_type} notifications")
            except ValueError:
                self.logger.warning(f"Callback not found for {notification_type} notifications")

    async def handle_notification(self, notification_line: str) -> None:
        """Parse and dispatch a notification to registered callbacks."""
        try:
            # Determine notification type directly from the notification string
            notification_type = self._parser.get_notification_type(notification_line)

            parsed_notification = self._parser.parse_notification(notification_line)
            if parsed_notification is None:
                self.logger.warning(f"Could not parse notification: {notification_line}")
                return

            # Call registered callbacks
            if notification_type in self._callbacks:
                for callback in self._callbacks[notification_type]:
                    try:
                        callback(parsed_notification)
                    except Exception as e:
                        self.logger.error(f"Error in notification callback: {e}")

            self.logger.debug(f"Processed {notification_type} notification: {parsed_notification}")

        except Exception as e:
            self.logger.error(f"Error handling notification '{notification_line}': {e}")


class _BaseNetworkHDClient(ABC):
    """Base NetworkHD client with common functionality.

    This is a private base class that provides notification handling
    and common client operations. Protocol-specific implementations
    inherit from this class.
    """

    def __init__(self):
        """Initialize base client with notification handler."""
        # Create notification handler (same for all protocols)
        self.notification_handler = _NotificationHandler()

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the NetworkHD device.

        Raises:
            ConnectionError: If the connection fails.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the NetworkHD device."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the device.

        Returns:
            True if connected, False otherwise.
        """
        pass

    @abstractmethod
    async def send_command(self, command: str, response_timeout: float | None = None) -> str:
        """Send a command to the device and get the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected to the device.
            CommandError: If the command fails or times out.
        """
        pass

    def register_notification_callback(
        self, notification_type: str, callback: Callable[[NotificationObject], None]
    ) -> None:
        """Register a callback function for specific notification types.

        Args:
            notification_type: Type of notification to listen for.
                Available types: 'endpoint', 'cec', 'infrared', 'rs232', 'video_input'
            callback: Function to call when this notification type is received.
                The callback will receive the parsed notification object as its argument.

        Example:
            ```python
            def handle_endpoint_status(notification):
                print(f"Endpoint {notification.device} is {'online' if notification.online else 'offline'}")

            client.register_notification_callback("endpoint", handle_endpoint_status)
            ```
        """
        self.notification_handler.register_callback(notification_type, callback)

    def unregister_notification_callback(
        self, notification_type: str, callback: Callable[[NotificationObject], None]
    ) -> None:
        """Remove a previously registered notification callback.

        Args:
            notification_type: Type of notification.
            callback: The callback function to remove.
        """
        self.notification_handler.unregister_callback(notification_type, callback)
