"""SSH client for NetworkHD devices with simplified architecture."""

import asyncio
import contextlib
from collections.abc import Callable
from typing import Any, TypeVar

import paramiko

from ..exceptions import AuthenticationError, ConnectionError
from ._client import _BaseNetworkHDClient

# Seconds between SSH keepalive packets, so a dead link is noticed and NAT/firewall state is kept
_KEEPALIVE_INTERVAL = 30

# Most bytes returned by one _read_available() call
_MAX_READ = 65536

_T = TypeVar("_T")


async def _in_thread(func: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
    """Run a blocking call in a thread; if cancelled, wait for it to finish so its result can still be closed."""
    future = asyncio.ensure_future(asyncio.to_thread(func, *args, **kwargs))
    try:
        return await asyncio.shield(future)
    except asyncio.CancelledError:
        with contextlib.suppress(Exception):
            await future
        raise


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
        circuit_breaker_timeout: float | None = None,
        heartbeat_interval: float | None = None,
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
            circuit_breaker_timeout: Deprecated and ignored (emits DeprecationWarning); removed in 4.0.
            heartbeat_interval: Deprecated and ignored (emits DeprecationWarning); removed in 4.0. SSH
                keepalive packets are sent every 30 s instead.
            message_dispatcher_interval: Sleep interval in seconds for the message
                dispatcher loop when nothing is readable (default: 0.1).

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        super().__init__(
            message_dispatcher_interval=message_dispatcher_interval,
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

        # Store connection parameters
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh_host_key_policy = ssh_host_key_policy

        # SSH connection objects
        self.client: paramiko.SSHClient | None = None
        self.shell: paramiko.Channel | None = None

    # ============================================================================
    # PROTECTED METHODS - SSH Implementation
    # ============================================================================

    @property
    def _target(self) -> str:
        return f"{self.host}:{self.port}"

    async def _open_transport(self) -> None:
        """Open the SSH connection and interactive shell; blocking paramiko calls run in a thread.

        Raises:
            AuthenticationError: If authentication fails.
            ConnectionError: On SSH protocol errors.
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(self._get_host_key_policy())
        try:
            await _in_thread(
                self.client.connect,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )
        except paramiko.AuthenticationException as e:
            raise AuthenticationError(self.username, self.host) from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error: {e}") from e

        transport = self.client.get_transport()
        if transport is not None:
            transport.set_keepalive(_KEEPALIVE_INTERVAL)
        shell = await _in_thread(self.client.invoke_shell)
        shell.settimeout(self.timeout)
        self.shell = shell

    async def _close_transport(self) -> None:
        shell, client = self.shell, self.client
        self.shell = self.client = None
        try:
            if shell is not None:
                await asyncio.to_thread(shell.close)
        finally:
            if client is not None:
                await asyncio.to_thread(client.close)

    def _transport_alive(self) -> bool:
        if self.client is None or self.shell is None or self.shell.closed:
            return False
        transport = self.client.get_transport()
        return transport is not None and transport.is_active()

    async def _write(self, command: str) -> None:
        if self.shell is None:
            raise ConnectionError("SSH shell not available")
        await asyncio.to_thread(self.shell.sendall, (command + "\n").encode())

    async def _read_available(self) -> bytes:
        if self.shell is None:
            raise ConnectionError("SSH shell not available")
        data = b""
        # Bounded so a flooding device can't grow one read without limit; the rest is read on the next call
        while len(data) < _MAX_READ and self.shell.recv_ready():
            chunk = self.shell.recv(4096)
            if not chunk:
                raise ConnectionError("SSH channel closed")
            data += chunk
        return data

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
