import asyncio
from abc import ABC, abstractmethod
from enum import Enum

import paramiko

from .exceptions import CommandError, ConnectionError
from .logging_config import get_logger


class ConnectionType(Enum):
    SSH = "ssh"


class HostKeyPolicy(Enum):
    """SSH host key verification policies."""

    AUTO_ADD = "auto_add"  # paramiko.AutoAddPolicy()
    REJECT = "reject"  # paramiko.RejectPolicy()
    WARN = "warn"  # paramiko.WarningPolicy()
    ASK = "ask"  # paramiko.AskPolicy()


class BaseConnection(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection.

        Raises:
            ConnectionError: If connection fails.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection."""
        pass

    @abstractmethod
    async def send_command(self, command: str, response_timeout: float | None = None) -> str:
        """Send a command through the connection.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response data (in seconds).

        Returns:
            The response string from the device.

        Raises:
            CommandError: If sending the command fails.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the connection is currently established.

        Returns:
            True if connected, False otherwise.
        """
        pass


class SSHConnection(BaseConnection):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: float,
        host_key_policy: HostKeyPolicy,
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

        # Set up logger for this connection instance
        self.logger = get_logger(f"{__name__}.SSHConnection")

    def _get_host_key_policy(self):
        """Get the appropriate Paramiko host key policy."""
        policy_map = {
            HostKeyPolicy.AUTO_ADD: paramiko.AutoAddPolicy(),
            HostKeyPolicy.REJECT: paramiko.RejectPolicy(),
            HostKeyPolicy.WARN: paramiko.WarningPolicy(),
            HostKeyPolicy.ASK: paramiko.AskPolicy(),
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
            if self.host_key_policy == HostKeyPolicy.AUTO_ADD:
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
            self.logger.debug("SSH shell ready")
        except Exception as e:
            self.logger.error(f"SSH connection failed: {e}")
            raise ConnectionError(f"Failed to connect via SSH: {e}") from e

    async def disconnect(self) -> None:
        """Close the SSH shell and client connection."""
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
                If None, returns as soon as no more data is available.

        Returns:
            The response string from the device.

        Raises:
            ConnectionError: If not connected.
            CommandError: If sending the command or receiving response fails.
        """
        if not self.client or not self.shell:
            raise ConnectionError("Not connected")

        try:
            self.logger.debug(f"Sending command via SSH: {command}")
            self.shell.send(command + "\n")
            response = ""

            if response_timeout is None:
                # Read until no more data available
                while True:
                    await asyncio.sleep(0.1)
                    if self.shell.recv_ready():
                        data = self.shell.recv(1024).decode("ascii")
                        response += data
                    else:
                        # If no data ready, break to avoid infinite loop
                        break
            else:
                # Read with timeout
                no_data_count = 0
                max_no_data_iterations = int(response_timeout * 10)  # Convert seconds to 0.1s intervals

                while True:
                    await asyncio.sleep(0.1)
                    if self.shell.recv_ready():
                        data = self.shell.recv(1024).decode("ascii")
                        response += data
                        no_data_count = 0  # Reset counter when we receive data
                    else:
                        no_data_count += 1
                        if no_data_count >= max_no_data_iterations:
                            break

            self.logger.debug(f"Received response via SSH (length: {len(response)})")
            return response
        except Exception as e:
            self.logger.error(f"Failed to send command via SSH: {e}")
            raise CommandError(f"Failed to send command: {e}") from e

    def is_connected(self) -> bool:
        """Check if the SSH client and shell are connected.

        Returns:
            True if connected, False otherwise.
        """
        return self.client is not None and self.client.get_transport() is not None and self.shell is not None


class NetworkHDClient:
    _connection_factory = {
        ConnectionType.SSH: SSHConnection,
    }

    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "admin",
        password: str | None = None,
        connection_type: ConnectionType = ConnectionType.SSH,
        timeout: float = 10.0,
        ssh_host_key_policy: HostKeyPolicy = HostKeyPolicy.WARN,
        **kwargs,
    ):
        """Initialize a NetworkHD client.

        Args:
            host: The hostname or IP address of the NetworkHD device.
            port: The port number for the connection. Default is 22 (SSH).
            username: The username for authentication. Default is "admin".
            password: The password for authentication.
            connection_type: The type of connection to use. Default is SSH.
            timeout: Connection timeout in seconds. Default is 10.0 seconds.
            ssh_host_key_policy: SSH host key verification policy. Defaults to WARN.
            **kwargs: Additional transport-specific parameters.

        Raises:
            ValueError: If the connection type is unsupported.
        """
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh_host_key_policy = ssh_host_key_policy

        connection_cls = self._connection_factory.get(connection_type)
        if not connection_cls:
            raise ValueError(f"Unsupported connection type: {connection_type}")

        # Pass ssh_host_key_policy to SSH connections
        if connection_type == ConnectionType.SSH:
            self.connection = connection_cls(host, port, username, password, timeout, ssh_host_key_policy, **kwargs)
        else:
            self.connection = connection_cls(host, port, username, password, timeout, **kwargs)

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.NetworkHDClient")

    async def connect(self) -> None:
        """Establish the underlying connection.

        Raises:
            ConnectionError: If connection fails.
        """
        self.logger.info(f"Connecting to {self.host}:{self.port} via {self.connection_type.value}")
        await self.connection.connect()
        self.logger.info(f"Successfully connected to {self.host}:{self.port}")

    async def disconnect(self) -> None:
        """Close the underlying connection."""
        self.logger.info(f"Disconnecting from {self.host}:{self.port}")
        await self.connection.disconnect()
        self.logger.info(f"Disconnected from {self.host}:{self.port}")

    def is_connected(self) -> bool:
        """Check if the underlying connection is established.

        Returns:
            True if connected, False otherwise.
        """
        return self.connection.is_connected()

    async def send_command(self, command: str, response_timeout: float | None = None) -> str:
        """Send a command through the underlying connection and parse the response.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for response data (in seconds).

        Returns:
            The parsed response string.

        Raises:
            ResponseError: If the response indicates an error.
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
            ResponseError: If the response indicates an error.
        """
        # Basic response parsing - can be extended for JSON responses
        response = response.replace("Welcome to NetworkHD", "").strip()
        if response.startswith("ERROR"):
            raise CommandError(f"Command error: {response}")
        return response

    async def __aenter__(self):
        """Async context manager entry: connect to the device.

        Returns:
            The NetworkHDClient instance.
        """
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Async context manager exit: disconnect from the device.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        await self.disconnect()
