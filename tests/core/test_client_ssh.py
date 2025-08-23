"""Tests for SSH client (client_ssh.py)."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import paramiko
import pytest

from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.exceptions import AuthenticationError, ConnectionError


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
        assert client.client is None
        assert client.shell is None

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
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="invalid"
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


class TestNetworkHDClientSSHConnection:
    """Test SSH client connection methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            ssh_host_key_policy="auto_add",
            timeout=5.0,
        )

    @pytest.mark.asyncio
    @patch("paramiko.SSHClient")
    async def test_connect_success(self, mock_ssh_client_class):
        """Test successful SSH connection."""
        # Set up mocks
        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_shell = Mock()
        mock_shell.closed = False
        mock_ssh_client.invoke_shell.return_value = mock_shell

        mock_ssh_client_class.return_value = mock_ssh_client

        # Mock the message dispatcher start
        with patch.object(self.client, "_start_message_dispatcher", new_callable=AsyncMock):
            await self.client.connect()

        # Verify connection setup
        assert self.client.client == mock_ssh_client
        assert self.client.shell == mock_shell
        assert self.client.get_connection_state() == "connected"

        # Verify paramiko calls
        mock_ssh_client.set_missing_host_key_policy.assert_called_once()
        mock_ssh_client.connect.assert_called_once_with(
            hostname="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            timeout=5.0,
            look_for_keys=False,
            allow_agent=False,
        )
        mock_ssh_client.invoke_shell.assert_called_once()
        mock_shell.settimeout.assert_called_once_with(5.0)

    @pytest.mark.asyncio
    @patch("paramiko.SSHClient")
    async def test_connect_authentication_failure(self, mock_ssh_client_class):
        """Test SSH connection with authentication failure."""
        mock_ssh_client = Mock()
        mock_ssh_client.connect.side_effect = paramiko.AuthenticationException("Auth failed")
        mock_ssh_client_class.return_value = mock_ssh_client

        with pytest.raises(AuthenticationError):
            await self.client.connect()

        assert self.client.get_connection_state() == "error"
        assert "Authentication failed" in self.client.get_connection_error()

    @pytest.mark.asyncio
    @patch("paramiko.SSHClient")
    async def test_connect_ssh_exception(self, mock_ssh_client_class):
        """Test SSH connection with SSH exception."""
        mock_ssh_client = Mock()
        mock_ssh_client.connect.side_effect = paramiko.SSHException("SSH error")
        mock_ssh_client_class.return_value = mock_ssh_client

        with pytest.raises(ConnectionError, match="SSH error"):
            await self.client.connect()

        assert self.client.get_connection_state() == "error"

    @pytest.mark.asyncio
    @patch("paramiko.SSHClient")
    async def test_connect_general_exception(self, mock_ssh_client_class):
        """Test SSH connection with general exception."""
        mock_ssh_client = Mock()
        mock_ssh_client.connect.side_effect = Exception("General error")
        mock_ssh_client_class.return_value = mock_ssh_client

        with pytest.raises(ConnectionError, match="Connection failed"):
            await self.client.connect()

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
        self.client.client = Mock()
        self.client.shell = Mock()

        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock):
            await self.client.disconnect()

        assert self.client.client is None
        assert self.client.shell is None
        assert self.client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    async def test_disconnect_with_exception(self):
        """Test disconnection with exception."""
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.close.side_effect = RuntimeError("Close failed")

        with patch.object(self.client, "_stop_message_dispatcher", new_callable=AsyncMock), pytest.raises(RuntimeError):
            await self.client.disconnect()

    def test_is_connected_true(self):
        """Test is_connected returns True when connected."""
        mock_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = True
        mock_client.get_transport.return_value = mock_transport

        mock_shell = Mock()
        mock_shell.closed = False

        self.client.client = mock_client
        self.client.shell = mock_shell
        self.client._set_connection_state("connected")

        assert self.client.is_connected()

    def test_is_connected_false_no_client(self):
        """Test is_connected returns False when no client."""
        assert not self.client.is_connected()

    def test_is_connected_false_no_shell(self):
        """Test is_connected returns False when no shell."""
        self.client.client = Mock()
        assert not self.client.is_connected()

    def test_is_connected_false_shell_closed(self):
        """Test is_connected returns False when shell is closed."""
        self.client.client = Mock()
        self.client.shell = Mock()
        self.client.shell.closed = True

        assert not self.client.is_connected()

    def test_is_connected_false_no_transport(self):
        """Test is_connected returns False when no transport."""
        self.client.client = Mock()
        self.client.client.get_transport.return_value = None
        self.client.shell = Mock()
        self.client.shell.closed = False

        assert not self.client.is_connected()

    def test_is_connected_false_transport_inactive(self):
        """Test is_connected returns False when transport inactive."""
        mock_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = False
        mock_client.get_transport.return_value = mock_transport

        self.client.client = mock_client
        self.client.shell = Mock()
        self.client.shell.closed = False

        assert not self.client.is_connected()

    def test_is_connected_updates_state_when_disconnected(self):
        """Test is_connected updates state when actually disconnected."""
        self.client._set_connection_state("connected")
        self.client.client = None  # Not actually connected

        result = self.client.is_connected()

        assert not result
        assert self.client.get_connection_state() == "disconnected"


