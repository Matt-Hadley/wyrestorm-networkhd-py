"""Tests for RS232 client (client_rs232.py)."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.exceptions import ConnectionError


class TestNetworkHDClientRS232Init:
    """Test NetworkHDClientRS232 initialization."""

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        assert client.port == "/dev/ttyUSB0"
        assert client.baudrate == 9600
        assert client.timeout == 10.0  # default
        assert client.serial_kwargs == {}
        assert client.message_dispatcher_interval == 0.05  # default
        assert client.serial is None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        client = NetworkHDClientRS232(
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=15.0,
            circuit_breaker_timeout=60.0,
            heartbeat_interval=45.0,
            message_dispatcher_interval=0.02,
            parity="even",
            stopbits=2,
        )

        assert client.port == "/dev/ttyUSB0"
        assert client.baudrate == 115200
        assert client.timeout == 15.0
        assert client._circuit_breaker_timeout == 60.0
        assert client._heartbeat_interval == 45.0
        assert client.message_dispatcher_interval == 0.02
        assert client.serial_kwargs == {"parity": "even", "stopbits": 2}

    def test_init_empty_port(self):
        """Test initialization with empty port."""
        with pytest.raises(ValueError, match="Port is required"):
            NetworkHDClientRS232(port="", baudrate=9600)

    def test_init_invalid_baudrate_type(self):
        """Test initialization with non-integer baudrate."""
        with pytest.raises(ValueError, match="Baudrate must be a positive integer"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate="9600")

    def test_init_invalid_baudrate_negative(self):
        """Test initialization with negative baudrate."""
        with pytest.raises(ValueError, match="Baudrate must be a positive integer"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=-9600)

    def test_init_invalid_baudrate_zero(self):
        """Test initialization with zero baudrate."""
        with pytest.raises(ValueError, match="Baudrate must be a positive integer"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=0)

    def test_init_invalid_timeout(self):
        """Test initialization with invalid timeout."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=-1)

    def test_init_invalid_message_dispatcher_interval(self):
        """Test initialization with invalid message dispatcher interval."""
        with pytest.raises(ValueError, match="Message dispatcher interval must be positive"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, message_dispatcher_interval=0)


class TestNetworkHDClientRS232Connection:
    """Test RS232 client connection methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0)

    @pytest.mark.asyncio
    @patch("async_pyserial.AsyncSerial")
    async def test_connect_success(self, mock_async_serial_class):
        """Test successful RS232 connection."""
        # Set up mock
        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.open = AsyncMock()
        mock_async_serial_class.return_value = mock_serial

        # Mock the message dispatcher start
        with patch.object(self.client, "_start_message_dispatcher", new_callable=AsyncMock):
            await self.client.connect()

        # Verify connection setup
        assert self.client.serial == mock_serial
        assert self.client.get_connection_state() == "connected"

        # Verify async_pyserial calls
        mock_async_serial_class.assert_called_once_with(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0)
        mock_serial.open.assert_called_once()

    @pytest.mark.asyncio
    @patch("async_pyserial.AsyncSerial")
    async def test_connect_with_serial_kwargs(self, mock_async_serial_class):
        """Test RS232 connection with additional serial kwargs."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, parity="even", stopbits=2)

        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.open = AsyncMock()
        mock_async_serial_class.return_value = mock_serial

        with patch.object(client, "_start_message_dispatcher", new_callable=AsyncMock):
            await client.connect()

        mock_async_serial_class.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=9600,
            timeout=10.0,  # default timeout
            parity="even",
            stopbits=2,
        )

    @pytest.mark.asyncio
    @patch("async_pyserial.AsyncSerial")
    async def test_connect_serial_exception(self, mock_async_serial_class):
        """Test RS232 connection with serial exception."""
        mock_async_serial_class.side_effect = Exception("Serial port error")

        with pytest.raises(ConnectionError, match="Connection failed"):
            await self.client.connect()

        assert self.client.get_connection_state() == "error"

    @pytest.mark.asyncio
    async def test_connect_circuit_breaker_open(self):
        """Test connection when circuit breaker is open."""
        # Force circuit breaker to open
        for _ in range(3):
            self.client._record_failure()

        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await self.client.connect()

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection."""
        # Set up connected state
        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.close = AsyncMock()
        self.client.serial = mock_serial

        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock):
            await self.client.disconnect()

        assert self.client.serial is None
        assert self.client.get_connection_state() == "disconnected"
        mock_serial.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_serial(self):
        """Test disconnection when no serial connection."""
        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock):
            # Should not raise exception
            await self.client.disconnect()

        assert self.client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    async def test_disconnect_serial_not_open(self):
        """Test disconnection when serial is not open."""
        mock_serial = Mock()
        mock_serial.is_open = False
        self.client.serial = mock_serial

        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock):
            await self.client.disconnect()

        assert self.client.serial is None
        mock_serial.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_disconnect_with_exception(self):
        """Test disconnection with exception."""
        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.close.side_effect = Exception("Close failed")
        self.client.serial = mock_serial

        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await self.client.disconnect()

    def test_is_connected_true(self):
        """Test is_connected returns True when connected."""
        mock_serial = Mock()
        mock_serial.is_open = True

        self.client.serial = mock_serial
        self.client._set_connection_state("connected")

        assert self.client.is_connected()

    def test_is_connected_false_no_serial(self):
        """Test is_connected returns False when no serial."""
        assert not self.client.is_connected()

    def test_is_connected_false_serial_not_open(self):
        """Test is_connected returns False when serial not open."""
        mock_serial = Mock()
        mock_serial.is_open = False

        self.client.serial = mock_serial

        assert not self.client.is_connected()

    def test_is_connected_updates_state_when_disconnected(self):
        """Test is_connected updates state when actually disconnected."""
        self.client._set_connection_state("connected")
        self.client.serial = None  # Not actually connected

        result = self.client.is_connected()

        assert not result
        assert self.client.get_connection_state() == "disconnected"


class TestNetworkHDClientRS232Commands:
    """Test RS232 client command sending."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Set up connected state
        self.mock_serial = Mock()
        self.mock_serial.is_open = True
        self.client.serial = self.mock_serial

    @pytest.mark.asyncio
    async def test_send_command_success(self):
        """Test successful command sending."""
        command = "test command"
        expected_response = "test response"

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_send_command_generic", new_callable=AsyncMock, return_value=expected_response),
        ):
            result = await self.client.send_command(command)

            assert result == expected_response

    @pytest.mark.asyncio
    async def test_send_command_not_connected(self):
        """Test command sending when not connected."""
        with patch.object(self.client, "is_connected", return_value=False):
            with pytest.raises(ConnectionError, match="Not connected"):
                await self.client.send_command("test command")

    @pytest.mark.asyncio
    async def test_send_command_with_timeout(self):
        """Test command sending with custom timeout."""
        command = "test command"
        timeout = 15.0

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_send_command_generic", new_callable=AsyncMock) as mock_send,
        ):
            await self.client.send_command(command, timeout)

            mock_send.assert_called_once()
            # Check that timeout was passed through
            args = mock_send.call_args[0]
            assert args[3] == timeout  # response_timeout parameter

    @pytest.mark.asyncio
    async def test_send_command_strips_whitespace(self):
        """Test command sending strips whitespace from command."""
        command = "  test command  "

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_send_command_generic", new_callable=AsyncMock) as mock_send,
        ):
            await self.client.send_command(command)

            # Check that command was stripped
            args = mock_send.call_args[0]
            assert args[0] == "test command"


