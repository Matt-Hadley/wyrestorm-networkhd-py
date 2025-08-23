"""Shared base test classes for common client behavior."""

from unittest.mock import AsyncMock, patch

import pytest

from wyrestorm_networkhd.core._client import _BaseNetworkHDClient, _ConnectionState
from wyrestorm_networkhd.exceptions import ConnectionError


class ConcreteTestClient(_BaseNetworkHDClient):
    """Concrete implementation of abstract base class for testing."""

    def __init__(self, **kwargs):
        kwargs.setdefault("circuit_breaker_timeout", 30.0)
        kwargs.setdefault("heartbeat_interval", 30.0)
        super().__init__(**kwargs)
        self._connected = False

    async def connect(self):
        self._connected = True
        self._connection_state = _ConnectionState.CONNECTED
        return True

    async def disconnect(self):
        self._connected = False
        self._connection_state = _ConnectionState.DISCONNECTED
        return True

    def is_connected(self):
        return self._connected

    async def _send_command_generic(self, _command, _timeout=None):
        return "OK: Mock response"

    async def send_command(self, command: str, _response_timeout: float | None = None) -> str:
        if not self.is_connected():
            raise ConnectionError("Not connected")
        return f"response to {command}"


class BaseClientTestMixin:
    """Base test mixin for common client behavior tests."""

    def test_init_default_params(self, client):
        """Test initialization with default parameters."""
        assert hasattr(client, "_circuit_breaker_timeout")
        assert hasattr(client, "_heartbeat_interval")
        assert client.get_connection_state() == "disconnected"
        assert client.get_connection_error() is None
        assert client._failure_count == 0
        assert client._circuit_open_time is None

    def test_connection_state_management(self, client):
        """Test connection state transitions."""
        assert client.get_connection_state() == "disconnected"

        client._set_connection_state("connecting")
        assert client.get_connection_state() == "connecting"

        client._set_connection_state("connected")
        assert client.get_connection_state() == "connected"

        client._set_connection_state("error", "Test error")
        assert client.get_connection_state() == "error"
        assert client.get_connection_error() == "Test error"

    def test_circuit_breaker_behavior(self, client):
        """Test circuit breaker functionality."""
        assert not client._is_circuit_open()

        # Open circuit after 3 failures
        for _ in range(3):
            client._record_failure()
        assert client._is_circuit_open()

        # Reset circuit
        client._reset_circuit()
        assert not client._is_circuit_open()
        assert client._failure_count == 0

    def test_metrics_tracking(self, client):
        """Test connection metrics tracking."""
        metrics = client.get_connection_metrics()
        assert "commands_sent" in metrics
        assert "commands_failed" in metrics
        assert "notifications_received" in metrics
        assert "last_command_time" in metrics

        # Update metrics
        client._record_command_sent()
        client._record_notification_received()
        client._record_command_failed()

        metrics = client.get_connection_metrics()
        assert metrics["commands_sent"] == 1
        assert metrics["notifications_received"] == 1
        assert metrics["commands_failed"] == 1


class BaseConnectionTestMixin:
    """Base test mixin for connection behavior tests."""

    @pytest.mark.asyncio
    async def test_context_manager_success(self, client):
        """Test async context manager success path."""
        with (
            patch.object(client, "connect", new_callable=AsyncMock),
            patch.object(client, "disconnect", new_callable=AsyncMock),
        ):
            async with client:
                pass
            client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_not_connected(self, client):
        """Test command sending when not connected."""
        with pytest.raises(ConnectionError, match="Not connected"):
            await client.send_command("test command")

    @pytest.mark.asyncio
    async def test_connect_circuit_breaker_open(self, client):
        """Test connection blocked when circuit breaker is open."""
        for _ in range(3):
            client._record_failure()
        assert client._is_circuit_open()

        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await client.connect()


class BaseCommandTestMixin:
    """Base test mixin for command behavior tests."""

    @pytest.mark.asyncio
    async def test_send_command_success(self, client, mock_connected_state):
        """Test successful command sending."""
        mock_connected_state(client)

        with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value="OK: Command executed"):
            response = await client.send_command("test command")
            assert "OK: Command executed" in response
