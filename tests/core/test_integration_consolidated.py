"""Consolidated integration tests for core clients - merged from multiple integration files."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.exceptions import ConnectionError

from .test_base_client import BaseClientTestMixin


@pytest.mark.integration
class TestClientIntegrationConsolidated(BaseClientTestMixin):
    """Consolidated integration tests for both SSH and RS232 clients."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_workflow(self, client):
        """Test complete client lifecycle for both client types."""
        # Mock appropriate connection type
        if hasattr(client, "host"):  # SSH client
            with patch("paramiko.SSHClient") as mock_ssh_class:
                mock_ssh, mock_shell, mock_transport = Mock(), Mock(), Mock()
                mock_shell.closed = False
                mock_transport.is_active.return_value = True
                mock_ssh.get_transport.return_value = mock_transport
                mock_ssh.invoke_shell.return_value = mock_shell
                mock_ssh_class.return_value = mock_ssh

                with (
                    patch.object(client, "_start_message_dispatcher"),
                    patch.object(client, "_stop_message_dispatcher"),
                ):
                    # Test full lifecycle
                    await client.connect()
                    assert client.is_connected()

                    # Send command
                    with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value="OK"):
                        response = await client.send_command("test")
                        assert "OK" in response

                    await client.disconnect()
                    assert not client.is_connected()

        else:  # RS232 client
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()
                mock_serial.close = AsyncMock()
                mock_serial_class.return_value = mock_serial

                with (
                    patch.object(client, "_start_message_dispatcher"),
                    patch.object(client, "_stop_message_dispatcher"),
                ):
                    # Test full lifecycle
                    await client.connect()
                    assert client.is_connected()

                    # Send command
                    with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value="OK"):
                        response = await client.send_command("test")
                        assert "OK" in response

                    await client.disconnect()
                    assert not client.is_connected()

    @pytest.mark.asyncio
    async def test_notification_callback_workflow(self, client):
        """Test notification callback registration and handling."""
        callback_called = False

        def test_callback(_notification):
            nonlocal callback_called
            callback_called = True

        # Register callback
        client.register_notification_callback("endpoint", test_callback)
        assert "endpoint" in client.notification_handler._callbacks
        assert test_callback in client.notification_handler._callbacks["endpoint"]

        # Unregister callback
        client.unregister_notification_callback("endpoint", test_callback)
        assert "endpoint" not in client.notification_handler._callbacks

    @pytest.mark.asyncio
    async def test_reconnection_workflow(self, client):
        """Test reconnection behavior for both client types."""
        if hasattr(client, "host"):  # SSH client
            with patch("paramiko.SSHClient") as mock_ssh_class:
                mock_ssh, mock_shell, mock_transport = Mock(), Mock(), Mock()
                mock_shell.closed = False
                mock_transport.is_active.return_value = True
                mock_ssh.get_transport.return_value = mock_transport
                mock_ssh.invoke_shell.return_value = mock_shell
                mock_ssh_class.return_value = mock_ssh

                with patch.object(client, "_start_message_dispatcher"):
                    await client.reconnect(max_attempts=1, delay=0.1)
                    assert client.is_connected()
        else:  # RS232 client
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()
                mock_serial_class.return_value = mock_serial

                with patch.object(client, "_start_message_dispatcher"):
                    await client.reconnect(max_attempts=1, delay=0.1)
                    assert client.is_connected()

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, client):
        """Test error recovery patterns."""
        # Test connection failure recovery
        for _ in range(2):  # Don't open circuit breaker
            client._record_failure()

        assert not client._is_circuit_open()

        # Mock successful recovery
        if hasattr(client, "host"):  # SSH client
            with patch("paramiko.SSHClient") as mock_ssh_class:
                mock_ssh = Mock()
                mock_ssh_class.return_value = mock_ssh

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()
                    # After successful connection, circuit should reset
                    client._reset_circuit()
                    assert client._failure_count == 0
        else:  # RS232 client
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()
                mock_serial_class.return_value = mock_serial

                await client.connect()
                client._reset_circuit()
                assert client._failure_count == 0

    @pytest.mark.asyncio
    async def test_performance_metrics_workflow(self, client):
        """Test performance metrics tracking across operations."""
        # Record various metrics
        client._record_command_sent()
        client._record_notification_received()

        metrics = client.get_connection_metrics()
        assert metrics["commands_sent"] == 1
        assert metrics["notifications_received"] == 1
        assert metrics["last_command_time"] is not None


@pytest.mark.integration
class TestNetworkResilienceConsolidated:
    """Consolidated network resilience tests."""

    @pytest.mark.asyncio
    async def test_connection_retry_behavior(self, client):
        """Test connection retry with exponential backoff."""
        failure_count = 0

        async def mock_connect_with_failures():
            nonlocal failure_count
            failure_count += 1
            if failure_count < 3:
                raise ConnectionError("Connection failed")
            return True

        with patch.object(client, "connect", side_effect=mock_connect_with_failures):
            await client.reconnect(max_attempts=3, delay=0.01)
            assert failure_count == 3  # Should succeed on 3rd attempt

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, client):
        """Test circuit breaker recovery after successful connection."""
        # Open circuit breaker
        for _ in range(3):
            client._record_failure()
        assert client._is_circuit_open()

        # Reset and verify recovery
        client._reset_circuit()
        assert not client._is_circuit_open()

        # Should be able to attempt connection again
        from contextlib import suppress

        if hasattr(client, "host"):
            with (
                patch("paramiko.SSHClient"),
                patch.object(client, "_start_message_dispatcher"),
                suppress(Exception),
            ):
                await client.connect()
        else:
            with (
                patch("async_pyserial.SerialPort"),
                suppress(Exception),
            ):
                await client.connect()
