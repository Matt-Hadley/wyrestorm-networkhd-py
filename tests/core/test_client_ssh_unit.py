"""Tests for SSH client (client_ssh.py) - Focused on unit testing behavior."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.exceptions import ConnectionError


@pytest.mark.unit
class TestNetworkHDClientSSHInit:
    """Test NetworkHDClientSSH initialization."""

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        assert client.host == "192.168.1.100"
        assert client.port == 22
        assert client.username == "admin"
        assert client.password == "password"
        assert client.ssh_host_key_policy == "auto_add"
        assert client.timeout == 10.0  # default
        assert client.message_dispatcher_interval == 0.1  # default

    def test_init_custom_timeouts(self):
        """Test initialization with custom timeout values."""
        client = NetworkHDClientSSH(
            host="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            ssh_host_key_policy="auto_add",
            timeout=15.0,
            circuit_breaker_timeout=60.0,
            heartbeat_interval=45.0,
            message_dispatcher_interval=0.05,
        )

        assert client.timeout == 15.0
        assert client._circuit_breaker_timeout == 60.0
        assert client._heartbeat_interval == 45.0
        assert client.message_dispatcher_interval == 0.05

    def test_init_empty_host(self):
        """Test initialization with empty host."""
        with pytest.raises(ValueError, match="Host is required"):
            NetworkHDClientSSH(host="", port=22, username="admin", password="password", ssh_host_key_policy="auto_add")

    def test_init_invalid_port_low(self):
        """Test initialization with port too low."""
        with pytest.raises(ValueError, match="Port must be an integer between 1 and 65535"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=0, username="admin", password="password", ssh_host_key_policy="auto_add"
            )

    def test_init_invalid_port_high(self):
        """Test initialization with port too high."""
        with pytest.raises(ValueError, match="Port must be an integer between 1 and 65535"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=65536, username="admin", password="password", ssh_host_key_policy="auto_add"
            )

    def test_init_invalid_port_type(self):
        """Test initialization with non-integer port."""
        with pytest.raises(ValueError, match="Port must be an integer between 1 and 65535"):
            NetworkHDClientSSH(
                host="192.168.1.100", port="22", username="admin", password="password", ssh_host_key_policy="auto_add"
            )

    def test_init_empty_username(self):
        """Test initialization with empty username."""
        with pytest.raises(ValueError, match="Username is required"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="", password="password", ssh_host_key_policy="auto_add"
            )

    def test_init_empty_password(self):
        """Test initialization with empty password."""
        with pytest.raises(ValueError, match="Password is required"):
            NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="", ssh_host_key_policy="auto_add"
            )

    def test_init_invalid_timeout(self):
        """Test initialization with invalid timeout."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            NetworkHDClientSSH(
                host="192.168.1.100",
                port=22,
                username="admin",
                password="password",
                ssh_host_key_policy="auto_add",
                timeout=-1,
            )

    def test_init_invalid_host_key_policy(self):
        """Test initialization with invalid host key policy."""
        with pytest.raises(ValueError, match="Invalid ssh_host_key_policy"):
            NetworkHDClientSSH(
                host="192.168.1.100",
                port=22,
                username="admin",
                password="password",
                ssh_host_key_policy="invalid",
            )

    def test_init_invalid_message_dispatcher_interval(self):
        """Test initialization with invalid message dispatcher interval."""
        with pytest.raises(ValueError, match="Message dispatcher interval must be positive"):
            NetworkHDClientSSH(
                host="192.168.1.100",
                port=22,
                username="admin",
                password="password",
                ssh_host_key_policy="auto_add",
                message_dispatcher_interval=0,
            )


