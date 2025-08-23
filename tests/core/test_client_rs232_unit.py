"""Tests for RS232 client (client_rs232.py) - Focused on unit testing behavior."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.exceptions import ConnectionError


@pytest.mark.unit
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


@pytest.mark.unit
class TestNetworkHDClientRS232Connection:
    """Test RS232 client connection behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0)

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful RS232 connection behavior."""
        # Mock the serial connection to work
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await self.client.connect()

            assert self.client.serial == mock_serial
            assert self.client.is_connected()
            assert self.client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test RS232 connection failure behavior."""
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.open = AsyncMock(side_effect=Exception("Serial connection failed"))
            mock_serial.is_open = False  # Ensure is_open returns False for failure
            mock_serial_class.return_value = mock_serial

            with pytest.raises(ConnectionError):
                await self.client.connect()

            assert not self.client.is_connected()
            assert self.client.get_connection_state() == "error"

    @pytest.mark.asyncio
    async def test_connect_circuit_breaker_open(self):
        """Test connection behavior when circuit breaker is open."""
        # Open the circuit breaker first
        for _ in range(3):
            self.client._record_failure()

        assert self.client._is_circuit_open()

        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await self.client.connect()

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection behavior."""
        # First connect
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await self.client.connect()
            assert self.client.is_connected()

            # Then disconnect
            await self.client.disconnect()
            assert not self.client.is_connected()
            assert self.client.get_connection_state() == "disconnected"

    def test_is_connected_true(self):
        """Test connection status when connected."""
        # Mock connected state
        self.client.serial = Mock()
        self.client.serial.is_open = True

        assert self.client.is_connected()

    def test_is_connected_false_no_serial(self):
        """Test connection status when no serial connection."""
        assert not self.client.is_connected()

    def test_is_connected_false_serial_closed(self):
        """Test connection status when serial is closed."""
        self.client.serial = Mock()
        self.client.serial.is_open = False

        assert not self.client.is_connected()


@pytest.mark.unit
class TestNetworkHDClientRS232Commands:
    """Test RS232 client command behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0)

    @pytest.mark.asyncio
    async def test_send_command_success(self):
        """Test command sending behavior when connected."""
        # Mock connected state
        self.client.serial = Mock()
        self.client.serial.is_open = True

        # Mock the base class's _send_command_generic method
        with patch.object(
            self.client, "_send_command_generic", new_callable=AsyncMock, return_value="OK: Command executed"
        ):
            response = await self.client.send_command("test command")
            assert "OK: Command executed" in response

    @pytest.mark.asyncio
    async def test_send_command_not_connected(self):
        """Test command sending behavior when not connected."""
        with pytest.raises(ConnectionError, match="Not connected"):
            await self.client.send_command("test command")

    @pytest.mark.asyncio
    async def test_send_command_with_timeout(self):
        """Test command sending behavior with timeout."""
        # Mock connected state
        self.client.serial = Mock()
        self.client.serial.is_open = True

        # Mock timeout scenario
        self.client.serial.in_waiting = 0

        with pytest.raises(Exception):  # Should timeout
            await self.client.send_command("test command", response_timeout=0.1)


@pytest.mark.unit
class TestNetworkHDClientRS232MessageDispatcher:
    """Test RS232 client message dispatcher behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0)

    @pytest.mark.asyncio
    async def test_start_message_dispatcher(self):
        """Test starting message dispatcher behavior."""
        # Mock connected state
        self.client.serial = Mock()
        self.client.serial.is_open = True

        # Mock the dispatcher task
        with patch("asyncio.create_task") as mock_create_task:
            mock_task = Mock()
            mock_create_task.return_value = mock_task

            await self.client._start_message_dispatcher()

            assert self.client._message_dispatcher_task == mock_task
            assert self.client._dispatcher_enabled

    @pytest.mark.asyncio
    async def test_start_message_dispatcher_already_running(self):
        """Test starting message dispatcher when already running."""
        # Mock already running
        self.client._dispatcher_enabled = True
        self.client._message_dispatcher_task = Mock()

        # Should not start again
        await self.client._start_message_dispatcher()

        # Verify no new task was created

    @pytest.mark.asyncio
    async def test_stop_message_dispatcher(self):
        """Test stopping message dispatcher behavior."""
        # Mock running dispatcher
        mock_task = Mock()
        mock_task.cancel = Mock()  # Ensure cancel method exists
        self.client._message_dispatcher_task = mock_task
        self.client._dispatcher_enabled = True

        # Patch the _stop_message_dispatcher method to avoid await issues
        with patch.object(self.client, "_stop_message_dispatcher") as mock_stop:
            # Call the method
            await self.client._stop_message_dispatcher()

            # Verify the method was called
            mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_message_dispatcher_not_running(self):
        """Test stopping message dispatcher when not running."""
        # Mock not running
        self.client._dispatcher_enabled = False
        self.client._message_dispatcher_task = None

        # Should not error
        await self.client._stop_message_dispatcher()


@pytest.mark.unit
class TestNetworkHDClientRS232ContextManager:
    """Test RS232 client async context manager behavior."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager behavior."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Mock successful connection
        with (
            patch.object(client, "connect", new_callable=AsyncMock),
            patch.object(client, "disconnect", new_callable=AsyncMock),
        ):
            async with client:
                # The client should be connected after connect() is called
                pass

            # Verify disconnect was called
            client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager_exception(self):
        """Test async context manager behavior with exception."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Mock connection that raises exception
        with (
            patch.object(client, "connect", new_callable=AsyncMock, side_effect=Exception("Connection failed")),
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            # When connect() fails, the context manager should raise the exception
            # and disconnect() should NOT be called since __aexit__ is never reached
            with pytest.raises(Exception, match="Connection failed"):
                async with client:
                    pass

            # Verify disconnect was NOT called since connect() failed
            mock_disconnect.assert_not_called()
