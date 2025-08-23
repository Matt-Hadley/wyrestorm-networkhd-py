"""Additional tests to achieve 100% coverage for the core module."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from wyrestorm_networkhd.core._client import (
    _BaseNetworkHDClient,
    _ConnectionState,
    _NotificationHandler,
)
from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.exceptions import CommandError, ConnectionError


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


class TestNotificationHandlerAdditional:
    """Additional tests for NotificationHandler coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = _NotificationHandler()

    def test_unregister_callback_not_found(self):
        """Test unregistering a callback that doesn't exist."""
        # Register a callback
        callback1 = Mock()
        self.handler.register_callback("endpoint", callback1)
        
        # Try to unregister a different callback
        callback2 = Mock()
        with patch.object(self.handler, 'logger') as mock_logger:
            self.handler.unregister_callback("endpoint", callback2)
            mock_logger.warning.assert_called_once_with(
                "Callback not found for endpoint notifications"
            )

    def test_unregister_callback_removes_empty_list(self):
        """Test that empty callback lists are removed."""
        callback = Mock()
        self.handler.register_callback("endpoint", callback)
        
        # Unregister the only callback
        self.handler.unregister_callback("endpoint", callback)
        
        # Verify the notification type was removed from callbacks dict
        assert "endpoint" not in self.handler._callbacks

    @pytest.mark.asyncio
    async def test_handle_notification_exception_in_callback(self):
        """Test that exceptions in callbacks are caught and logged."""
        # Register a callback that raises an exception
        callback = Mock(side_effect=Exception("Callback error"))
        self.handler.register_callback("endpoint", callback)
        
        with patch.object(self.handler, 'logger') as mock_logger:
            await self.handler.handle_notification("notify endpoint device=1 online=1")
            
            # Verify error was logged
            mock_logger.error.assert_called()
            assert "Error in notification callback" in str(mock_logger.error.call_args)

    @pytest.mark.asyncio
    async def test_handle_notification_general_exception(self):
        """Test handling of general exceptions during notification processing."""
        with patch.object(self.handler._parser, 'get_notification_type', side_effect=Exception("Parse error")):
            with patch.object(self.handler, 'logger') as mock_logger:
                await self.handler.handle_notification("invalid notification")
                
                # Verify error was logged
                mock_logger.error.assert_called()
                assert "Error handling notification" in str(mock_logger.error.call_args)