class TestNetworkHDClientRS232MessageDispatcher:
    """Test RS232 client message dispatcher."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(
            port="/dev/ttyUSB0",
            baudrate=9600,
            message_dispatcher_interval=0.01,  # Fast for testing
        )

    @pytest.mark.asyncio
    async def test_start_message_dispatcher(self):
        """Test starting message dispatcher."""
        assert not self.client._dispatcher_enabled
        assert self.client._message_dispatcher_task is None

        await self.client._start_message_dispatcher()

        assert self.client._dispatcher_enabled
        assert self.client._message_dispatcher_task is not None

        # Clean up
        await self.client._stop_message_dispatcher()

    @pytest.mark.asyncio
    async def test_start_message_dispatcher_already_running(self):
        """Test starting message dispatcher when already running."""
        await self.client._start_message_dispatcher()
        first_task = self.client._message_dispatcher_task

        # Try to start again
        await self.client._start_message_dispatcher()

        # Should be the same task
        assert self.client._message_dispatcher_task == first_task

        # Clean up
        await self.client._stop_message_dispatcher()

    @pytest.mark.asyncio
    async def test_stop_message_dispatcher(self):
        """Test stopping message dispatcher."""
        await self.client._start_message_dispatcher()
        assert self.client._dispatcher_enabled

        await self.client._stop_message_dispatcher()

        assert not self.client._dispatcher_enabled
        assert self.client._message_dispatcher_task is None

    @pytest.mark.asyncio
    async def test_stop_message_dispatcher_not_running(self):
        """Test stopping message dispatcher when not running."""
        # Should not raise exception
        await self.client._stop_message_dispatcher()

    @pytest.mark.asyncio
    async def test_message_dispatcher_no_serial(self):
        """Test message dispatcher with no serial."""
        self.client.serial = None

        # Should return immediately
        await self.client._message_dispatcher()

    @pytest.mark.asyncio
    async def test_message_dispatcher_processes_notification(self):
        """Test message dispatcher processes notifications."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(return_value=b"notify endpoint device=1 online=1\n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(
                self.client.notification_handler, "handle_notification", new_callable=AsyncMock
            ) as mock_handle,
        ):
            # Run dispatcher for a short time
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)  # Let it process
            self.client._dispatcher_enabled = False
            await task

            mock_handle.assert_called_once_with("notify endpoint device=1 online=1")

    @pytest.mark.asyncio
    async def test_message_dispatcher_processes_command_response(self):
        """Test message dispatcher processes command responses."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(return_value=b"command response\n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            mock_handle.assert_called_once_with("command response")

    @pytest.mark.asyncio
    async def test_message_dispatcher_handles_partial_lines(self):
        """Test message dispatcher handles partial lines correctly."""
        mock_serial = Mock()
        # First call returns partial line, second completes it
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(side_effect=[b"partial", b" line\n"])

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            mock_handle.assert_called_once_with("partial line")

    @pytest.mark.asyncio
    async def test_message_dispatcher_handles_multiple_lines(self):
        """Test message dispatcher handles multiple lines in one read."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(return_value=b"line1\nline2\nline3\n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            # Should be called for each line
            assert mock_handle.call_count == 3
            mock_handle.assert_any_call("line1")
            mock_handle.assert_any_call("line2")
            mock_handle.assert_any_call("line3")

    @pytest.mark.asyncio
    async def test_message_dispatcher_ignores_empty_lines(self):
        """Test message dispatcher ignores empty lines."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(return_value=b"\n\n\n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            mock_handle.assert_not_called()

    @pytest.mark.asyncio
    async def test_message_dispatcher_handles_carriage_return(self):
        """Test message dispatcher strips carriage returns."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        mock_serial.read = AsyncMock(return_value=b"test line\r\n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            mock_handle.assert_called_once_with("test line")

    @pytest.mark.asyncio
    async def test_message_dispatcher_handles_decode_errors(self):
        """Test message dispatcher handles decode errors gracefully."""
        mock_serial = Mock()
        mock_serial.in_waiting = 1
        # Invalid UTF-8 bytes
        mock_serial.read = AsyncMock(return_value=b"\xff\xfe invalid \n")

        self.client.serial = mock_serial
        self.client._dispatcher_enabled = True

        with (
            patch.object(self.client, "is_connected", return_value=True),
            patch.object(self.client, "_handle_command_response", new_callable=AsyncMock) as mock_handle,
        ):
            task = asyncio.create_task(self.client._message_dispatcher())
            await asyncio.sleep(0.05)
            self.client._dispatcher_enabled = False
            await task

            # Should still process the line (with replacement chars)
            mock_handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_command_response_no_pending_commands(self):
        """Test handling command response with no pending commands."""
        response_line = "test response"

        # Should not raise exception
        await self.client._handle_command_response(response_line)

    @pytest.mark.asyncio
    async def test_handle_command_response_with_pending_command(self):
        """Test handling command response with pending command."""
        response_line = "test response"

        # Set up pending command
        queue = asyncio.Queue()
        self.client._pending_commands = {"cmd_1": queue}

        await self.client._handle_command_response(response_line)

        # Check response was queued
        assert not queue.empty()
        result = queue.get_nowait()
        assert result == response_line

    @pytest.mark.asyncio
    async def test_handle_command_response_queue_full(self):
        """Test handling command response with full queue."""
        response_line = "test response"

        # Set up full queue
        queue = asyncio.Queue(maxsize=1)
        queue.put_nowait("existing")
        self.client._pending_commands = {"cmd_1": queue}

        # Should not raise exception
        await self.client._handle_command_response(response_line)


