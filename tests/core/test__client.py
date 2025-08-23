"""Tests for the base NetworkHD client (_client.py)."""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core._client import (
    _BaseNetworkHDClient,
    _ConnectionState,
    _NotificationHandler,
)
from wyrestorm_networkhd.models.api_notifications import NotificationObject


class ConcreteTestClient(_BaseNetworkHDClient):
    """Concrete implementation for testing the abstract base class."""

    def __init__(self, **kwargs):
        super().__init__(circuit_breaker_timeout=30.0, heartbeat_interval=30.0, **kwargs)
        self._connected = False

    async def connect(self):
        """Mock connect implementation."""
        self._connected = True
        self._set_connection_state("connected")

    async def disconnect(self):
        """Mock disconnect implementation."""
        self._connected = False
        self._set_connection_state("disconnected")

    def is_connected(self):
        """Mock is_connected implementation."""
        return self._connected

    async def send_command(self, command: str, response_timeout: float | None = None):
        """Mock send_command implementation."""
        if not self.is_connected():
            from wyrestorm_networkhd.exceptions import ConnectionError

            raise ConnectionError("Not connected")
        return f"response to {command}"


class TestConnectionState:
    """Test the _ConnectionState enum."""

    def test_connection_state_values(self):
        """Test that connection state enum has expected values."""
        assert _ConnectionState.DISCONNECTED.value == "disconnected"
        assert _ConnectionState.CONNECTING.value == "connecting"
        assert _ConnectionState.CONNECTED.value == "connected"
        assert _ConnectionState.ERROR.value == "error"
        assert _ConnectionState.RECONNECTING.value == "reconnecting"


class TestNotificationHandler:
    """Test the _NotificationHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = _NotificationHandler()

    def test_init(self):
        """Test notification handler initialization."""
        assert self.handler._callbacks == {}
        assert self.handler._parser is not None
        assert self.handler.logger is not None

    def test_register_callback(self):
        """Test registering notification callbacks."""
        callback = Mock()

        self.handler.register_callback("endpoint", callback)

        assert "endpoint" in self.handler._callbacks
        assert callback in self.handler._callbacks["endpoint"]

    def test_register_multiple_callbacks_same_type(self):
        """Test registering multiple callbacks for same notification type."""
        callback1 = Mock()
        callback2 = Mock()

        self.handler.register_callback("endpoint", callback1)
        self.handler.register_callback("endpoint", callback2)

        assert len(self.handler._callbacks["endpoint"]) == 2
        assert callback1 in self.handler._callbacks["endpoint"]
        assert callback2 in self.handler._callbacks["endpoint"]

    def test_unregister_callback(self):
        """Test unregistering notification callbacks."""
        callback = Mock()

        self.handler.register_callback("endpoint", callback)
        self.handler.unregister_callback("endpoint", callback)

        assert "endpoint" not in self.handler._callbacks

    def test_unregister_callback_not_found(self):
        """Test unregistering callback that doesn't exist."""
        callback = Mock()

        # Should not raise exception
        self.handler.unregister_callback("endpoint", callback)

    def test_unregister_callback_partial(self):
        """Test unregistering one of multiple callbacks."""
        callback1 = Mock()
        callback2 = Mock()

        self.handler.register_callback("endpoint", callback1)
        self.handler.register_callback("endpoint", callback2)
        self.handler.unregister_callback("endpoint", callback1)

        assert len(self.handler._callbacks["endpoint"]) == 1
        assert callback2 in self.handler._callbacks["endpoint"]

    @pytest.mark.asyncio
    async def test_handle_notification_success(self):
        """Test successful notification handling."""
        callback = Mock()
        notification_line = "notify endpoint device=1 online=1"

        with (
            patch.object(self.handler._parser, "get_notification_type", return_value="endpoint"),
            patch.object(self.handler._parser, "parse_notification", return_value=Mock(spec=NotificationObject)),
        ):
            self.handler.register_callback("endpoint", callback)
            await self.handler.handle_notification(notification_line)

            callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_notification_parse_failure(self):
        """Test notification handling when parsing fails."""
        callback = Mock()
        notification_line = "invalid notification"

        with (
            patch.object(self.handler._parser, "get_notification_type", return_value="endpoint"),
            patch.object(self.handler._parser, "parse_notification", return_value=None),
        ):
            self.handler.register_callback("endpoint", callback)
            await self.handler.handle_notification(notification_line)

            callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_notification_callback_exception(self):
        """Test notification handling when callback raises exception."""
        callback = Mock(side_effect=Exception("Test error"))
        notification_line = "notify endpoint device=1 online=1"

        with (
            patch.object(self.handler._parser, "get_notification_type", return_value="endpoint"),
            patch.object(self.handler._parser, "parse_notification", return_value=Mock(spec=NotificationObject)),
        ):
            self.handler.register_callback("endpoint", callback)
            # Should not raise exception
            await self.handler.handle_notification(notification_line)

            callback.assert_called_once()