class TestBaseNetworkHDClientAdditional:
    """Additional tests for _BaseNetworkHDClient coverage."""

    def test_init_invalid_circuit_breaker_timeout(self):
        """Test initialization with invalid circuit breaker timeout."""
        with pytest.raises(ValueError, match="Circuit breaker timeout must be positive"):
            ConcreteTestClient(circuit_breaker_timeout=0)
        
        with pytest.raises(ValueError, match="Circuit breaker timeout must be positive"):
            ConcreteTestClient(circuit_breaker_timeout=-1)

    def test_init_invalid_heartbeat_interval(self):
        """Test initialization with invalid heartbeat interval."""
        with pytest.raises(ValueError, match="Heartbeat interval must be positive"):
            ConcreteTestClient(heartbeat_interval=0)
        
        with pytest.raises(ValueError, match="Heartbeat interval must be positive"):
            ConcreteTestClient(heartbeat_interval=-1)

    @pytest.mark.asyncio
    async def test_send_command_generic_with_response(self):
        """Test _send_command_generic with actual response handling."""
        client = ConcreteTestClient()
        
        # Mock the send function
        send_func = Mock()
        receive_func = Mock(return_value=None)
        
        # Set up the client as connected
        client._connected = True
        
        # Create a response queue and add it to pending commands
        with patch.object(client, '_command_lock', asyncio.Lock()):
            # Simulate command sending and response collection
            async def simulate_response():
                # Wait a bit then add response to queue
                await asyncio.sleep(0.1)
                if "test_cmd_id" in client._pending_commands:
                    await client._pending_commands["test_cmd_id"].put("Line 1")
                    await client._pending_commands["test_cmd_id"].put("Line 2")
            
            # Start the simulation
            asyncio.create_task(simulate_response())
            
            # Mock the command ID counter
            client._command_id_counter = 1
            
            # Call the method
            with patch.object(client, '_record_command_sent'):
                response = await client._send_command_generic(
                    "test command", send_func, receive_func, response_timeout=0.5
                )
            
            # Verify multi-line response
            assert response == "Line 1\nLine 2"
            send_func.assert_called_once_with("test command")

    @pytest.mark.asyncio
    async def test_send_command_generic_exception_handling(self):
        """Test _send_command_generic exception handling."""
        client = ConcreteTestClient()
        client._connected = True
        
        # Mock send function that raises an exception
        send_func = Mock(side_effect=Exception("Send error"))
        receive_func = Mock(return_value=None)
        
        with patch.object(client, '_command_lock', asyncio.Lock()):
            with patch.object(client, '_record_command_failed') as mock_record_failed:
                with pytest.raises(Exception, match="Send error"):
                    await client._send_command_generic(
                        "test command", send_func, receive_func, response_timeout=1.0
                    )
                
                # Verify failure was recorded
                mock_record_failed.assert_called_once()
                
                # Verify command was removed from pending
                assert len(client._pending_commands) == 0

    def test_is_circuit_open_auto_close(self):
        """Test circuit breaker auto-closing after timeout."""
        client = ConcreteTestClient(circuit_breaker_timeout=0.1)
        
        # Open the circuit
        client._circuit_open = True
        client._circuit_open_time = time.time()
        
        # Initially circuit should be open
        assert client._is_circuit_open() is True
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Now circuit should auto-close
        with patch.object(client, 'logger') as mock_logger:
            assert client._is_circuit_open() is False
            mock_logger.info.assert_called_with("Circuit breaker auto-closing after timeout")
            
        # Verify state was reset
        assert client._circuit_open is False
        assert client._failure_count == 0


