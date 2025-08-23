"""Integration tests for RS232 client - Testing real behavior patterns."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.exceptions import ConnectionError


@pytest.mark.integration
class TestRS232ClientIntegration:
    """Integration tests focusing on RS232 client behavior patterns."""

    @pytest.mark.asyncio
    async def test_full_connection_lifecycle(self):
        """Test RS232 client behaves correctly through full connection lifecycle."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test initial state
        assert not client.is_connected()
        assert client.get_connection_state() == "disconnected"

        # Mock successful connection
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial_class.return_value = mock_serial

            # Test connection
            await client.connect()
            assert client.is_connected()
            assert client.get_connection_state() == "connected"

            # Test command sending
            mock_serial.in_waiting = 10
            mock_serial.read = AsyncMock(return_value=b"OK: Command executed\n")
            mock_serial.write = AsyncMock()

            response = await client.send_command("test command")
            assert "OK: Command executed" in response

            # Test disconnection
            await client.disconnect()
            assert not client.is_connected()
            assert client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test RS232 client handles errors gracefully in real scenarios."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test connection failure
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.open = AsyncMock(side_effect=Exception("Serial connection failed"))
            mock_serial.is_open = False  # Ensure is_open returns False for failure
            mock_serial_class.return_value = mock_serial

            with pytest.raises(ConnectionError):
                await client.connect()

            assert not client.is_connected()
            assert client.get_connection_state() == "error"

    @pytest.mark.asyncio
    async def test_circuit_breaker_workflow(self):
        """Test RS232 client circuit breaker behavior in real scenarios."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test circuit breaker opens after failures
        for i in range(3):
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.open = AsyncMock(side_effect=Exception(f"Failure {i + 1}"))
                mock_serial_class.return_value = mock_serial

                with pytest.raises(ConnectionError):
                    await client.connect()

        # Circuit should be open now
        assert client._is_circuit_open()

        # Connection attempts should be blocked
        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_context_manager_workflow(self):
        """Test that RS232 client works correctly as async context manager."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

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
    async def test_context_manager_exception_handling(self):
        """Test context manager cleanup on exception."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        with (
            patch.object(client, "connect", new_callable=AsyncMock, side_effect=Exception("Connection failed")),
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            with pytest.raises(Exception, match="Connection failed"):
                async with client:
                    pass

            # Verify disconnect was NOT called since connect() failed
            mock_disconnect.assert_not_called()

    @pytest.mark.asyncio
    async def test_connection_state_transitions(self):
        """Test RS232 client connection state transitions in real scenarios."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test state transitions during connection
        assert client.get_connection_state() == "disconnected"

        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial_class.return_value = mock_serial

            # Should transition to connecting
            await client.connect()
            assert client.get_connection_state() == "connected"

            # Should transition to disconnected
            await client.disconnect()
            assert client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    async def test_command_workflow_with_connection(self):
        """Test command sending workflow with real connection."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Mock connection
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial.in_waiting = 10
            mock_serial.read = AsyncMock(return_value=b"OK: Test command\n")
            mock_serial.write = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await client.connect()

            # Test command workflow
            response = await client.send_command("test command")
            assert "OK: Test command" in response

    @pytest.mark.asyncio
    async def test_message_dispatcher_workflow(self):
        """Test message dispatcher behavior in real scenarios."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Mock connection
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await client.connect()

            # Test message dispatcher start
            with patch("asyncio.create_task") as mock_create_task:
                mock_task = Mock()
                mock_create_task.return_value = mock_task

                await client._start_message_dispatcher()

                # The actual task will be different from our mock, so just check that it's set
                assert client._message_dispatcher_task is not None
                assert client._dispatcher_enabled

            # Test message dispatcher stop
            await client._stop_message_dispatcher()
            assert not client._dispatcher_enabled

    @pytest.mark.asyncio
    async def test_serial_parameters_workflow(self):
        """Test RS232 client handles serial parameters correctly."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200, parity="even", stopbits=2, timeout=15.0)

        # Verify parameters are stored correctly
        assert client.port == "/dev/ttyUSB0"
        assert client.baudrate == 115200
        assert client.timeout == 15.0
        assert client.serial_kwargs == {"parity": "even", "stopbits": 2}

        # Test connection with custom parameters
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial.close = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await client.connect()
            assert client.is_connected()

            await client.disconnect()
            assert not client.is_connected()

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test RS232 client error recovery behavior."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test connection failure then recovery
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            # First attempt fails
            mock_serial = Mock()
            mock_serial.open = AsyncMock(side_effect=Exception("First failure"))
            mock_serial_class.return_value = mock_serial

            with pytest.raises(ConnectionError):
                await client.connect()

            assert client.get_connection_state() == "error"

            # Second attempt succeeds
            mock_serial.open = AsyncMock()
            mock_serial.is_open = True
            mock_serial.close = AsyncMock()

            await client.connect()
            assert client.is_connected()
            assert client.get_connection_state() == "connected"

            await client.disconnect()
            assert not client.is_connected()
