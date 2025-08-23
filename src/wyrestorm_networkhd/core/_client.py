"""NetworkHD client with inheritance-based architecture."""

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any

from ..logging_config import get_logger
from ..models.api_notifications import (
    NotificationObject,
    NotificationParser,
)


class _ConnectionState(Enum):
    """Connection state enumeration (private)."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class _NotificationHandler:
    """Handles parsing and dispatching of NetworkHD API notifications."""

    def __init__(self):
        """Initialize notification handler with parser and callbacks."""
        self._callbacks: dict[str, list[Callable[[NotificationObject], None]]] = {}
        self._parser = NotificationParser()
        self.logger = get_logger(f"{__name__}._NotificationHandler")

    def register_callback(self, notification_type: str, callback: Callable[[NotificationObject], None]) -> None:
        """Register a callback for a specific notification type.

        Args:
            notification_type: Type of notification to listen for.
            callback: Function to call when this notification type is received.
        """
        if notification_type not in self._callbacks:
            self._callbacks[notification_type] = []
        self._callbacks[notification_type].append(callback)
        self.logger.debug(f"Registered callback for {notification_type} notifications")

    def unregister_callback(self, notification_type: str, callback: Callable[[NotificationObject], None]) -> None:
        """Unregister a specific callback for a notification type.

        Args:
            notification_type: Type of notification.
            callback: The callback function to remove.
        """
        if notification_type in self._callbacks:
            try:
                self._callbacks[notification_type].remove(callback)
                if not self._callbacks[notification_type]:
                    del self._callbacks[notification_type]
                self.logger.debug(f"Unregistered callback for {notification_type} notifications")
            except ValueError:
                self.logger.warning(f"Callback not found for {notification_type} notifications")

    async def handle_notification(self, notification_line: str) -> None:
        """Parse and dispatch a notification to registered callbacks.

        Args:
            notification_line: Raw notification string from the device.
        """
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

    def __init__(
        self,
        *,
        circuit_breaker_timeout: float,
        heartbeat_interval: float,
    ):
        """Initialize base client with notification handler and state management.

        Args:
            circuit_breaker_timeout: Time in seconds after which the circuit breaker
                will automatically reset after being opened.
            heartbeat_interval: Interval in seconds between heartbeat checks.

        Raises:
            ValueError: If any parameters are invalid.
        """
        # Validate parameters
        if circuit_breaker_timeout <= 0:
            raise ValueError("Circuit breaker timeout must be positive")
        if heartbeat_interval <= 0:
            raise ValueError("Heartbeat interval must be positive")
        # Create notification handler (same for all protocols)
        self.notification_handler = _NotificationHandler()

        # Connection state management
        self._connection_state = _ConnectionState.DISCONNECTED
        self._connection_error: str | None = None
        self._last_connection_attempt: float | None = None

        # Circuit breaker for connection failures (configurable timeout)
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._circuit_open = False
        self._circuit_open_time: float | None = None
        self._circuit_breaker_timeout = circuit_breaker_timeout

        # Command response handling (generic)
        self._pending_commands: dict[str, asyncio.Queue] = {}
        self._command_lock = asyncio.Lock()
        self._command_id_counter = 0

        # Connection health monitoring (generic, configurable interval)
        self._last_heartbeat: float | None = None
        self._heartbeat_interval: float = heartbeat_interval
        self._connection_metrics: dict[str, Any] = {
            "commands_sent": 0,
            "commands_failed": 0,
            "notifications_received": 0,
            "last_command_time": None,
        }

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    # ============================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ============================================================================

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
    async def send_command(self, command: str, response_timeout: float) -> str:
        """Send a command to the device and get the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response in seconds.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected to the device.
            CommandError: If the command fails or times out.
        """
        pass

    # ============================================================================
    # PUBLIC METHODS - Configuration and Status
    # ============================================================================

    def get_connection_state(self) -> str:
        """Get the current connection state as a string.

        Returns:
            Current connection state: 'disconnected', 'connecting', 'connected', 'error', or 'reconnecting'.
        """
        return self._connection_state.value

    def get_connection_error(self) -> str | None:
        """Get the last connection error message.

        Returns:
            Last error message or None if no error occurred.
        """
        return self._connection_error

    def get_connection_metrics(self) -> dict:
        """Get connection health metrics.

        Returns:
            Dictionary containing connection metrics:
            - commands_sent: Number of commands sent
            - commands_failed: Number of commands that failed
            - notifications_received: Number of notifications received
            - last_command_time: Timestamp of last command
        """
        return self._connection_metrics.copy()

    def register_notification_callback(
        self, notification_type: str, callback: Callable[[NotificationObject], None]
    ) -> None:
        """Register a callback function for specific notification types.

        Args:
            notification_type: Type of notification to listen for.
                Available types: 'endpoint', 'cecinfo', 'irinfo', 'serialinfo', 'video', 'sink'
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

    # ============================================================================
    # PUBLIC METHODS - Connection Management
    # ============================================================================

    async def reconnect(self, max_attempts: int, delay: float) -> None:
        """Attempt to reconnect to the device with exponential backoff.

        Args:
            max_attempts: Maximum number of reconnection attempts.
            delay: Initial delay between attempts in seconds.

        Raises:
            ConnectionError: If reconnection fails after max attempts.
        """
        if self._connection_state == _ConnectionState.CONNECTING:
            self.logger.warning("Already attempting to connect")
            return

        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Reconnection attempt {attempt + 1}/{max_attempts}")
                self._set_connection_state("reconnecting")

                # Wait before retry (exponential backoff)
                if attempt > 0:
                    wait_time = delay * (2 ** (attempt - 1))
                    self.logger.info(f"Waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)

                await self.connect()
                self.logger.info("Reconnection successful")
                return

            except Exception as e:
                error_msg = f"Reconnection attempt {attempt + 1} failed: {e}"
                self._set_connection_state("error", error_msg)
                self.logger.warning(error_msg)

                if attempt == max_attempts - 1:
                    raise ConnectionError(f"Failed to reconnect after {max_attempts} attempts: {e}") from e

    # ============================================================================
    # PROTECTED METHODS - Command Handling
    # ============================================================================

    async def _send_command_generic(
        self,
        command: str,
        send_func: Callable[[str], None],
        receive_func: Callable[[], str | None],  # noqa: ARG002
        response_timeout: float,
    ) -> str:
        """Generic command sending with response handling.

        Args:
            command: The command string to send.
            send_func: Protocol-specific function to send the command.
            receive_func: Protocol-specific function to receive response.
            response_timeout: Maximum time to wait for response.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected.
            TimeoutError: If response times out.
        """
        async with self._command_lock:
            command_id = str(self._command_id_counter)
            self._command_id_counter += 1
            response_queue: asyncio.Queue[str] = asyncio.Queue()

            try:
                self._pending_commands[command_id] = response_queue
                send_func(command)
                self._record_command_sent()

                # Collect all response lines until timeout
                response_lines = []
                start_time = asyncio.get_event_loop().time()

                while asyncio.get_event_loop().time() - start_time < response_timeout:
                    try:
                        # Wait for next response line
                        line = await asyncio.wait_for(response_queue.get(), timeout=1.0)
                        response_lines.append(line)
                    except TimeoutError:
                        # No more lines coming
                        break

                # Join all response lines
                return "\n".join(response_lines) if response_lines else ""
            except Exception:  # noqa: B904
                self._record_command_failed()
                raise
            finally:
                self._pending_commands.pop(command_id, None)

    def _parse_response(self, response: str) -> str:
        """Generic response parsing for NetworkHD devices.

        Args:
            response: The raw response string from the device.

        Returns:
            The parsed response string.

        Raises:
            CommandError: If the response indicates an error.
        """
        from ..exceptions import CommandError

        # Remove welcome message and strip whitespace
        response = response.replace("Welcome to NetworkHD", "").strip()

        # Check for error responses
        if response.startswith("ERROR"):
            raise CommandError(f"Command error: {response}")

        return response

    # ============================================================================
    # PROTECTED METHODS - Metrics and State Management
    # ============================================================================

    def _record_command_sent(self) -> None:
        """Record that a command was sent."""
        self._connection_metrics["commands_sent"] += 1
        self._connection_metrics["last_command_time"] = time.time()

    def _record_command_failed(self) -> None:
        """Record that a command failed."""
        self._connection_metrics["commands_failed"] += 1

    def _record_notification_received(self) -> None:
        """Record that a notification was received."""
        self._connection_metrics["notifications_received"] += 1

    def _set_connection_state(self, state: str, error: str | None = None) -> None:
        """Update connection state and error information.

        Args:
            state: New connection state string.
            error: Optional error message.
        """
        old_state = self._connection_state

        # Convert string state to enum value using the enum's value lookup
        try:
            self._connection_state = _ConnectionState(state)
        except ValueError:
            self.logger.warning(f"Unknown connection state: {state}")
            self._connection_state = _ConnectionState.ERROR

        self._connection_error = error

        if self._connection_state != old_state:
            self.logger.info(f"Connection state changed: {old_state.value} -> {self._connection_state.value}")
            if error:
                self.logger.error(f"Connection error: {error}")

        # Update circuit breaker state
        if self._connection_state == _ConnectionState.ERROR:
            self._record_failure()
        elif self._connection_state == _ConnectionState.CONNECTED:
            self._reset_circuit()

    # ============================================================================
    # PROTECTED METHODS - Circuit Breaker Logic
    # ============================================================================

    def _record_failure(self) -> None:
        """Record a connection failure for circuit breaker logic."""
        current_time = time.time()

        self._failure_count += 1
        self._last_failure_time = current_time

        # Open circuit after 3 consecutive failures
        if self._failure_count >= 3:
            self._circuit_open = True
            self._circuit_open_time = current_time
            self.logger.warning("Circuit breaker opened due to repeated failures")

    def _reset_circuit(self) -> None:
        """Reset circuit breaker after successful connection."""
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_open_time = None
        self.logger.info("Circuit breaker reset after successful connection")

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open.

        Returns:
            True if circuit breaker is open, False otherwise.
        """
        if not self._circuit_open:
            return False

        # Auto-close circuit after configured timeout
        import time

        if self._circuit_open_time and (time.time() - self._circuit_open_time) > self._circuit_breaker_timeout:
            self.logger.info("Circuit breaker auto-closing after timeout")
            self._circuit_open = False
            self._failure_count = 0
            return False

        return True

    def __del__(self):
        """Destructor to ensure message dispatcher task is cleaned up."""
        if (
            hasattr(self, "_message_dispatcher_task")
            and self._message_dispatcher_task
            and not self._message_dispatcher_task.done()
        ):
            # If there's still a running task, cancel it
            self._message_dispatcher_task.cancel()