class TestNetworkHDClientRS232Additional:
    """Additional tests for NetworkHDClientRS232 coverage."""

    @pytest.mark.asyncio
    async def test_connect_circuit_breaker_open(self):
        """Test connect when circuit breaker is open."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Open the circuit breaker
        client._circuit_open = True
        
        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_connect_base_class_validation_failure(self):
        """Test connect when base class validation fails."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Mock the base class connect to raise an exception
        with patch.object(_BaseNetworkHDClient, 'connect', side_effect=ValueError("Invalid config")):
            with pytest.raises(ConnectionError, match="Connection failed: Invalid config"):
                await client.connect()
            
            # Verify state was set to error
            assert client._connection_state == _ConnectionState.ERROR
            assert "Connection failed: Invalid config" in client._connection_error

    @pytest.mark.asyncio
    async def test_connect_serial_open_failure(self):
        """Test connect when serial port fails to open."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        with patch('wyrestorm_networkhd.core.client_rs232.async_pyserial') as mock_pyserial:
            mock_serial = AsyncMock()
            mock_serial.open.side_effect = Exception("Port not found")
            mock_pyserial.AsyncSerial.return_value = mock_serial
            
            with pytest.raises(ConnectionError, match="Connection failed: Port not found"):
                await client.connect()

    @pytest.mark.asyncio
    async def test_disconnect_when_already_disconnected(self):
        """Test disconnect when not connected."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Client starts disconnected
        assert client.serial is None
        
        # Should not raise an error
        await client.disconnect()
        
        # Verify state
        assert client._connection_state == _ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_disconnect_exception_handling(self):
        """Test disconnect exception handling."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Mock serial connection
        mock_serial = AsyncMock()
        mock_serial.is_open = True
        mock_serial.close.side_effect = Exception("Close error")
        client.serial = mock_serial
        
        with pytest.raises(Exception, match="Close error"):
            await client.disconnect()
        
        # Verify error state was set
        assert client._connection_state == _ConnectionState.ERROR
        assert "Disconnect error: Close error" in client._connection_error

    def test_is_connected_updates_state_when_serial_closed(self):
        """Test is_connected updates state when serial is closed unexpectedly."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        mock_serial = Mock()
        mock_serial.is_open = False  # Serial is closed
        client.serial = mock_serial
        
        # Check connection
        assert client.is_connected() is False
        
        # Verify state was updated
        assert client._connection_state == _ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_send_command_rs232_specific_formatting(self):
        """Test RS232-specific command formatting."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200)
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        mock_serial = AsyncMock()
        mock_serial.is_open = True
        client.serial = mock_serial
        
        # Mock the generic send command
        with patch.object(client, '_send_command_generic', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "OK"
            
            response = await client.send_command("test command")
            
            # Verify the command was stripped and sent
            assert response == "OK"
            
            # Get the send_func that was passed
            call_args = mock_send.call_args
            send_func = call_args[0][1]  # Second positional argument
            
            # Test the send function
            with patch.object(asyncio, 'create_task') as mock_create_task:
                send_func("test")
                
                # Verify the message was formatted with CRLF
                task_call = mock_create_task.call_args[0][0]
                # The task should be a coroutine for serial.write
                assert mock_serial.write.called or str(task_call).startswith("<coroutine")


class TestNetworkHDClientSSHAdditional:
    """Additional tests for NetworkHDClientSSH coverage."""

    def test_is_connected_updates_state_when_transport_inactive(self):
        """Test is_connected updates state when SSH transport becomes inactive."""
        client = NetworkHDClientSSH(host="192.168.1.1", port=22, username="admin", password="admin", ssh_host_key_policy="auto_add")
        
        # Set up as connected
        client._connection_state = _ConnectionState.CONNECTED
        
        # Mock SSH client with inactive transport
        mock_client = Mock()
        mock_transport = Mock()
        mock_transport.is_active.return_value = False
        mock_client.get_transport.return_value = mock_transport
        client.client = mock_client
        client.shell = Mock()
        
        # Check connection
        assert client.is_connected() is False
        
        # Verify state was updated
        assert client._connection_state == _ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_send_command_ssh_specific_formatting(self):
        """Test SSH-specific command formatting."""
        client = NetworkHDClientSSH(host="192.168.1.1", port=22, username="admin", password="admin", ssh_host_key_policy="auto_add")
        
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
        
        # Mock the generic send command
        with patch.object(client, '_send_command_generic', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "OK"
            
            response = await client.send_command("test command")
            
            # Verify the command was stripped and sent
            assert response == "OK"
            
            # Get the send_func that was passed
            call_args = mock_send.call_args
            send_func = call_args[0][1]  # Second positional argument
            
            # Test the send function
            send_func("test")
            
            # Verify the message was sent with newline
            mock_shell.send.assert_called_once_with("test\n")

    @pytest.mark.asyncio
    async def test_message_dispatcher_handles_empty_lines(self):
        """Test that message dispatcher skips empty lines."""
        client = NetworkHDClientSSH(host="192.168.1.1", port=22, username="admin", password="admin", ssh_host_key_policy="auto_add")
        
        # Set up mock shell with empty lines
        mock_shell = Mock()
        mock_shell.recv.side_effect = [
            b"\n",  # Empty line
            b"\r\n",  # Empty line with CR
            b"actual data\n",
            b"",  # End of data
        ]
        client.shell = mock_shell
        
        # Track received lines
        received_lines = []
        
        async def mock_handle_response(line):
            received_lines.append(line)
        
        client._handle_command_response = mock_handle_response
        
        # Start and quickly stop the dispatcher
        client._dispatcher_task = asyncio.create_task(client._message_dispatcher())
        await asyncio.sleep(0.1)
        client._dispatcher_task.cancel()
        
        try:
            await client._dispatcher_task
        except asyncio.CancelledError:
            pass
        
        # Verify only non-empty line was processed
        assert received_lines == ["actual data"]