class TestNetworkHDClientSSHCommands:
    """Test SSH client command sending."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Set up connected state
        self.mock_shell = Mock()
        self.client.shell = self.mock_shell
        self.client._connected = True  # For is_connected check

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
        with (
            patch.object(self.client, "is_connected", return_value=False),
            pytest.raises(ConnectionError, match="Not connected"),
        ):
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


class TestNetworkHDClientSSHHostKeyPolicy:
    """Test SSH client host key policy handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

    def test_get_host_key_policy_auto_add(self):
        """Test getting AutoAddPolicy."""
        self.client.ssh_host_key_policy = "auto_add"
        policy = self.client._get_host_key_policy()
        assert isinstance(policy, paramiko.AutoAddPolicy)

    def test_get_host_key_policy_reject(self):
        """Test getting RejectPolicy."""
        self.client.ssh_host_key_policy = "reject"
        policy = self.client._get_host_key_policy()
        assert isinstance(policy, paramiko.RejectPolicy)

    def test_get_host_key_policy_warn(self):
        """Test getting WarningPolicy."""
        self.client.ssh_host_key_policy = "warn"
        policy = self.client._get_host_key_policy()
        assert isinstance(policy, paramiko.WarningPolicy)


class TestNetworkHDClientSSHMessageDispatcher:
    """Test SSH client message dispatcher."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = NetworkHDClientSSH(
            host="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            ssh_host_key_policy="auto_add",
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
    async def test_message_dispatcher_no_shell(self):
        """Test message dispatcher with no shell."""
        self.client.shell = None

        # Should return immediately
        await self.client._message_dispatcher()

    @pytest.mark.asyncio
    async def test_message_dispatcher_processes_notification(self):
        """Test message dispatcher processes notifications."""
        mock_shell = Mock()
        mock_shell.recv_ready.side_effect = [True, False]  # Data available once
        mock_shell.recv.return_value = b"notify endpoint device=1 online=1\n"

        self.client.shell = mock_shell
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
        mock_shell = Mock()
        mock_shell.recv_ready.side_effect = [True, False]
        mock_shell.recv.return_value = b"command response\n"

        self.client.shell = mock_shell
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


class TestNetworkHDClientSSHContextManager:
    """Test SSH client as context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using SSH client as async context manager."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

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
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        with (
            patch.object(client, "connect", new_callable=AsyncMock),
            patch.object(client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            with pytest.raises(ValueError):
                async with client:
                    raise ValueError("Test error")

            mock_disconnect.assert_called_once()


class TestNetworkHDClientSSHIntegration:
    """Integration tests for SSH client."""

    @pytest.mark.asyncio
    @patch("paramiko.SSHClient")
    async def test_full_connection_lifecycle(self, mock_ssh_client_class):
        """Test complete connection lifecycle."""
        # Set up mocks
        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_shell = Mock()
        mock_shell.closed = False
        mock_shell.recv_ready.return_value = False
        mock_ssh_client.invoke_shell.return_value = mock_shell

        mock_ssh_client_class.return_value = mock_ssh_client

        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Test connection
        await client.connect()
        assert client.is_connected()
        assert client.get_connection_state() == "connected"

        # Test disconnection
        await client.disconnect()
        assert not client.is_connected()
        assert client.get_connection_state() == "disconnected"
