"""SSH connection with unified message dispatcher for NetworkHD devices."""

import asyncio
import contextlib
import uuid
from enum import Enum

import paramiko

from ..exceptions import CommandError, ConnectionError
from ..logging_config import get_logger
from ._client import _BaseNetworkHDClient, _NotificationHandler


class _HostKeyPolicy(Enum):
    """SSH host key verification policies."""

    AUTO_ADD = "auto_add"  # paramiko.AutoAddPolicy()
    REJECT = "reject"  # paramiko.RejectPolicy()
    WARN = "warn"  # paramiko.WarningPolicy()


class _SSHConnection:
    """SSH connection to NetworkHD device with unified message dispatcher.

    Automatically separates notifications from command responses to prevent interference.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: float,
        host_key_policy: _HostKeyPolicy,
        notification_handler: _NotificationHandler,
    ):
        """Initialize an SSH connection instance.

        Args:
            host: The hostname or IP address of the device.
            port: The SSH port number.
            username: The SSH username.
            password: The SSH password.
            timeout: Connection timeout in seconds.
            host_key_policy: SSH host key verification policy.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.host_key_policy = host_key_policy
        self.client: paramiko.SSHClient | None = None
        self.shell: paramiko.Channel | None = None

        # Message handling
        self.notification_handler = notification_handler
        self._message_dispatcher_task: asyncio.Task | None = None
        self._dispatcher_enabled: bool = False

        # Command response handling
        self._pending_commands: dict[str, asyncio.Queue] = {}
        self._command_lock = asyncio.Lock()

        # Set up logger for this connection instance
        self.logger = get_logger(f"{__name__}._SSHConnection")

    def _get_host_key_policy(
        self,
    ) -> paramiko.client.AutoAddPolicy | paramiko.client.RejectPolicy | paramiko.client.WarningPolicy:
        """Get the appropriate Paramiko host key policy."""
        policy_map = {
            _HostKeyPolicy.AUTO_ADD: paramiko.AutoAddPolicy(),
            _HostKeyPolicy.REJECT: paramiko.RejectPolicy(),
            _HostKeyPolicy.WARN: paramiko.WarningPolicy(),
        }
        return policy_map[self.host_key_policy]

    async def connect(self) -> None:
        """Establish an SSH connection and open a shell.

        Raises:
            ConnectionError: If the SSH connection fails.
        """
        try:
            self.logger.debug(f"Initializing SSH client for {self.host}:{self.port}")
            self.client = paramiko.SSHClient()

            # Apply the configured host key policy
            host_key_policy = self._get_host_key_policy()
            self.client.set_missing_host_key_policy(host_key_policy)

            # Log the policy being used (for security auditing)
            if self.host_key_policy == _HostKeyPolicy.AUTO_ADD:
                self.logger.warning(
                    f"Using AutoAddPolicy for {self.host} - this automatically trusts unknown host keys. "
                    "Consider using a more restrictive policy in production environments."
                )

            self.logger.debug(f"Connecting to {self.host}:{self.port} as {self.username}")
            self.client.connect(
                self.host, port=self.port, username=self.username, password=self.password, timeout=self.timeout
            )
            self.logger.debug("SSH connection established, opening shell")
            self.shell = self.client.invoke_shell()
            await asyncio.sleep(0.1)  # allow shell to be ready

            # Start the message dispatcher automatically
            await self._start_message_dispatcher()
            self.logger.debug("SSH shell ready with message dispatcher running")
        except Exception as e:
            self.logger.error(f"SSH connection failed: {e}")
            raise ConnectionError(f"Failed to connect via SSH: {e}") from e

    async def disconnect(self) -> None:
        """Close the SSH shell and client connection."""
        # Stop message dispatcher first
        await self._stop_message_dispatcher()

        if self.shell:
            self.logger.debug("Closing SSH shell")
            self.shell.close()
            self.shell = None
        if self.client:
            self.logger.debug("Closing SSH client")
            self.client.close()
            self.client = None

    async def send_command(self, command: str, response_timeout: float | None = None) -> str:
        """Send a command to the SSH shell and retrieve the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response data (in seconds).
                Defaults to 10 seconds if None.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected.
            CommandError: If sending the command or receiving response fails.
        """
        if not self.client or not self.shell:
            raise ConnectionError("Not connected")

        if response_timeout is None:
            response_timeout = 10.0  # Default timeout

        async with self._command_lock:
            command_id = str(uuid.uuid4())
            response_queue: asyncio.Queue = asyncio.Queue()

            try:
                # Register this command to receive responses
                self._pending_commands[command_id] = response_queue

                self.logger.debug(f"Sending command via SSH: {command}")
                self.shell.send(command + "\\n")

                # Wait for the response with timeout
                try:
                    response = await asyncio.wait_for(response_queue.get(), timeout=response_timeout)
                    self.logger.debug(f"Received response via SSH (length: {len(response)})")
                    return response
                except TimeoutError:
                    raise CommandError(f"Command timed out after {response_timeout} seconds") from None

            finally:
                # Always clean up the pending command
                self._pending_commands.pop(command_id, None)

    def is_connected(self) -> bool:
        """Check if the SSH client and shell are connected.

        Returns:
            True if connected, False otherwise.
        """
        return self.client is not None and self.client.get_transport() is not None and self.shell is not None

    async def _start_message_dispatcher(self) -> None:
        """Start the unified message dispatcher that handles both commands and notifications."""
        if self._message_dispatcher_task is not None:
            self.logger.warning("Message dispatcher already running")
            return

        self._dispatcher_enabled = True
        self._message_dispatcher_task = asyncio.create_task(self._message_dispatcher())
        self.logger.info("Started message dispatcher")

    async def _stop_message_dispatcher(self) -> None:
        """Stop the message dispatcher."""
        if self._message_dispatcher_task is None:
            return

        self._dispatcher_enabled = False
        if not self._message_dispatcher_task.done():
            self._message_dispatcher_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._message_dispatcher_task

        self._message_dispatcher_task = None
        self.logger.info("Stopped message dispatcher")

    async def _message_dispatcher(self) -> None:
        """Unified message dispatcher that separates notifications from command responses."""
        buffer = ""

        while self._dispatcher_enabled and self.is_connected():
            try:
                if self.shell and self.shell.recv_ready():
                    # Read available data
                    data = self.shell.recv(1024).decode("utf-8", errors="ignore")
                    buffer += data

                    # Process complete lines
                    while "\\n" in buffer:
                        line, buffer = buffer.split("\\n", 1)
                        line = line.strip()

                        if not line:  # Skip empty lines
                            continue

                        if line.startswith("notify "):
                            # This is a notification - handle it
                            await self.notification_handler.handle_notification(line)
                        else:
                            # This is likely a command response - send to oldest pending command
                            await self._handle_command_response(line)

                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.05)

            except Exception as e:
                self.logger.error(f"Error in message dispatcher: {e}")
                await asyncio.sleep(1)

    async def _handle_command_response(self, response_line: str) -> None:
        """Send response line to the first available pending command."""
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


