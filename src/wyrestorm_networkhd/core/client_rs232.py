"""RS232 client for NetworkHD devices with simplified architecture."""

import asyncio
import contextlib

import async_pyserial  # type: ignore[import-untyped]

from ..exceptions import ConnectionError
from ..logging_config import get_logger
from ._client import _BaseNetworkHDClient


class NetworkHDClientRS232(_BaseNetworkHDClient):
    """RS232 client for NetworkHD devices.

    Provides a simplified interface for connecting to NetworkHD devices via RS232,
    with automatic message dispatching and notification handling.
    """

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================

    def __init__(
        self,
        port: str,
        baudrate: int,
        timeout: float = 10.0,
        *,
        circuit_breaker_timeout: float = 30.0,
        heartbeat_interval: float = 30.0,
        message_dispatcher_interval: float = 0.05,
        **serial_kwargs,
    ):
        """Initialize RS232 client.

        Args:
            port: The serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM1' on Windows).
            baudrate: The baud rate for serial communication.
            timeout: Connection timeout in seconds (default: 10.0).
            circuit_breaker_timeout: Time in seconds after which the circuit breaker
                will automatically reset after being opened (default: 30.0).
            heartbeat_interval: Interval in seconds between heartbeat checks (default: 30.0).
            message_dispatcher_interval: Sleep interval in seconds for the message
                dispatcher loop to prevent busy waiting (default: 0.05).
            **serial_kwargs: Additional serial port configuration options.

        Raises:
            ValueError: If any parameters are invalid.
        """
        super().__init__(
            circuit_breaker_timeout=circuit_breaker_timeout,
            heartbeat_interval=heartbeat_interval,
        )

        # Validate parameters
        if not port:
            raise ValueError("Port is required")
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError("Baudrate must be a positive integer")
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if message_dispatcher_interval <= 0:
            raise ValueError("Message dispatcher interval must be positive")

        # Store connection parameters
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_kwargs = serial_kwargs
        self.message_dispatcher_interval = message_dispatcher_interval

        # Serial connection objects
        self.serial: async_pyserial.SerialPort | None = None

        # Message handling
        self._message_dispatcher_task: asyncio.Task | None = None
        self._dispatcher_enabled = False

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.NetworkHDClientRS232")

    # ============================================================================
    # PUBLIC METHODS - Connection Management
    # ============================================================================

    async def connect(self) -> None:
        """Establish RS232 connection to the NetworkHD device.

        Raises:
            ConnectionError: If the connection fails.
        """
        # Check circuit breaker
        if self._is_circuit_open():
            raise ConnectionError("Circuit breaker is open - connection attempts are blocked")

        try:
            self._set_connection_state("connecting")
            self.logger.info(f"Connecting to {self.port} at {self.baudrate} baud")

            # Implementation of abstract connect method

            # Create async serial connection
            self.serial = async_pyserial.SerialPort(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                **self.serial_kwargs,
            )

            # Open the connection
            await self.serial.open()

            # Start message dispatcher
            await self._start_message_dispatcher()

            self._set_connection_state("connected")
            self.logger.info(f"Successfully connected to {self.port}")

        except Exception as e:
            error_msg = f"Connection failed: {e}"
            self._set_connection_state("error", error_msg)
            raise ConnectionError(error_msg) from e

    async def disconnect(self) -> None:
        """Disconnect from the NetworkHD device.

        Closes the RS232 connection and stops the message dispatcher.
        """
        try:
            self.logger.info(f"Disconnecting from {self.port}")

            # Stop message dispatcher
            await self._stop_message_dispatcher()

            # Close serial connection
            if self.serial and self.serial.is_open:
                await self.serial.close()
                self.serial = None

            self._set_connection_state("disconnected")
            self.logger.info(f"Disconnected from {self.port}")

        except Exception as e:
            error_msg = f"Disconnect error: {e}"
            self._set_connection_state("error", error_msg)
            raise

    def is_connected(self) -> bool:
        """Check if connected to the device via RS232.

        Returns:
            True if connected, False otherwise.
        """
        connected = self.serial is not None and self.serial.is_open

        if not connected and self._connection_state == "connected":
            self._set_connection_state("disconnected")  # type: ignore[unreachable]

        return connected

    async def send_command(self, command: str, response_timeout: float = 10.0) -> str:
        """Send a command to the device via RS232 and get the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response in seconds.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected to the device.
            CommandError: If the command fails or times out.

        """
        if not self.is_connected():
            raise ConnectionError("Not connected")

        # Use the base class's generic command infrastructure
        def send_func(cmd: str) -> None:
            if not self.serial:
                raise ConnectionError("RS232 serial port not available")
            # Add carriage return and line feed for RS232
            message = cmd + "\r\n"
            asyncio.create_task(self.serial.write(message.encode()))
            self.logger.debug(f"Sending command via RS232: {cmd}")

        def receive_func() -> str | None:
            # This will be called by the message dispatcher
            return None

        response = await self._send_command_generic(command.strip(), send_func, receive_func, response_timeout)

        self.logger.debug(f"Raw response: {response}")
        return response

    # ============================================================================
    # PROTECTED METHODS - RS232 Implementation
    # ============================================================================

    async def _start_message_dispatcher(self) -> None:
        """Start the message dispatcher task.

        Creates an asyncio task to handle incoming RS232 messages and route them
        to either notification handlers or command response queues.
        """
        if self._dispatcher_enabled:
            return

        self._dispatcher_enabled = True
        self._message_dispatcher_task = asyncio.create_task(self._message_dispatcher())
        self.logger.debug("Message dispatcher started")

    async def _stop_message_dispatcher(self) -> None:
        """Stop the message dispatcher task.

        Cancels the dispatcher task and waits for it to complete cleanup.
        """
        if not self._dispatcher_enabled:
            return

        self._dispatcher_enabled = False
        if self._message_dispatcher_task:
            self._message_dispatcher_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._message_dispatcher_task
            self._message_dispatcher_task = None
        self.logger.debug("Message dispatcher stopped")

    async def _message_dispatcher(self) -> None:
        """Message dispatcher that separates notifications from command responses.

        Continuously reads from the RS232 port and routes incoming messages to
        either notification handlers or command response queues based on message
        content.
        """
        if not self.serial:
            return

        buffer = ""
        while self._dispatcher_enabled and self.is_connected():
            try:
                # Read data from serial port
                if self.serial.in_waiting > 0:
                    chunk = await self.serial.read(self.serial.in_waiting)
                    buffer += chunk.decode("utf-8", errors="ignore")

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip().rstrip("\r")

                        if not line:
                            continue

                        # Check if this is a notification
                        if line.startswith("notify "):
                            # This is a notification - handle it
                            await self.notification_handler.handle_notification(line)
                            # Record notification for metrics
                            self._record_notification_received()
                        else:
                            # This is likely a command response - send to oldest pending command
                            await self._handle_command_response(line)

                # Small delay to prevent busy waiting
                await asyncio.sleep(self.message_dispatcher_interval)

            except Exception as e:
                if self._dispatcher_enabled:
                    self.logger.error(f"Error in message dispatcher: {e}")
                break

        self.logger.debug("Message dispatcher stopped")

    async def _handle_command_response(self, response_line: str) -> None:
        """Send response line to the first available pending command.

        Args:
            response_line: The response line to route to a waiting command.
        """
        # Use the base class's pending commands
        if not self._pending_commands:
            # No commands waiting - this might be unsolicited output
            self.logger.debug(f"Received unsolicited output: {response_line}")
            return

        # Send to the first pending command (FIFO order)
        command_id = next(iter(self._pending_commands))
        queue = self._pending_commands[command_id]

        try:
            queue.put_nowait(response_line)
        except asyncio.QueueFull:
            self.logger.warning(f"Response queue full for command {command_id}")

    # ============================================================================
    # CONTEXT MANAGER METHODS
    # ============================================================================

    async def __aenter__(self):
        """Async context manager entry.

        Returns:
            Self after establishing connection.
        """
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Async context manager exit.

        Ensures proper cleanup of RS232 connection and message dispatcher.
        """
        await self.disconnect()
