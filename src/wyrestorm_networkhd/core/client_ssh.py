"""SSH client for NetworkHD devices with simplified architecture."""

import asyncio
import base64
import builtins
import contextlib
import hashlib
import re
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

import paramiko

from ..exceptions import AuthenticationError, ConnectionError, HostKeyMismatchError
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

# Fingerprints in a string are separated by commas or whitespace (spaces, newlines)
_FINGERPRINT_SEPARATORS = re.compile(r"[,\s]+")


def _parse_sha256(token: str) -> str | None:
    """Return "SHA256:<base64>" for a base64 SHA-256 digest (with or without "=" padding), else None."""
    b64 = token.rstrip("=")
    if len(b64) != 43:
        return None
    try:
        digest = base64.b64decode(b64 + "=", validate=True)
    except ValueError:  # binascii.Error is a ValueError
        return None
    return f"SHA256:{b64}" if len(digest) == 32 else None


def normalize_fingerprints(value: str | Sequence[str]) -> tuple[str, ...]:
    """Parse SSH host key SHA256 fingerprints into canonical form.

    Accepts "SHA256:<base64>" or bare "<base64>", with or without "=" padding. A string may hold several,
    separated by commas, whitespace or newlines, and may be the output of ``ssh-keygen -lf`` (e.g.
    ``256 SHA256:... [host]:10022 (ECDSA)``): other words on such lines are ignored.

    Args:
        value: A string, or a sequence of strings, holding one or more fingerprints.

    Returns:
        The fingerprints as "SHA256:<base64 without padding>", duplicates removed, in input order.

    Raises:
        ValueError: If no fingerprint is found, a "SHA256:" token is not a valid SHA-256 digest, or an item
            is not a string.
    """
    items = [value] if isinstance(value, str) else list(value)
    found: dict[str, None] = {}
    for item in items:
        if not isinstance(item, str):
            raise ValueError(f"Host key fingerprint must be a string, not {type(item).__name__}")
        for token in _FINGERPRINT_SEPARATORS.split(item):
            explicit = token[:7].upper() == "SHA256:"
            fingerprint = _parse_sha256(token[7:] if explicit else token)
            if fingerprint is not None:
                found[fingerprint] = None
            elif explicit:
                raise ValueError(f"Invalid SHA256 host key fingerprint: {token!r}")
    if not found:
        raise ValueError("No SHA256 host key fingerprint found")
    return tuple(found)


def _fingerprint(key: paramiko.PKey) -> str:
    """The key's SHA256 fingerprint as OpenSSH prints it: unpadded base64 of the SHA-256 of the key blob."""
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")


class _HostKeyPolicy(paramiko.MissingHostKeyPolicy):
    """Records the presented host key's fingerprint, then checks it against the pins or defers to ``fallback``.

    paramiko calls this before authenticating (no known_hosts is loaded, so every key is "missing").
    """

    def __init__(self, pins: tuple[str, ...] | None, fallback: paramiko.MissingHostKeyPolicy):
        self.pins = pins
        self.fallback = fallback
        self.presented: str | None = None

    def missing_host_key(self, client: paramiko.SSHClient, hostname: str, key: paramiko.PKey) -> None:
        self.presented = _fingerprint(key)
        if self.pins is None:
            self.fallback.missing_host_key(client, hostname, key)
        elif self.presented not in self.pins:
            raise HostKeyMismatchError(hostname, self.presented)


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
        host_key_fingerprints: str | Sequence[str] | None = None,
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
            host_key_fingerprints: SHA256 fingerprint(s) of the controller's SSH host key, in any form
                `normalize_fingerprints` accepts. When given, only a matching host key is accepted, checked before
                the password is sent, and `ssh_host_key_policy` is ignored; a mismatch raises
                HostKeyMismatchError. None (default) leaves host key checking to `ssh_host_key_policy`.
                Also a settable attribute, read at every connect: assign a tuple from `normalize_fingerprints` (or
                None) on an existing client, e.g. after trusting `host_key_fingerprint` on first use, and the next
                connect or reconnect is checked against it.

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
        self.host_key_fingerprints = (
            None if host_key_fingerprints is None else normalize_fingerprints(host_key_fingerprints)
        )
        self._host_key_fingerprint: str | None = None

        # SSH connection objects
        self.client: paramiko.SSHClient | None = None
        self.shell: paramiko.Channel | None = None

    # ============================================================================
    # PROTECTED METHODS - SSH Implementation
    # ============================================================================

    @property
    def host_key_fingerprint(self) -> str | None:
        """SHA256 fingerprint ("SHA256:<base64>") of the host key presented on the last successful connect.

        Set whether or not fingerprints are pinned; None before the first successful connect. Pass it as
        ``host_key_fingerprints`` on later connections to trust the controller on first use.
        """
        return self._host_key_fingerprint

    @property
    def _target(self) -> str:
        return f"{self.host}:{self.port}"

    async def _open_transport(self) -> None:
        """Open the SSH connection and interactive shell; blocking paramiko calls run in a thread.

        Raises:
            AuthenticationError: If authentication fails.
            HostKeyMismatchError: If the host key matches none of the pinned fingerprints.
            ConnectionError: On SSH protocol errors.
        """
        if self.host_key_fingerprints is not None:
            self.logger.debug("Host key fingerprints are pinned; ssh_host_key_policy is ignored")
        policy = _HostKeyPolicy(self.host_key_fingerprints, self._get_host_key_policy())
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(policy)
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
        # paramiko waits for the shell request's reply with no time limit; closing the client ends that wait
        shell_future = asyncio.ensure_future(asyncio.to_thread(self.client.invoke_shell))
        try:
            await asyncio.wait_for(asyncio.shield(shell_future), self.timeout)
        except builtins.TimeoutError:
            await asyncio.to_thread(self.client.close)
            with contextlib.suppress(Exception):
                await shell_future
            raise ConnectionError(f"Timed out opening the SSH shell after {self.timeout}s") from None
        except asyncio.CancelledError:
            with contextlib.suppress(Exception):
                await shell_future
            raise
        shell = shell_future.result()
        shell.settimeout(self.timeout)
        self.shell = shell
        self._host_key_fingerprint = policy.presented

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