class NetworkHDClientSSH(_BaseNetworkHDClient):
    """NetworkHD SSH client with notification support.

    Provides SSH connection to NetworkHD devices with full notification handling.




    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        ssh_host_key_policy: str,
        port: int = 22,
        timeout: float = 10.0,
    ):
        """Initialize SSH NetworkHD client.

        Args:
            host: The hostname or IP address of the NetworkHD device.
            username: The SSH username.
            password: The SSH password.
            ssh_host_key_policy: SSH host key verification policy.
                Options: "auto_add", "reject", "warn".
                This parameter is required to ensure explicit security policy selection.
            port: The SSH port number (default: 22).
            timeout: Connection timeout in seconds (default: 10.0).

        Raises:
            ValueError: If required parameters are missing.
        """
        super().__init__()

        if not host:
            raise ValueError("Host is required")
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if not ssh_host_key_policy:
            raise ValueError("ssh_host_key_policy is required - must be 'auto_add', 'reject', or 'warn'")

        # Convert string literal to _HostKeyPolicy enum
        policy_map = {
            "auto_add": _HostKeyPolicy.AUTO_ADD,
            "reject": _HostKeyPolicy.REJECT,
            "warn": _HostKeyPolicy.WARN,
        }

        if ssh_host_key_policy not in policy_map:
            raise ValueError(
                f"Invalid ssh_host_key_policy: {ssh_host_key_policy}. Must be one of: {list(policy_map.keys())}"
            )

        host_key_policy_enum = policy_map[ssh_host_key_policy]

        # Create SSH connection with notification handler
        self.connection = _SSHConnection(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            host_key_policy=host_key_policy_enum,
            notification_handler=self.notification_handler,
        )

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.NetworkHDClientSSH")

    async def connect(self) -> None:
        """Establish SSH connection to the NetworkHD device.

        Raises:
            ConnectionError: If the connection fails.
        """
        self.logger.info(f"Connecting to {self.connection.host}:{self.connection.port}")
        await self.connection.connect()
        self.logger.info(f"Successfully connected to {self.connection.host}:{self.connection.port}")

    async def disconnect(self) -> None:
        """Disconnect from the NetworkHD device."""
        self.logger.info(f"Disconnecting from {self.connection.host}:{self.connection.port}")
        await self.connection.disconnect()
        self.logger.info(f"Disconnected from {self.connection.host}:{self.connection.port}")

    def is_connected(self) -> bool:
        """Check if connected to the device via SSH.

        Returns:
            True if connected, False otherwise.
        """
        return self.connection.is_connected()

    async def send_command(self, command: str, response_timeout: float | None = None) -> str:
        """Send a command to the device via SSH and get the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response (default: 10 seconds).

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected to the device.
            CommandError: If the command fails or times out.
        """
        response = await self.connection.send_command(command.strip(), response_timeout)
        self.logger.debug(f"Command sent: {command}")
        self.logger.debug(f"Raw response: {response}")
        return self._parse_response(response)

    def _parse_response(self, response: str) -> str:
        """Parse the response string from the device.

        Args:
            response: The raw response string.

        Returns:
            The parsed response string.

        Raises:
            CommandError: If the response indicates an error.
        """
        from .exceptions import CommandError

        # Basic response parsing - can be extended for JSON responses
        response = response.replace("Welcome to NetworkHD", "").strip()
        if response.startswith("ERROR"):
            raise CommandError(f"Command error: {response}")
        return response

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Async context manager exit."""
        await self.disconnect()