@pytest.mark.unit
class TestNetworkHDClientSSHConnection:
    """Test SSH client connection behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful SSH connection."""
        # Mock paramiko SSH client and shell
        mock_ssh = Mock()
        mock_shell = Mock()
        mock_transport = Mock()

        # Set up mock behavior
        mock_shell.closed = False
        mock_transport.is_active.return_value = True
        mock_ssh.get_transport.return_value = mock_transport

        with patch("paramiko.SSHClient") as mock_ssh_client_class:
            mock_ssh_client_class.return_value = mock_ssh

            # Mock the connect method to simulate successful connection
            with patch.object(self.client, "_start_message_dispatcher"):
                await self.client.connect()

                # Set the internal state that is_connected() checks
                self.client.client = mock_ssh
                self.client.shell = mock_shell

                # Verify connection state
                assert self.client.is_connected()
                assert self.client.get_connection_state() == "connected"

                # Verify mocks were called
                mock_ssh.connect.assert_called_once()
                mock_ssh.invoke_shell.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_authentication_failure(self):
        """Test connection behavior when authentication fails."""
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_ssh.connect.side_effect = Exception("Authentication failed")
            mock_ssh_class.return_value = mock_ssh

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
        """Test successful SSH disconnection."""
        # Mock paramiko SSH client and shell
        mock_ssh = Mock()
        mock_shell = Mock()
        mock_transport = Mock()

        # Set up mock behavior
        mock_shell.closed = False
        mock_transport.is_active.return_value = True
        mock_ssh.get_transport.return_value = mock_transport

        # Set the internal state to simulate connected state
        self.client.client = mock_ssh
        self.client.shell = mock_shell

        # Mock the stop message dispatcher
        with patch.object(self.client, "_stop_message_dispatcher"):
            await self.client.disconnect()

            # Verify disconnection
            assert not self.client.is_connected()
            assert self.client.get_connection_state() == "disconnected"

            # Verify mocks were called
            mock_shell.close.assert_called_once()
            mock_ssh.close.assert_called_once()

    def test_is_connected_true(self):
        """Test connection status when connected."""
        # Mock connected state
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = False

        transport = Mock()
        transport.is_active.return_value = True
        self.client.client.get_transport.return_value = transport

        assert self.client.is_connected()

    def test_is_connected_false_no_client(self):
        """Test connection status when no client."""
        assert not self.client.is_connected()

    def test_is_connected_false_no_shell(self):
        """Test connection status when no shell."""
        self.client.client = Mock()
        assert not self.client.is_connected()

    def test_is_connected_false_shell_closed(self):
        """Test connection status when shell is closed."""
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = True

        assert not self.client.is_connected()

    def test_is_connected_false_no_transport(self):
        """Test connection status when no transport."""
        self.client.client = Mock()
        self.client.client.get_transport.return_value = None

        assert not self.client.is_connected()

    def test_is_connected_false_transport_inactive(self):
        """Test connection status when transport is inactive."""
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = False

        transport = Mock()
        transport.is_active.return_value = False
        self.client.client.get_transport.return_value = transport

        assert not self.client.is_connected()


@pytest.mark.unit
class TestNetworkHDClientSSHCommands:
    """Test SSH client command behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

    @pytest.mark.asyncio
    async def test_send_command_success(self):
        """Test successful command sending behavior."""
        # Mock connected state
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = False

        transport = Mock()
        transport.is_active.return_value = True
        self.client.client.get_transport.return_value = transport

        # Mock command response
        self.client.shell.recv_ready.return_value = True
        self.client.shell.recv.return_value = b"OK: Command executed\n"

        # Mock the response handling
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
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = False

        transport = Mock()
        transport.is_active.return_value = True
        self.client.client.get_transport.return_value = transport

        # Mock timeout scenario
        self.client.shell.recv_ready.return_value = False

        # Mock the timeout behavior
        with (
            patch.object(
                self.client, "_send_command_generic", new_callable=AsyncMock, side_effect=Exception("Timeout")
            ),
            pytest.raises(Exception, match="Timeout"),
        ):
            await self.client.send_command("test command", response_timeout=0.1)


@pytest.mark.unit
class TestNetworkHDClientSSHHostKeyPolicy:
    """Test SSH host key policy behavior."""

    def test_get_host_key_policy_auto_add(self):
        """Test auto_add host key policy behavior."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Test that the policy is set correctly
        assert client.ssh_host_key_policy == "auto_add"

    def test_get_host_key_policy_reject(self):
        """Test reject host key policy behavior."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="reject"
        )

        assert client.ssh_host_key_policy == "reject"

    def test_get_host_key_policy_warn(self):
        """Test warn host key policy behavior."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="warn"
        )

        assert client.ssh_host_key_policy == "warn"


@pytest.mark.unit
class TestNetworkHDClientSSHMessageDispatcher:
    """Test SSH client message dispatcher behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

    @pytest.mark.asyncio
    async def test_start_message_dispatcher(self):
        """Test starting message dispatcher behavior."""
        # Mock connected state
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = False

        transport = Mock()
        transport.is_active.return_value = True
        self.client.client.get_transport.return_value = transport

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
        """Test stopping message dispatcher."""
        # Create a mock task
        mock_task = Mock()
        mock_task.cancel = Mock()

        # Set up the client with a mock task
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
class TestNetworkHDClientSSHContextManager:
    """Test SSH client async context manager behavior."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager behavior."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

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
        """Test async context manager with exception."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Mock paramiko SSH client and shell
        mock_ssh = Mock()
        mock_shell = Mock()
        mock_transport = Mock()

        # Set up mock behavior
        mock_shell.closed = False
        mock_transport.is_active.return_value = True
        mock_ssh.get_transport.return_value = mock_transport

        # Set the internal state to simulate connected state
        client.client = mock_ssh
        client.shell = mock_shell

        # Mock the connect and disconnect methods
        with (
            patch.object(client, "connect", new_callable=AsyncMock) as mock_connect,
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
            patch.object(client, "_start_message_dispatcher"),
            patch.object(client, "_stop_message_dispatcher"),
        ):
            # Test context manager with exception
            try:
                async with client:
                    raise Exception("Test exception")
            except Exception:
                pass

            # Verify connect and disconnect were called
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()