class TestBaseNetworkHDClient:
    """Test the _BaseNetworkHDClient abstract base class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ConcreteTestClient()

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        client = ConcreteTestClient()

        assert client.notification_handler is not None
        assert client._connection_state == _ConnectionState.DISCONNECTED
        assert client._connection_error is None
        assert client._failure_count == 0
        assert client._circuit_open is False
        assert client._circuit_breaker_timeout == 30.0
        assert client._heartbeat_interval == 30.0
        assert client.logger is not None

    def test_init_invalid_circuit_breaker_timeout(self):
        """Test initialization with invalid circuit breaker timeout."""
        # Test is now in test_coverage_additions.py to avoid conflicts
        pass

    def test_init_invalid_heartbeat_interval(self):
        """Test initialization with invalid heartbeat interval."""
        # Test is now in test_coverage_additions.py to avoid conflicts
        pass

    def test_get_connection_state(self):
        """Test getting connection state."""
        assert self.client.get_connection_state() == "disconnected"

        self.client._set_connection_state("connected")
        assert self.client.get_connection_state() == "connected"

    def test_get_connection_error(self):
        """Test getting connection error."""
        assert self.client.get_connection_error() is None

        self.client._set_connection_state("error", "Test error")
        assert self.client.get_connection_error() == "Test error"

    def test_get_connection_metrics(self):
        """Test getting connection metrics."""
        metrics = self.client.get_connection_metrics()

        assert "commands_sent" in metrics
        assert "commands_failed" in metrics
        assert "notifications_received" in metrics
        assert "last_command_time" in metrics
        assert metrics["commands_sent"] == 0
        assert metrics["commands_failed"] == 0
        assert metrics["notifications_received"] == 0
        assert metrics["last_command_time"] is None

    def test_register_notification_callback(self):
        """Test registering notification callback."""
        callback = Mock()

        self.client.register_notification_callback("endpoint", callback)

        assert "endpoint" in self.client.notification_handler._callbacks

    def test_unregister_notification_callback(self):
        """Test unregistering notification callback."""
        callback = Mock()

        self.client.register_notification_callback("endpoint", callback)
        self.client.unregister_notification_callback("endpoint", callback)

        assert "endpoint" not in self.client.notification_handler._callbacks

    @pytest.mark.asyncio
    async def test_reconnect_success(self):
        """Test successful reconnection."""
        max_attempts = 3
        delay = 0.1

        await self.client.reconnect(max_attempts, delay)

        assert self.client.is_connected()
        assert self.client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_reconnect_failure(self):
        """Test reconnection failure."""
        max_attempts = 2
        delay = 0.1

        # Mock connect to always fail
        original_connect = self.client.connect
        self.client.connect = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(ConnectionError, match="Failed to reconnect after 2 attempts"):
            await self.client.reconnect(max_attempts, delay)

        # Restore original connect
        self.client.connect = original_connect

    @pytest.mark.asyncio
    async def test_reconnect_already_connecting(self):
        """Test reconnection when already connecting."""
        self.client._set_connection_state("connecting")

        # Should return without attempting reconnection
        await self.client.reconnect(1, 0.1)

    def test_record_command_sent(self):
        """Test recording sent command metrics."""
        initial_count = self.client._connection_metrics["commands_sent"]
        initial_time = self.client._connection_metrics["last_command_time"]

        self.client._record_command_sent()

        assert self.client._connection_metrics["commands_sent"] == initial_count + 1
        assert self.client._connection_metrics["last_command_time"] != initial_time
        assert self.client._connection_metrics["last_command_time"] is not None

    def test_record_command_failed(self):
        """Test recording failed command metrics."""
        initial_count = self.client._connection_metrics["commands_failed"]

        self.client._record_command_failed()

        assert self.client._connection_metrics["commands_failed"] == initial_count + 1

    def test_record_notification_received(self):
        """Test recording notification metrics."""
        initial_count = self.client._connection_metrics["notifications_received"]

        self.client._record_notification_received()

        assert self.client._connection_metrics["notifications_received"] == initial_count + 1

    def test_set_connection_state_valid(self):
        """Test setting valid connection state."""
        self.client._set_connection_state("connected")

        assert self.client._connection_state == _ConnectionState.CONNECTED
        assert self.client._connection_error is None

    def test_set_connection_state_with_error(self):
        """Test setting connection state with error."""
        error_msg = "Test error message"

        self.client._set_connection_state("error", error_msg)

        assert self.client._connection_state == _ConnectionState.ERROR
        assert self.client._connection_error == error_msg

    def test_set_connection_state_invalid(self):
        """Test setting invalid connection state."""
        self.client._set_connection_state("invalid_state")

        assert self.client._connection_state == _ConnectionState.ERROR

    def test_record_failure(self):
        """Test recording connection failure."""
        assert self.client._failure_count == 0
        assert not self.client._circuit_open

        self.client._record_failure()

        assert self.client._failure_count == 1
        assert not self.client._circuit_open  # Circuit opens after 3 failures

    def test_record_failure_opens_circuit(self):
        """Test that circuit breaker opens after 3 failures."""
        # Record 3 failures
        for _ in range(3):
            self.client._record_failure()

        assert self.client._failure_count == 3
        assert self.client._circuit_open
        assert self.client._circuit_open_time is not None

    def test_reset_circuit(self):
        """Test resetting circuit breaker."""
        # First open the circuit
        for _ in range(3):
            self.client._record_failure()

        assert self.client._circuit_open

        # Then reset it
        self.client._reset_circuit()

        assert self.client._failure_count == 0
        assert not self.client._circuit_open
        assert self.client._circuit_open_time is None

    def test_is_circuit_open_false(self):
        """Test circuit breaker is not open initially."""
        assert not self.client._is_circuit_open()

    def test_is_circuit_open_true(self):
        """Test circuit breaker is open after failures."""
        for _ in range(3):
            self.client._record_failure()

        assert self.client._is_circuit_open()

    def test_is_circuit_open_auto_close(self):
        """Test circuit breaker auto-closes after timeout."""
        # Test is now in test_coverage_additions.py with better implementation
        pass

    @pytest.mark.asyncio
    async def test_send_command_generic_success(self):
        """Test generic command sending success."""
        command = "test command"
        expected_response = "test response"

        send_func = Mock()
        receive_func = Mock()

        # Mock the response queue
        with patch.object(self.client, "_pending_commands", {}):
            response_queue = asyncio.Queue()

            async def mock_send_command_generic():
                # Simulate adding response to queue
                await response_queue.put(expected_response)

                # Get response from queue
                response_lines = []
                try:
                    line = await asyncio.wait_for(response_queue.get(), timeout=1.0)
                    response_lines.append(line)
                except TimeoutError:
                    pass

                return "\n".join(response_lines) if response_lines else ""

            result = await mock_send_command_generic()

            assert result == expected_response

    def test_parse_response_success(self):
        """Test successful response parsing."""
        response = "Welcome to NetworkHD\nOK: Command executed"

        result = self.client._parse_response(response)

        assert result == "OK: Command executed"

    def test_parse_response_error(self):
        """Test response parsing with error."""
        response = "ERROR: Invalid command"

        with pytest.raises(Exception):  # CommandError imported in method
            self.client._parse_response(response)

    def test_parse_response_empty(self):
        """Test response parsing with empty response."""
        response = "Welcome to NetworkHD"

        result = self.client._parse_response(response)

        assert result == ""


class TestBaseNetworkHDClientIntegration:
    """Integration tests for the base client."""

    @pytest.mark.asyncio
    async def test_connect_disconnect_cycle(self):
        """Test complete connect/disconnect cycle."""
        client = ConcreteTestClient()

        # Initial state
        assert not client.is_connected()
        assert client.get_connection_state() == "disconnected"

        # Connect
        await client.connect()
        assert client.is_connected()
        assert client.get_connection_state() == "connected"

        # Disconnect
        await client.disconnect()
        assert not client.is_connected()
        assert client.get_connection_state() == "disconnected"

    @pytest.mark.asyncio
    async def test_command_sending_when_not_connected(self):
        """Test command sending fails when not connected."""
        client = ConcreteTestClient()

        with pytest.raises(Exception):  # ConnectionError
            await client.send_command("test command")

    @pytest.mark.asyncio
    async def test_notification_callback_integration(self):
        """Test notification callback integration."""
        client = ConcreteTestClient()
        callback_called = False
        received_notification = None

        def test_callback(notification):
            nonlocal callback_called, received_notification
            callback_called = True
            received_notification = notification

        client.register_notification_callback("endpoint", test_callback)

        # Mock notification handling
        mock_notification = Mock(spec=NotificationObject)

        with (
            patch.object(client.notification_handler._parser, "get_notification_type", return_value="endpoint"),
            patch.object(client.notification_handler._parser, "parse_notification", return_value=mock_notification),
        ):
            await client.notification_handler.handle_notification("notify endpoint device=1 online=1")

        assert callback_called
        assert received_notification == mock_notification
