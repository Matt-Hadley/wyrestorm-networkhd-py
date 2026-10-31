"""NetworkHD client with inheritance-based architecture."""

import asyncio
import builtins
import contextlib
import inspect
import random
import re
import time
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any

from ..exceptions import (
    AuthenticationError,
    CommandError,
    ConnectionError,
    ConnectionLostError,
    HostKeyMismatchError,
    NetworkHDError,
    ReconnectionError,
    TimeoutError,
    UnknownCommandError,
)
from ..logging_config import get_logger
from ..models.api_notifications import (
    NotificationObject,
    NotificationParser,
)

# Upper bound for the reconnect backoff delay, in seconds
_MAX_RECONNECT_DELAY = 30.0

# Header line of an RS-232 data notification; <infolen> bytes of data follow after CR LF (PDF section 12).
# The digit count is not bounded here so an oversized header is recognised (and dropped) rather than dispatched.
_SERIALINFO_HEADER = re.compile(r"^notify serialinfo \S+ (hex|ascii) (\d+):$")

# What hex-mode serialinfo data may contain; anything else means <infolen> overstated the data
_HEX_PAYLOAD = re.compile(rb"[0-9A-Fa-f\s]*")

# Largest <infolen> accepted; hex data of a 16 KiB RS-232 burst is ~48 KiB, far above what endpoints send in one go
_MAX_SERIALINFO_LEN = 65536

# Longest line, or multi-line irinfo notification, kept while waiting for its end; beyond it the data is dropped
_MAX_LINE_LEN = 65536

# A continuation line of a ``notify irinfo`` notification: hex words, optionally ending with the closing quote
_IRINFO_DATA = re.compile(r'^[0-9A-Fa-f]+(?:\s+[0-9A-Fa-f]+)*\s*"?$')

# First and second words of the commands this library sends (the command strings in commands/*.py). The controller
# echoes every session's commands to every session, so a line starting with one of these may be another client's
# command echo. The second word keeps a reply row whose first device happens to be named like a verb ("scene display1")
# from being taken for one; cec, infrared and serial are followed by quoted data or an option instead.
_COMMAND_WORDS = {
    "config": {"get", "set"},
    "matrix": {"audio", "audio2", "audio3", "get", "infrared", "infrared2", "serial", "serial2", "set", "usb", "video"},
    "mscene": {"active", "change", "get", "set"},
    "mview": {"get", "set"},
    "scene": {"active", "get", "set"},
    "vw": {"change", "get"},
    "wscene2": {"active", "get", "window"},
}
_DATA_COMMAND_VERBS = frozenset({"cec", "infrared", "serial"})


