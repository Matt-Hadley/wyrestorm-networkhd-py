"""Final tests to achieve 100% coverage for the core module."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core._client import (
    _BaseNetworkHDClient,
    _ConnectionState,
)
from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH


class ConcreteTestClient(_BaseNetworkHDClient):
    """Concrete implementation for testing the abstract base class."""

    def __init__(self, circuit_breaker_timeout=30.0, heartbeat_interval=30.0):
        super().__init__(
            circuit_breaker_timeout=circuit_breaker_timeout,
            heartbeat_interval=heartbeat_interval
        )
        self._connected = False

    async def connect(self):
        """Mock connect implementation."""
        self._connected = True

    async def disconnect(self):
        """Mock disconnect implementation."""
        self._connected = False

    def is_connected(self) -> bool:
        """Mock is_connected implementation."""
        return self._connected

    async def send_command(self, command: str, response_timeout: float = 10.0) -> str:
        """Mock send_command implementation."""
        return f"Response to: {command}"


class TestBaseNetworkHDClientFinalCoverage:
    """Final tests for _BaseNetworkHDClient to achieve 100% coverage."""

    @pytest.mark.asyncio
    async def test_send_command_generic_timeout_break(self):
        """Test _send_command_generic timeout break in line 346."""
        client = ConcreteTestClient()
        client._connected = True
        
        # Mock the send function
        send_func = Mock()
        receive_func = Mock(return_value=None)
        
        # Create a response queue that never gets data
        with patch.object(client, '_command_lock', asyncio.Lock()):
            client._command_id_counter = 1
            
            # Call the method with very short timeout
            with patch.object(client, '_record_command_sent'):
                response = await client._send_command_generic(
                    "test command", send_func, receive_func, response_timeout=0.1
                )
            
            # Should return empty string when no response
            assert response == ""
            send_func.assert_called_once_with("test command")


class TestNetworkHDClientRS232FinalCoverage:
    """Final tests for NetworkHDClientRS232 to achieve 100% coverage."""

    def test_is_connected_updates_state_disconnected_line_159(self):
        """Test line 159 - updating state when serial is closed."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        
        # Mock serial as closed
        mock_serial = Mock()
        mock_serial.is_open = False
        client.serial = mock_serial
        
        # Check connection - this should update state
        result = client.is_connected()
        
        assert result is False
        assert client._connection_state == _ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_send_command_receive_func_line_189(self):
        """Test line 189 - the receive_func that returns None."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        mock_serial = AsyncMock()
        mock_serial.is_open = True
        client.serial = mock_serial
        
        # Mock the generic send command to capture the receive_func
        receive_func_captured = None
        
        async def capture_receive_func(cmd, send_func, receive_func, timeout):
            nonlocal receive_func_captured
            receive_func_captured = receive_func
            return "OK"
        
        with patch.object(client, '_send_command_generic', side_effect=capture_receive_func):
            await client.send_command("test")
            
            # Test the captured receive_func
            assert receive_func_captured() is None


class TestNetworkHDClientSSHFinalCoverage:
    """Final tests for NetworkHDClientSSH to achieve 100% coverage."""

    def test_is_connected_updates_state_disconnected_line_205(self):
        """Test line 205 - updating state when transport is inactive."""
        client = NetworkHDClientSSH(
            host="192.168.1.1", 
            port=22, 
            username="admin", 
            password="admin", 
            ssh_host_key_policy="auto_add"
        )
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        
        # Mock SSH client with inactive transport
        mock_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = False
        mock_client.get_transport.return_value = mock_transport
        client.client = mock_client
        client.shell = Mock()
        
        # Check connection - this should update state
        result = client.is_connected()
        
        assert result is False
        assert client._connection_state == _ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_send_command_lines_228_229_233(self):
        """Test lines 228-229 and 233 - send_func and receive_func."""
        client = NetworkHDClientSSH(
            host="192.168.1.1",
            port=22,
            username="admin",
            password="admin",
            ssh_host_key_policy="auto_add"
        )
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        mock_shell = Mock()
        client.shell = mock_shell
        
        # Mock client and transport
        mock_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = True
        mock_client.get_transport.return_value = mock_transport
        client.client = mock_client
        
        # Capture the functions passed to _send_command_generic
        send_func_captured = None
        receive_func_captured = None
        
        async def capture_funcs(cmd, send_func, receive_func, timeout):
            nonlocal send_func_captured, receive_func_captured
            send_func_captured = send_func
            receive_func_captured = receive_func
            # Test the functions
            with patch.object(client, 'logger') as mock_logger:
                send_func("test_cmd")
                mock_logger.debug.assert_called_with("Sending command via SSH: test_cmd")
            return "OK"
        
        with patch.object(client, '_send_command_generic', side_effect=capture_funcs):
            await client.send_command("test")
            
            # Verify shell.send was called
            mock_shell.send.assert_called_once_with("test_cmd\n")
            
            # Test the receive_func
            assert receive_func_captured() is None

    @pytest.mark.asyncio
    async def test_message_dispatcher_empty_line_skip_312(self):
        """Test line 312 - continue when line is empty."""
        client = NetworkHDClientSSH(
            host="192.168.1.1",
            port=22,
            username="admin",
            password="admin",
            ssh_host_key_policy="auto_add"
        )
        
        # Set up mock shell with empty lines
        mock_shell = Mock()
        # Simulate receiving data with empty lines
        mock_shell.recv.side_effect = [
            b"\n",  # Just newline - empty line
            b"data\n",  # Actual data
            b"",  # End of stream
        ]
        client.shell = mock_shell
        
        # Track what lines are processed
        processed_lines = []
        
        async def track_lines(line):
            processed_lines.append(line)
        
        client._handle_command_response = track_lines
        
        # Run the dispatcher briefly
        client._dispatcher_task = asyncio.create_task(client._message_dispatcher())
        await asyncio.sleep(0.1)
        client._dispatcher_task.cancel()
        
        try:
            await client._dispatcher_task
        except asyncio.CancelledError:
            pass
        
        # Only non-empty line should be processed
        assert processed_lines == ["data"]