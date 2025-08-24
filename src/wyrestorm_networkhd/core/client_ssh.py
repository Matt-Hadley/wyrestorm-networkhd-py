"""SSH client for NetworkHD devices with simplified architecture."""

import asyncio
import contextlib

import paramiko

from ..exceptions import AuthenticationError, ConnectionError
from ..logging_config import get_logger
from ._client import _BaseNetworkHDClient, _ConnectionState

# Type alias for SSH host key policies
HostKeyPolicy = str  # 'auto_add', 'reject', or 'warn'


class NetworkHDClientSSH(_BaseNetworkHDClient):
    """SSH client for NetworkHD devices.

    Provides a simplified interface for connecting to NetworkHD devices via SSH,
    with automatic message dispatching and notification handling.
    """

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        ssh_host_key_policy: HostKeyPolicy,
        timeout: float = 10.0,
        *,
        circuit_breaker_timeout: float = 30.0,
        heartbeat_interval: float = 30.0,
        message_dispatcher_interval: float = 0.1,
    ):
        """Initialize SSH client.

        Args:
            host: The hostname or IP address of the device.
            port: The SSH port number.
            username: The SSH username.
            password: The SSH password.
            ssh_host_key_policy: SSH host key verification policy.
                Must be one of: 'auto_add', 'reject', or 'warn'.
            timeout: Connection timeout in seconds (default: 10.0).
            circuit_breaker_timeout: Time in seconds after which the circuit breaker
                will automatically reset after being opened (default: 30.0).
            heartbeat_interval: Interval in seconds between heartbeat checks (default: 30.0).
            message_dispatcher_interval: Sleep interval in seconds for the message
                dispatcher loop to prevent busy waiting (default: 0.1).

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        super().__init__(
            circuit_breaker_timeout=circuit_breaker_timeout,
            heartbeat_interval=heartbeat_interval,
        )

        # Validate parameters
        if not host:
            raise ValueError("Host is required")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be an integer between 1 and 65535")
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if ssh_host_key_policy not in ("auto_add", "reject", "warn"):
            raise ValueError(
                f"Invalid ssh_host_key_policy: {ssh_host_key_policy}. Must be one of: auto_add, reject, warn"
            )
        if message_dispatcher_interval <= 0:
            raise ValueError("Message dispatcher interval must be positive")

        # Store connection parameters
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh_host_key_policy = ssh_host_key_policy
        self.message_dispatcher_interval = message_dispatcher_interval

        # SSH connection objects
        self.client: paramiko.SSHClient | None = None
        self.shell: paramiko.Channel | None = None

        # Message handling
        self._message_dispatcher_task: asyncio.Task | None = None
        self._dispatcher_enabled = False

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.NetworkHDClientSSH")

    # ============================================================================
    # PUBLIC METHODS - Connection Management
    # ============================================================================

    async def connect(self) -> None:
        """Establish SSH connection to the NetworkHD device.

        Raises:
            ConnectionError: If the connection fails.
            AuthenticationError: If authentication fails.
        """
        # Check circuit breaker
        if self._is_circuit_open():
            raise ConnectionError("Circuit breaker is open - connection attempts are blocked")

        try:
            self._set_connection_state("connecting")
            self.logger.info(f"Connecting to {self.host}:{self.port}")

            # Implementation of abstract connect method

            # Single connection mode
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(self._get_host_key_policy())

            # Connect to the device
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )

            # Open interactive shell
            self.shell = self.client.invoke_shell()
            self.shell.settimeout(self.timeout)

            # Start message dispatcher
            await self._start_message_dispatcher()

            self._set_connection_state("connected")
            self.logger.info(f"Successfully connected to {self.host}:{self.port}")

        except paramiko.AuthenticationException as e:
            error_msg = f"Authentication failed: {e}"
            self._set_connection_state("error", error_msg)
            raise AuthenticationError(self.username, self.host) from e
        except paramiko.SSHException as e:
            error_msg = f"SSH error: {e}"
            self._set_connection_state("error", error_msg)
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Connection failed: {e}"
            self._set_connection_state("error", error_msg)
            raise ConnectionError(error_msg) from e

    async def disconnect(self) -> None:
        """Disconnect from the NetworkHD device.

        Closes the SSH connection and stops the message dispatcher.
        """
        try:
            self.logger.info(f"Disconnecting from {self.host}:{self.port}")

            # Stop message dispatcher
            await self._stop_message_dispatcher()

            # Close SSH connection
            if self.shell:
                self.shell.close()
                self.shell = None

            if self.client:
                self.client.close()
                self.client = None

            self._set_connection_state("disconnected")
            self.logger.info(f"Disconnected from {self.host}:{self.port}")

        except Exception as e:
            error_msg = f"Disconnect error: {e}"
            self._set_connection_state("error", error_msg)
            raise

    def is_connected(self) -> bool:
        """Check if connected to the device via SSH.

        Returns:
            True if connected, False otherwise.
        """
        connected = (
            self.client is not None
            and self.shell is not None
            and not self.shell.closed
            and self.client.get_transport() is not None
            and self.client.get_transport().is_active()
        )

        if not connected and self._connection_state == _ConnectionState.CONNECTED:
            self._set_connection_state("disconnected")

        return connected

    async def send_command(self, command: str, response_timeout: float = 10.0) -> str:
        """Send a command to the device via SSH and get the response.

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
            if not self.shell:
                raise ConnectionError("SSH shell not available")
            self.shell.send(cmd + "\n")
            self.logger.debug(f"Sending command via SSH: {cmd}")

        def receive_func() -> str | None:
            # This will be called by the message dispatcher
            return None

        response = await self._send_command_generic(command.strip(), send_func, receive_func, response_timeout)

        self.logger.debug(f"Raw response: {response}")
        return response

    # ============================================================================
    # PROTECTED METHODS - SSH Implementation
    # ============================================================================

    def _get_host_key_policy(
        self,
    ) -> paramiko.client.AutoAddPolicy | paramiko.client.RejectPolicy | paramiko.client.WarningPolicy:
        """Get the appropriate Paramiko host key policy.

        Returns:
            Paramiko host key policy object based on ssh_host_key_policy setting.
        """
        policy_map = {
            "auto_add": paramiko.AutoAddPolicy(),
            "reject": paramiko.RejectPolicy(),
            "warn": paramiko.WarningPolicy(),
        }
        return policy_map[self.ssh_host_key_policy]

    async def _start_message_dispatcher(self) -> None:
        """Start the message dispatcher task.

        Creates an asyncio task to handle incoming SSH messages and route them
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

        Continuously reads from the SSH shell and routes incoming messages to
        either notification handlers or command response queues based on message
        content.
        """
        if not self.shell:
            return

        buffer = ""
        while self._dispatcher_enabled and self.is_connected():
            try:
                # Read data from SSH shell
                if self.shell.recv_ready():
                    chunk = self.shell.recv(1024).decode("utf-8", errors="ignore")
                    buffer += chunk

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if not line:
                            continue

                        # Debug: log what we're receiving
                        self.logger.debug(f"Message dispatcher received line: {repr(line)}")

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

        self.logger.debug(f"Routing response '{response_line}' to command {command_id}")

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

        Ensures proper cleanup of SSH connection and message dispatcher.
        """
        await self.disconnect()