def _is_foreign_echo(line: str, command: str) -> bool:
    """Return whether a line looks like the echo of a command other than ours (sent by another API session).

    Reply lines that start with a verb are excluded: headers end with ":" ("matrix information:", "scene list:") and
    acknowledgements end with success/failure ("scene OfficeVW-Splitmode active success"), and replies about a named
    object put a possessive second ("scene OfficeVW-Splitmode's source in [1,2] change to source1"). A repeat of our
    own command after our echo is another session's and is dropped by the caller.
    """
    words = line.split()
    if len(words) < 2:
        return False
    verb, second = words[0], words[1]
    if verb in _DATA_COMMAND_VERBS:
        is_command = second.startswith(('"', "-"))
    else:
        is_command = second in _COMMAND_WORDS.get(verb, ())
    return (
        is_command
        and line != command
        and not line.endswith(":")
        and words[-1].lower() not in ("success", "failure")
        and not second.endswith("'s")
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

    def __init__(self) -> None:
        """Initialize notification handler with parser and callbacks."""
        self._callbacks: dict[str, list[Callable[[NotificationObject], Any]]] = {}
        self._parser = NotificationParser()
        # Keeps references to tasks running async callbacks so they are not garbage collected mid-run
        self._tasks: set[asyncio.Future] = set()
        self.logger = get_logger(f"{__name__}._NotificationHandler")

    def register_callback(self, notification_type: str, callback: Callable[[NotificationObject], Any]) -> None:
        """Register a callback for a specific notification type.

        Args:
            notification_type: Type of notification to listen for.
            callback: Function or coroutine function to call when this notification type is received.
        """
        if notification_type not in self._callbacks:
            self._callbacks[notification_type] = []
        self._callbacks[notification_type].append(callback)
        self.logger.debug(f"Registered callback for {notification_type} notifications")

    def unregister_callback(self, notification_type: str, callback: Callable[[NotificationObject], Any]) -> None:
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

    def handle_notification(self, notification_line: str) -> None:
        """Parse and dispatch a notification to registered callbacks.

        Sync callbacks run immediately; if a callback returns an awaitable it is scheduled as a task.
        Callback errors are logged and never reach the reader.

        Args:
            notification_line: Raw notification string from the device.
        """
        try:
            notification_type = self._parser.get_notification_type(notification_line)
        except ValueError:
            self.logger.debug(f"Ignoring unknown notification type: {notification_line}")
            return

        try:
            parsed_notification = self._parser.parse_notification(notification_line)
        except Exception:
            self.logger.warning(f"Could not parse notification: {notification_line}", exc_info=True)
            return

        # Copy so callbacks may (un)register callbacks while we iterate
        for callback in list(self._callbacks.get(notification_type, ())):
            try:
                result = callback(parsed_notification)
                if inspect.isawaitable(result):
                    task = asyncio.ensure_future(result)
                    self._tasks.add(task)
                    task.add_done_callback(self._on_callback_done)
            except Exception:
                self.logger.exception(f"Error in {notification_type} notification callback")

        self.logger.debug(f"Processed {notification_type} notification: {parsed_notification}")

    def _on_callback_done(self, task: asyncio.Future) -> None:
        """Forget a finished async callback task and log its error, if any."""
        self._tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            self.logger.error("Error in async notification callback", exc_info=task.exception())


class _BaseNetworkHDClient(ABC):
    """Base NetworkHD client with common functionality.

    This is a private base class that owns the connection lifecycle, the reader task, response framing and
    notification dispatch. Protocol-specific subclasses only open/close the transport and read/write bytes.
    """

    def __init__(
        self,
        *,
        message_dispatcher_interval: float,
        circuit_breaker_timeout: float | None = None,
        heartbeat_interval: float | None = None,
    ):
        """Initialize base client with notification handler and state management.

        Args:
            message_dispatcher_interval: Sleep interval in seconds between reads when nothing is readable.
            circuit_breaker_timeout: Deprecated and ignored; will be removed in 4.0.
            heartbeat_interval: Deprecated and ignored; will be removed in 4.0.

        Raises:
            ValueError: If any parameters are invalid.
        """
        for name, value in (
            ("circuit_breaker_timeout", circuit_breaker_timeout),
            ("heartbeat_interval", heartbeat_interval),
        ):
            if value is not None:
                warnings.warn(
                    f"{name} is deprecated and ignored; it will be removed in 4.0", DeprecationWarning, stacklevel=3
                )
        if message_dispatcher_interval <= 0:
            raise ValueError("Message dispatcher interval must be positive")
        self.message_dispatcher_interval = message_dispatcher_interval

        # Create notification handler (same for all protocols)
        self.notification_handler = _NotificationHandler()

        # Connection state management
        self._connection_state = _ConnectionState.DISCONNECTED
        self._connection_error: str | None = None
        self._connection_lost_reason: str | None = None
        self._reconnect_lock = asyncio.Lock()
        # Serialises connect() and disconnect() so only one reader task and transport exist at a time
        self._connection_lock = asyncio.Lock()

        # Reader task and line framing
        self._message_dispatcher_task: asyncio.Task | None = None
        self._reader_idle = asyncio.Event()
        self._buffer = bytearray()
        self._pending_serialinfo: tuple[str, int, bool] | None = None  # header, <infolen>, hex mode
        self._pending_irinfo: str | None = None
        self._skip_line = False  # drop everything up to the next line break (after discarding an overlong line)

        # Command response handling: lines go to the command currently waiting, None tells it the link died
        self._response_queue: asyncio.Queue[str | None] | None = None
        self._command_lock = asyncio.Lock()

        self._connection_metrics: dict[str, Any] = {
            "commands_sent": 0,
            "commands_failed": 0,
            "notifications_received": 0,
            "last_command_time": None,
        }

        # Set up logger for this client instance
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    # ============================================================================
    # ABSTRACT METHODS - Transport, implemented by subclasses
    # ============================================================================

    @property
    @abstractmethod
    def _target(self) -> str:
        """Human-readable name of the device connection, for logs and errors."""

    @abstractmethod
    async def _open_transport(self) -> None:
        """Open the transport.

        Raises:
            NetworkHDError: Library errors (e.g. AuthenticationError) are re-raised as is; anything else is
                wrapped in ConnectionError by connect().
        """

    @abstractmethod
    async def _close_transport(self) -> None:
        """Close the transport and clear its objects, even if closing fails."""

    @abstractmethod
    def _transport_alive(self) -> bool:
        """Return whether the transport is open."""

    @abstractmethod
    async def _write(self, command: str) -> None:
        """Write one command, adding the protocol's line terminator."""

    @abstractmethod
    async def _read_available(self) -> bytes:
        """Return all bytes readable right now without waiting, or b"" if none.

        Raises:
            Exception: If the link is closed; the reader then marks the connection as lost.
        """

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
        self, notification_type: str, callback: Callable[[NotificationObject], Any]
    ) -> None:
        """Register a callback function for specific notification types.

        Args:
            notification_type: Type of notification to listen for.
                Available types: 'endpoint', 'cecinfo', 'irinfo', 'serialinfo', 'video', 'sink'
            callback: Function or coroutine function to call when this notification type is received.
                It receives the parsed notification object. A coroutine is scheduled as a task; exceptions
                are logged.

        Raises:
            ValueError: If notification_type isn't one of the available types.

        Example:
            ```python
            def handle_endpoint_status(notification):
                print(f"Endpoint {notification.device} is {'online' if notification.online else 'offline'}")

            client.register_notification_callback("endpoint", handle_endpoint_status)
            ```
        """
        known = [info["type"] for info in NotificationParser._NOTIFICATION_MAPPINGS.values()]
        if notification_type not in known:
            raise ValueError(f"Unknown notification type {notification_type!r}, expected one of {known}")
        self.notification_handler.register_callback(notification_type, callback)

    def unregister_notification_callback(
        self, notification_type: str, callback: Callable[[NotificationObject], Any]
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

    async def connect(self) -> None:
        """Connect to the NetworkHD device and start the reader task.

        Any existing connection and reader task are torn down first, so this also serves to reconnect.

        Raises:
            ConnectionError: If the connection fails.
            AuthenticationError: If authentication fails (SSH).
        """
        async with self._connection_lock:
            await self._teardown()
            self._set_connection_state(_ConnectionState.CONNECTING)
            self.logger.info(f"Connecting to {self._target}")
            try:
                await self._open_transport()
            except Exception as e:
                self._set_connection_state(_ConnectionState.ERROR, f"Connection failed: {e}")
                with contextlib.suppress(Exception):
                    await self._close_transport()
                if isinstance(e, NetworkHDError):
                    raise
                raise ConnectionError(f"Connection failed: {e}") from e
            except BaseException:
                # Cancelled: close whatever was opened so no session is left behind
                self._set_connection_state(_ConnectionState.DISCONNECTED)
                with contextlib.suppress(Exception):
                    await self._close_transport()
                raise

            self._buffer = bytearray()
            self._pending_serialinfo = None
            self._pending_irinfo = None
            self._skip_line = False
            self._connection_lost_reason = None
            self._message_dispatcher_task = asyncio.create_task(self._message_dispatcher())
            self._set_connection_state(_ConnectionState.CONNECTED)
            self.logger.info(f"Successfully connected to {self._target}")

    async def disconnect(self) -> None:
        """Disconnect from the NetworkHD device and stop the reader task."""
        async with self._connection_lock:
            self.logger.info(f"Disconnecting from {self._target}")
            try:
                await self._teardown(suppress_errors=False)
            finally:
                self._set_connection_state(_ConnectionState.DISCONNECTED)
            self.logger.info(f"Disconnected from {self._target}")

    def is_connected(self) -> bool:
        """Check if connected to the device.

        Returns:
            True if the transport is open and the reader is running, False otherwise.
        """
        connected = self._connection_state == _ConnectionState.CONNECTED and self._transport_alive()
        if not connected and self._connection_state == _ConnectionState.CONNECTED:
            self._set_connection_state(_ConnectionState.DISCONNECTED)
        return connected

    async def reconnect(self, max_attempts: int = 5, delay: float = 1.0) -> None:
        """Reconnect to the device, retrying with capped exponential backoff and jitter.

        If another reconnect is already running, waits for it and returns if it succeeded.

        Args:
            max_attempts: Maximum number of connection attempts.
            delay: Delay before the second attempt in seconds; doubles per attempt, capped at 30 s.

        Raises:
            ReconnectionError: If every attempt fails.
            AuthenticationError: If the device rejects the credentials (not retried).
            HostKeyMismatchError: If the SSH host key matches none of the pinned fingerprints (not retried).
        """
        already_running = self._reconnect_lock.locked()
        async with self._reconnect_lock:
            if already_running and self.is_connected():
                return

            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                if attempt > 1:
                    # Jitter only spreads retries out; it has no security role.
                    wait_time = min(delay * 2 ** (attempt - 2), _MAX_RECONNECT_DELAY) * random.uniform(0.5, 1.0)  # nosec B311
                    self._set_connection_state(_ConnectionState.RECONNECTING, str(last_error))
                    self.logger.info(f"Waiting {wait_time:.1f}s before reconnection attempt {attempt}/{max_attempts}")
                    await asyncio.sleep(wait_time)
                try:
                    self.logger.info(f"Reconnection attempt {attempt}/{max_attempts}")
                    await self.connect()
                    self.logger.info("Reconnection successful")
                    return
                except (AuthenticationError, HostKeyMismatchError):
                    raise
                except Exception as e:
                    last_error = e
                    self.logger.warning(f"Reconnection attempt {attempt} failed: {e}")

            raise ReconnectionError(self._target, max_attempts, str(last_error)) from last_error

    async def send_command(
        self, command: str, response_timeout: float = 10.0, response_line_timeout: float = 0.3
    ) -> str:
        """Send a command to the device and get the response.

        The response starts at the line echoing the command (earlier, stale lines are dropped) and ends when no
        further line arrives for response_line_timeout. Devices that do not echo get all lines received. A reply
        still arriving when response_timeout expires is not returned truncated: TimeoutError is raised. The controller
        also echoes other API sessions' commands and replies; such an echo ends the response, and it and the rest of
        that burst are dropped.

        Args:
            command: The command string to send.
            response_timeout: Maximum time to wait for the response in seconds, including the first line.
            response_line_timeout: Idle gap in seconds after a line that ends the response.

        Returns:
            The response string from the device, lines joined with "\\n".

        Raises:
            ConnectionError: If not connected to the device (ConnectionLostError if the link dropped).
            CommandError: If the command contains a line break or the device reports an error.
            UnknownCommandError: If the device answers "unknown command".
            TimeoutError: If the response has not ended within response_timeout.
        """
        command = command.strip()
        if "\r" in command or "\n" in command:
            raise CommandError(f"Command must be a single line: {command!r}")
        async with self._command_lock:
            # Checked under the lock: the link may have dropped while this command waited for the one before it
            if not self.is_connected():
                if self._connection_lost_reason is not None:
                    raise ConnectionLostError(self._target, self._connection_lost_reason)
                raise ConnectionError("Not connected")
            try:
                await self._drain_stale_lines()
                queue: asyncio.Queue[str | None] = asyncio.Queue()
                self._response_queue = queue
                self.logger.debug(f"Sending command: {command}")
                try:
                    await self._write(command)
                except NetworkHDError:
                    raise
                except OSError as e:
                    # The link can drop after the check above; report it as the library error the docstring promises
                    raise ConnectionLostError(self._target, f"write failed: {e!r}") from e
                self._record_command_sent()
                lines = await self._collect_response(command, queue, response_timeout, response_line_timeout)
                response = self._parse_response(command, lines)
            except Exception:
                self._record_command_failed()
                raise
            finally:
                self._response_queue = None

        self.logger.debug(f"Raw response: {response}")
        return response

    # ============================================================================
    # PROTECTED METHODS - Command Handling
    # ============================================================================

    async def _drain_stale_lines(self) -> None:
        """Let the reader consume and drop whatever is already readable before a command is sent."""
        self._reader_idle.clear()
        # Bounded so a busy stream of notifications cannot hold the command back
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._reader_idle.wait(), timeout=1.0)

    async def _collect_response(
        self, command: str, queue: "asyncio.Queue[str | None]", response_timeout: float, response_line_timeout: float
    ) -> list[str]:
        """Collect response lines for a command.

        Returns:
            The response lines, starting at the command echo when one was seen.

        Raises:
            TimeoutError: If no line arrives within response_timeout, or lines are still arriving after it.
            ConnectionLostError: If the link drops, or the client disconnects, while waiting.
        """
        lines: list[str] = []
        echo_index: int | None = None
        # Another session's command echo was seen (the controller echoes every session's traffic to all of them).
        # Before our echo: the device echoes, so wait for ours past idle gaps. After it: our reply has ended, and the
        # rest of that burst is dropped.
        foreign = False

        def add(line: str | None) -> None:
            nonlocal echo_index, foreign
            if line is None:
                raise ConnectionLostError(self._target, self._connection_lost_reason or "connection closed")
            if echo_index is None and line == command:
                echo_index, foreign = len(lines), False
            elif line == command or _is_foreign_echo(line, command):
                foreign = True
            if foreign and echo_index is not None:
                self.logger.debug(f"Dropping another session's line during '{command}': {line}")
                return
            lines.append(line)

        loop = asyncio.get_running_loop()
        deadline = loop.time() + response_timeout
        try:
            add(await asyncio.wait_for(queue.get(), timeout=response_timeout))
        except builtins.TimeoutError:
            raise TimeoutError(command, response_timeout) from None
        while True:
            awaiting_echo = foreign and echo_index is None
            try:
                line = await asyncio.wait_for(
                    queue.get(), timeout=max(deadline - loop.time(), 0) if awaiting_echo else response_line_timeout
                )
            except builtins.TimeoutError:
                if awaiting_echo:
                    raise TimeoutError(command, response_timeout) from None
                break  # the idle gap ends the response, even if it ran past the deadline
            if line is not None and loop.time() > deadline:
                raise TimeoutError(command, response_timeout)
            add(line)

        if echo_index:
            self.logger.debug(f"Dropping stale lines before echo of '{command}': {lines[:echo_index]}")
            lines = lines[echo_index:]
        return lines

    def _parse_response(self, command: str, lines: list[str]) -> str:
        """Generic response parsing for NetworkHD devices.

        Args:
            command: The command that was sent.
            lines: The response lines, starting with the echo if the device sent one.

        Returns:
            The response string.

        Raises:
            CommandError: If the response indicates an error.
            UnknownCommandError: If the device did not understand the command.
        """
        lines = [stripped for line in lines if (stripped := line.replace("Welcome to NetworkHD", "").strip())]
        if any(line.lower() == "unknown command" for line in lines):
            raise UnknownCommandError(command)
        body = lines[1:] if lines and lines[0] == command else lines
        if body and body[0].startswith("ERROR"):
            detail = "\n".join(body)
            raise CommandError(f"Command error: {detail}")
        return "\n".join(lines)

    # ============================================================================
    # PROTECTED METHODS - Reader
    # ============================================================================

    async def _message_dispatcher(self) -> None:
        """Read from the transport until it closes, routing lines to notifications or the waiting command."""
        try:
            while True:
                if not self._transport_alive():
                    raise ConnectionError("transport closed")
                data = await self._read_available()
                if data:
                    self._feed(data)
                    continue
                self._reader_idle.set()
                await asyncio.sleep(self.message_dispatcher_interval)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self._mark_connection_lost(str(e))
        finally:
            self._reader_idle.set()
            if self._message_dispatcher_task is asyncio.current_task():
                self._message_dispatcher_task = None
            self.logger.debug("Message dispatcher stopped")

    def _feed(self, data: bytes) -> None:
        """Split received bytes into lines and route each one.

        Multi-line notifications are assembled first: ``notify serialinfo`` by its <infolen> byte count,
        ``notify irinfo`` while lines look like IR data, until its closing quote; the handler gets header and data
        as one "\\n"-joined string. Lines and pending notifications are capped at 64 KiB; a serialinfo with a larger
        <infolen> is dropped. Hex-mode serialinfo data must be hex digits and whitespace: other bytes mean <infolen>
        overstated the data, so framing is abandoned and the buffer is parsed as normal lines.
        """
        self._buffer += data
        buffer = self._buffer
        pos = 0  # start of unconsumed data; consumed bytes are removed once, on return
        try:
            while True:
                if self._pending_serialinfo is not None:
                    header, length, hex_mode = self._pending_serialinfo
                    if hex_mode and not _HEX_PAYLOAD.fullmatch(buffer, pos, pos + length):
                        self.logger.debug(f"Abandoning serialinfo framing, data isn't hex: {header!r}")
                        self._pending_serialinfo = None
                        continue
                    if len(buffer) - pos < length:
                        return
                    serial_data = bytes(buffer[pos : pos + length])
                    pos += length
                    self._pending_serialinfo = None
                    # No terminator is promised after the data: consume a line break if one is already here;
                    # anything else (including a late one) is parsed as normal lines
                    if buffer.startswith((b"\r\n", b"\n"), pos):
                        pos = buffer.index(b"\n", pos) + 1
                    self._dispatch_notification(f"{header}\n{serial_data.decode('utf-8', errors='replace')}")
                    continue

                end = buffer.find(b"\n", pos)
                if end == -1:
                    if len(buffer) - pos > _MAX_LINE_LEN:
                        self.logger.warning(f"Dropping {len(buffer) - pos} bytes received without a line break")
                        pos = len(buffer)
                        self._skip_line = True
                    return
                raw_line = buffer[pos:end]
                pos = end + 1
                if self._skip_line or len(raw_line) > _MAX_LINE_LEN:
                    if not self._skip_line:
                        self.logger.warning(f"Dropping {len(raw_line)}-byte line")
                    self._skip_line = False
                    continue
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                if self._pending_irinfo is not None:
                    if _IRINFO_DATA.match(line) and len(self._pending_irinfo) + len(line) < _MAX_LINE_LEN:
                        self._pending_irinfo += "\n" + line
                        if '"' in line:
                            line, self._pending_irinfo = self._pending_irinfo, None
                            self._dispatch_notification(line)
                        continue
                    # Not IR data (or too long): the closing quote never came, so hand over what we have and handle
                    # this line normally
                    pending, self._pending_irinfo = self._pending_irinfo, None
                    self._dispatch_notification(pending)

                self.logger.debug(f"Message dispatcher received line: {line!r}")
                if line.startswith("notify "):
                    if match := _SERIALINFO_HEADER.match(line):
                        mode, digits = match.groups()
                        if len(digits) > len(str(_MAX_SERIALINFO_LEN)) or int(digits) > _MAX_SERIALINFO_LEN:
                            # Without a believable length the data can't be framed; its lines are handled as they come
                            self.logger.warning(f"Dropping serialinfo with oversized length: {line[:100]!r}")
                        else:
                            self._pending_serialinfo = (line, int(digits), mode == "hex")
                    elif line.startswith("notify irinfo ") and line.count('"') == 1:
                        self._pending_irinfo = line
                    else:
                        self._dispatch_notification(line)
                elif self._response_queue is not None:
                    self._response_queue.put_nowait(line)
                else:
                    self.logger.debug(f"Dropping unsolicited line: {line}")
        finally:
            del buffer[:pos]

    def _dispatch_notification(self, notification: str) -> None:
        """Hand a complete notification to the notification handler."""
        self._record_notification_received()
        self.notification_handler.handle_notification(notification)

    def _mark_connection_lost(self, reason: str) -> None:
        """Record that the link died and fail the command waiting for a response, if any."""
        self.logger.warning(f"Connection to {self._target} lost: {reason}")
        self._connection_lost_reason = reason
        self._set_connection_state(_ConnectionState.ERROR, f"Connection lost: {reason}")
        if self._response_queue is not None:
            self._response_queue.put_nowait(None)

    async def _teardown(self, *, suppress_errors: bool = True) -> None:
        """Fail the command waiting for a response, stop the reader task and close the transport."""
        # Detach the waiting command's queue so it fails now and never gets a line from the next session
        queue, self._response_queue = self._response_queue, None
        if queue is not None:
            queue.put_nowait(None)
        task, self._message_dispatcher_task = self._message_dispatcher_task, None
        if task is not None and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        if suppress_errors:
            with contextlib.suppress(Exception):
                await self._close_transport()
        else:
            await self._close_transport()

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

    def _set_connection_state(self, state: _ConnectionState, error: str | None = None) -> None:
        """Update connection state and error information.

        Args:
            state: New connection state.
            error: Optional error message.
        """
        old_state, self._connection_state = self._connection_state, state
        self._connection_error = error

        if state != old_state:
            self.logger.info(f"Connection state changed: {old_state.value} -> {state.value}")
            if error:
                self.logger.warning(f"Connection error: {error}")

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
        """Async context manager exit; disconnects."""
        await self.disconnect()
