"""Cross-client integration tests - Testing interactions between different client types."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.exceptions import ConnectionError


@pytest.mark.integration
class TestCrossClientIntegration:
    """Integration tests focusing on cross-client behavior patterns."""

    @pytest.mark.asyncio
    async def test_client_factory_pattern(self):
        """Test that different client types can be created and used consistently."""
        # Test SSH client creation
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Test RS232 client creation
        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Both should have similar base behavior
        assert not ssh_client.is_connected()
        assert not rs232_client.is_connected()
        assert ssh_client.get_connection_state() == "disconnected"
        assert rs232_client.get_connection_state() == "disconnected"

        # Both should support metrics
        ssh_metrics = ssh_client.get_connection_metrics()
        rs232_metrics = rs232_client.get_connection_metrics()

        assert "commands_sent" in ssh_metrics
        assert "commands_sent" in rs232_metrics
        assert "notifications_received" in ssh_metrics
        assert "notifications_received" in rs232_metrics

    @pytest.mark.asyncio
    async def test_circuit_breaker_consistency(self):
        """Test that circuit breaker behavior is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test circuit breaker opens after failures for both
        for client in [ssh_client, rs232_client]:
            # Open circuit breaker
            for _ in range(3):
                client._record_failure()

            assert client._is_circuit_open()

            # Connection attempts should be blocked
            with pytest.raises(ConnectionError, match="Circuit breaker is open"):
                await client.connect()

    @pytest.mark.asyncio
    async def test_notification_handler_consistency(self):
        """Test that notification handling is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test notification callback registration for both
        for client in [ssh_client, rs232_client]:
            callback_called = False

            def test_callback(_notification):
                nonlocal callback_called
                callback_called = True

            client.register_notification_callback("endpoint", test_callback)

            # Verify callback was registered
            assert "endpoint" in client.notification_handler._callbacks
            assert test_callback in client.notification_handler._callbacks["endpoint"]

    @pytest.mark.asyncio
    async def test_context_manager_consistency(self):
        """Test that context manager behavior is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test context manager for both
        for client in [ssh_client, rs232_client]:
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
    async def test_metrics_tracking_consistency(self):
        """Test that metrics tracking is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test metrics tracking for both
        for client in [ssh_client, rs232_client]:
            # Initial metrics
            metrics = client.get_connection_metrics()
            assert metrics["commands_sent"] == 0
            assert metrics["commands_failed"] == 0
            assert metrics["notifications_received"] == 0
            assert metrics["last_command_time"] is None

            # Update metrics
            client._record_command_sent()
            client._record_notification_received()
            client._record_command_failed()

            # Verify metrics were updated
            metrics = client.get_connection_metrics()
            assert metrics["commands_sent"] == 1
            assert metrics["notifications_received"] == 1
            assert metrics["commands_failed"] == 1
            assert metrics["last_command_time"] is not None

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test that error handling is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test error handling for both
        for client in [ssh_client, rs232_client]:
            # Test connection failure
            with patch.object(client, "connect", new_callable=AsyncMock) as mock_connect:
                # Create a closure that captures the current client
                def create_mock_connect_impl(current_client):
                    async def mock_connect_impl():
                        current_client._set_connection_state("error", "Test error")
                        raise ConnectionError("Test error")

                    return mock_connect_impl

                mock_connect.side_effect = create_mock_connect_impl(client)

                with pytest.raises(ConnectionError):
                    await client.connect()

                assert not client.is_connected()
                assert client.get_connection_state() == "error"
                assert client.get_connection_error() is not None

    @pytest.mark.asyncio
    async def test_reconnection_consistency(self):
        """Test that reconnection behavior is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test reconnection for both
        for client in [ssh_client, rs232_client]:
            if isinstance(client, NetworkHDClientSSH):
                # For SSH client, mock paramiko instead of connect method
                with patch("paramiko.SSHClient") as mock_ssh_class:
                    mock_ssh = Mock()
                    mock_shell = Mock()
                    mock_transport = Mock()

                    # Set up all the required mock properties for is_connected() to work
                    mock_shell.closed = False
                    mock_transport.is_active.return_value = True
                    mock_ssh.get_transport.return_value = mock_transport
                    mock_ssh.invoke_shell.return_value = mock_shell
                    mock_ssh_class.return_value = mock_ssh

                    # Mock the message dispatcher to avoid async issues
                    with patch.object(client, "_start_message_dispatcher"):
                        await client.reconnect(max_attempts=1, delay=0.1)

                        assert client.is_connected()
                        assert client.get_connection_state() == "connected"
            else:
                # For RS232 client, mock async_pyserial instead of connect method
                with patch("async_pyserial.SerialPort") as mock_serial_class:
                    mock_serial = Mock()
                    mock_serial.is_open = True
                    mock_serial.open = AsyncMock()
                    mock_serial.close = AsyncMock()
                    mock_serial_class.return_value = mock_serial

                    # Mock the message dispatcher to avoid async issues
                    with patch.object(client, "_start_message_dispatcher"):
                        await client.reconnect(max_attempts=1, delay=0.1)

                        assert client.is_connected()
                        assert client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_connection_state_consistency(self):
        """Test that connection state management is consistent across client types."""
        ssh_client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        rs232_client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test state transitions for both
        for client in [ssh_client, rs232_client]:
            # Initial state
            assert client.get_connection_state() == "disconnected"

            # Test state transitions
            client._set_connection_state("connecting")
            assert client.get_connection_state() == "connecting"

            client._set_connection_state("connected")
            assert client.get_connection_state() == "connected"

            client._set_connection_state("disconnected")
            assert client.get_connection_state() == "disconnected"

            client._set_connection_state("error", "Test error")
            assert client.get_connection_state() == "error"
            assert client.get_connection_error() == "Test error"
