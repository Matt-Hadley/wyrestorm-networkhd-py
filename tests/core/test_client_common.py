"""Consolidated tests for common client behavior using parameterized clients."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.exceptions import ConnectionError

from .test_base_client import BaseClientTestMixin, BaseCommandTestMixin, BaseConnectionTestMixin


@pytest.mark.unit
class TestClientInit(BaseClientTestMixin):
    """Test client initialization for both SSH and RS232 clients."""

    def test_init_custom_timeouts(self, client):
        """Test initialization with custom timeout values."""
        # Create new client with custom values based on client type
        if hasattr(client, "host"):  # SSH client
            from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH

            custom_client = NetworkHDClientSSH(
                host="192.168.1.100",
                port=22,
                username="admin",
                password="password",
                ssh_host_key_policy="auto_add",
                timeout=15.0,
                circuit_breaker_timeout=60.0,
                heartbeat_interval=45.0,
            )
            assert custom_client.timeout == 15.0
        else:  # RS232 client
            from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232

            custom_client = NetworkHDClientRS232(
                port="/dev/ttyUSB0",
                baudrate=115200,
                timeout=15.0,
                circuit_breaker_timeout=60.0,
                heartbeat_interval=45.0,
            )
            assert custom_client.timeout == 15.0
            assert custom_client.baudrate == 115200

        assert custom_client._circuit_breaker_timeout == 60.0
        assert custom_client._heartbeat_interval == 45.0


@pytest.mark.unit
class TestClientValidation:
    """Test client parameter validation."""

    def test_ssh_invalid_params(self):
        """Test SSH client parameter validation."""
        from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH

        # Empty host
        with pytest.raises(ValueError, match="Host is required"):
            NetworkHDClientSSH(host="", port=22, username="admin", password="password", ssh_host_key_policy="auto_add")

        # Invalid port range
        with pytest.raises(ValueError, match="Port must be an integer between 1 and 65535"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=0, username="admin", password="password", ssh_host_key_policy="auto_add"
            )

        # Empty credentials
        with pytest.raises(ValueError, match="Username is required"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="", password="password", ssh_host_key_policy="auto_add"
            )

    def test_rs232_invalid_params(self):
        """Test RS232 client parameter validation."""
        from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232

        # Empty port
        with pytest.raises(ValueError, match="Port is required"):
            NetworkHDClientRS232(port="", baudrate=9600)

        # Invalid baudrate
        with pytest.raises(ValueError, match="Baudrate must be a positive integer"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=0)

        # Invalid timeout
        with pytest.raises(ValueError, match="Timeout must be positive"):
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=-1)


@pytest.mark.unit
class TestClientConnection(BaseConnectionTestMixin):
    """Test client connection behavior for both client types."""

    @pytest.mark.asyncio
    async def test_connect_success(self, client):
        """Test successful connection for both client types."""
        if hasattr(client, "host"):  # SSH client
            with patch("paramiko.SSHClient") as mock_ssh_class:
                mock_ssh, mock_shell, mock_transport = Mock(), Mock(), Mock()
                mock_shell.closed = False
                mock_transport.is_active.return_value = True
                mock_ssh.get_transport.return_value = mock_transport
                mock_ssh.invoke_shell.return_value = mock_shell
                mock_ssh_class.return_value = mock_ssh

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()
                    assert client.get_connection_state() == "connected"
        else:  # RS232 client
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()
                mock_serial_class.return_value = mock_serial

                await client.connect()
                assert client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_connect_failure(self, client):
        """Test connection failure for both client types."""
        if hasattr(client, "host"):  # SSH client
            with patch("paramiko.SSHClient") as mock_ssh_class:
                mock_ssh = Mock()
                mock_ssh.connect.side_effect = Exception("Connection failed")
                mock_ssh_class.return_value = mock_ssh

                with pytest.raises(ConnectionError):
                    await client.connect()
        else:  # RS232 client
            with patch("async_pyserial.SerialPort") as mock_serial_class:
                mock_serial = Mock()
                mock_serial.open = AsyncMock(side_effect=Exception("Serial connection failed"))
                mock_serial.is_open = False
                mock_serial_class.return_value = mock_serial

                with pytest.raises(ConnectionError):
                    await client.connect()

        assert not client.is_connected()
        assert client.get_connection_state() == "error"


@pytest.mark.unit
class TestClientCommands(BaseCommandTestMixin):
    """Test client command behavior for both client types."""

    @pytest.mark.asyncio
    async def test_send_command_timeout(self, client, mock_connected_state):
        """Test command timeout behavior."""
        mock_connected_state(client)

        with (
            patch.object(
                client, "_send_command_generic", new_callable=AsyncMock, side_effect=TimeoutError("Command timeout")
            ),
            pytest.raises(TimeoutError),
        ):
            await client.send_command("test command", response_timeout=0.1)


@pytest.mark.unit
class TestClientContextManager:
    """Test async context manager behavior for both client types."""

    @pytest.mark.asyncio
    async def test_context_manager_exception(self, client):
        """Test context manager with connection exception."""
        with (
            patch.object(client, "connect", new_callable=AsyncMock, side_effect=Exception("Connection failed")),
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            with pytest.raises(Exception, match="Connection failed"):
                async with client:
                    pass
            # disconnect should not be called if connect fails
            mock_disconnect.assert_not_called()


@pytest.mark.unit
class TestClientMessageDispatcher:
    """Test message dispatcher behavior for both client types."""

    @pytest.mark.asyncio
    async def test_start_message_dispatcher(self, client, mock_connected_state):
        """Test starting message dispatcher."""
        mock_connected_state(client)

        with patch("asyncio.create_task") as mock_create_task:
            mock_task = Mock()
            mock_create_task.return_value = mock_task

            await client._start_message_dispatcher()

            assert client._message_dispatcher_task == mock_task
            assert client._dispatcher_enabled

    @pytest.mark.asyncio
    async def test_stop_message_dispatcher(self, client):
        """Test stopping message dispatcher."""
        # Create a proper Task-like mock
        import asyncio

        async def dummy_coro():
            pass

        mock_task = asyncio.create_task(dummy_coro())
        mock_task.cancel = Mock(wraps=mock_task.cancel)  # Wrap the real cancel method
        client._message_dispatcher_task = mock_task
        client._dispatcher_enabled = True

        await client._stop_message_dispatcher()

        assert not client._dispatcher_enabled
        assert client._message_dispatcher_task is None
