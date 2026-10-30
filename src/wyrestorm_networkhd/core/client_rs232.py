"""RS232 client for NetworkHD devices with simplified architecture."""

import asyncio
from typing import Any

import async_pyserial  # type: ignore[import-untyped]

from ..exceptions import ConnectionError
from ._client import _BaseNetworkHDClient


class NetworkHDClientRS232(_BaseNetworkHDClient):
    """RS232 client for NetworkHD devices.

    Provides a simplified interface for connecting to NetworkHD devices via RS232,
    with automatic message dispatching and notification handling.

    A serial link has no keepalive: a failed write marks the connection as lost (is_connected() returns False and
    the next command raises ConnectionLostError), but a cable that is pulled silently shows up only as commands
    timing out.
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
        circuit_breaker_timeout: float | None = None,
        heartbeat_interval: float | None = None,
        message_dispatcher_interval: float = 0.05,
        **serial_kwargs: Any,
    ):
        """Initialize RS232 client.

        Args:
            port: The serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM1' on Windows).
            baudrate: The baud rate for serial communication.
            timeout: Write timeout in seconds (default: 10.0).
            circuit_breaker_timeout: Deprecated and ignored (emits DeprecationWarning); removed in 4.0.
            heartbeat_interval: Deprecated and ignored (emits DeprecationWarning); removed in 4.0.
            message_dispatcher_interval: Sleep interval in seconds for the message
                dispatcher loop when nothing is readable (default: 0.05).
            **serial_kwargs: Additional ``async_pyserial.SerialPortOptions`` attributes
                (bytesize, stopbits, parity, read_timeout, write_timeout, read_bufsize).

        Raises:
            ValueError: If any parameters are invalid.
        """
        super().__init__(
            message_dispatcher_interval=message_dispatcher_interval,
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
        unknown_options = set(serial_kwargs) - set(vars(async_pyserial.SerialPortOptions()))
        if unknown_options:
            raise ValueError(f"Unknown serial options: {', '.join(sorted(unknown_options))}")

        # Store connection parameters
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_kwargs = serial_kwargs

        # Serial connection objects; _received is filled from async_pyserial's data callback thread via the loop
        self.serial: async_pyserial.SerialPort | None = None
        self._received = bytearray()

    # ============================================================================
    # PROTECTED METHODS - RS232 Implementation
    # ============================================================================

    @property
    def _target(self) -> str:
        return f"{self.port} at {self.baudrate} baud"

    async def _open_transport(self) -> None:
        options = async_pyserial.SerialPortOptions()
        options.baudrate = self.baudrate
        for name, value in self.serial_kwargs.items():
            setattr(options, name, value)

        serial = async_pyserial.SerialPort(self.port, options)
        loop = asyncio.get_running_loop()
        self._received = bytearray()
        received = self._received
        # async_pyserial delivers data on its own thread; hand it to the event loop
        serial.on(async_pyserial.SerialPortEvent.ON_DATA, lambda data: loop.call_soon_threadsafe(received.extend, data))
        self.serial = serial
        await asyncio.to_thread(serial.open)

    async def _close_transport(self) -> None:
        serial, self.serial = self.serial, None
        if serial is not None:
            serial.remove_all_listeners(async_pyserial.SerialPortEvent.ON_DATA)
            if serial.is_open():
                await asyncio.to_thread(serial.close)

    def _transport_alive(self) -> bool:
        return self.serial is not None and bool(self.serial.is_open())

    async def _write(self, command: str) -> None:
        if self.serial is None:
            raise ConnectionError("RS232 serial port not available")
        loop = asyncio.get_running_loop()
        written: asyncio.Future[None] = loop.create_future()

        def settle(error: Exception | None) -> None:
            if written.done():
                return
            if error is not None:
                written.set_exception(error)
            else:
                written.set_result(None)

        # The PDF's command delimiter is CR LF
        self.serial.write((command + "\r\n").encode(), lambda error: loop.call_soon_threadsafe(settle, error))
        try:
            await asyncio.wait_for(written, timeout=self.timeout)
        except Exception as e:
            # The port can stay "open" after the adapter is gone, so a failed write is the only sign of link loss
            self._mark_connection_lost(f"write failed: {e!r}")
            raise

    async def _read_available(self) -> bytes:
        data = bytes(self._received)
        self._received.clear()
        return data