class TestNetworkHDClientRS232ContextManager:
    """Test RS232 client as context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using RS232 client as async context manager."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        with (
            patch.object(client, "connect", new_callable=AsyncMock) as mock_connect,
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            async with client as c:
                assert c is client
                mock_connect.assert_called_once()
                mock_disconnect.assert_not_called()

            mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager_exception(self):
        """Test context manager cleanup on exception."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        with (
            patch.object(client, "connect", new_callable=AsyncMock),
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            with pytest.raises(ValueError):
                async with client:
                    raise ValueError("Test error")

            mock_disconnect.assert_called_once()


class TestNetworkHDClientRS232Integration:
    """Integration tests for RS232 client."""

    @pytest.mark.asyncio
    @patch("async_pyserial.AsyncSerial")
    async def test_full_connection_lifecycle(self, mock_async_serial_class):
        """Test complete connection lifecycle."""
        # Set up mock
        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.open = AsyncMock()
        mock_serial.close = AsyncMock()
        mock_serial.in_waiting = 0
        mock_async_serial_class.return_value = mock_serial

        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test connection
        await client.connect()
        assert client.is_connected()
        assert client.get_connection_state() == "connected"

        # Test disconnection
        await client.disconnect()
        assert not client.is_connected()
        assert client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    @patch("async_pyserial.AsyncSerial")
    async def test_send_command_integration(self, mock_async_serial_class):
        """Test command sending integration."""
        mock_serial = Mock()
        mock_serial.is_open = True
        mock_serial.open = AsyncMock()
        mock_serial.write = AsyncMock()
        mock_serial.in_waiting = 0
        mock_async_serial_class.return_value = mock_serial

        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        await client.connect()

        # Mock the command response queue
        with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value="OK"):
            result = await client.send_command("test command")
            assert result == "OK"
